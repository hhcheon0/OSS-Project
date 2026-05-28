import os
import uvicorn
import subprocess
import threading
from fastapi import FastAPI, Depends, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from campus_notice_crawler.utils.db_connection import init_db, SessionLocal, Notice, get_db

# FastAPI 앱 생성
app = FastAPI(
    title="Campus Notice AI Crawler API",
    description="대학 학사공지 수집 모듈의 제어 및 데이터 연동을 위한 REST API",
    version="1.0.0"
)

# CORS 설정 (타 팀원의 프론트엔드/백엔드 연동 지원)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 크롤러 가동 상태 추적용 전역 변수
crawler_status = {
    "is_running": False,
    "last_run": None,
    "last_result": "Never run"
}
crawler_lock = threading.Lock()

@app.on_event("startup")
def startup_event():
    # 애플리케이션 시작 시 DB 스키마 자동 초기화
    init_db()

def run_crawler_subprocess():
    """백그라운드에서 Scrapy 크롤러 프로세스 실행"""
    global crawler_status
    with crawler_lock:
        if crawler_status["is_running"]:
            return
        crawler_status["is_running"] = True

    import time
    start_time = time.strftime('%Y-%m-%d %H:%M:%S')
    crawler_status["last_run"] = start_time
    crawler_status["last_result"] = "Running"

    try:
        # Scrapy 명령어 실행
        result = subprocess.run(
            ["scrapy", "crawl", "daegu_notice"],
            capture_output=True,
            text=True,
            check=True
        )
        crawler_status["last_result"] = "Success"
    except subprocess.CalledProcessError as e:
        crawler_status["last_result"] = f"Failed: Subprocess error (Exit code: {e.returncode})"
    except Exception as e:
        crawler_status["last_result"] = f"Failed: {str(e)}"
    finally:
        with crawler_lock:
            crawler_status["is_running"] = False

@app.post("/crawl", status_code=202)
def trigger_crawl(background_tasks: BackgroundTasks):
    """
    [POST] 크롤러 즉시 가동 트리거
    이미 크롤러가 구동 중인 경우 중복 구동을 방지하며, 비동기로 백그라운드 태스크를 가동합니다.
    """
    global crawler_status
    if crawler_status["is_running"]:
        raise HTTPException(status_code=409, detail="Crawler is already running.")
        
    background_tasks.add_task(run_crawler_subprocess)
    return {"message": "Crawl triggered successfully.", "status": "Pending/Running"}

@app.get("/status")
def get_crawler_status():
    """
    [GET] 크롤러 실행 상태 및 마지막 가동 정보 확인
    """
    return crawler_status

@app.get("/notices")
def list_notices(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 당 항목 수"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    pinned_only: Optional[bool] = Query(None, description="상단 고정 공지만 조회 여부"),
    search: Optional[str] = Query(None, description="제목 내 검색어 키워드"),
    db: Session = Depends(get_db)
):
    """
    [GET] 수집 완료된 공지사항 목록 페이징 조회
    서버 및 UI 개발 팀원이 JSON 규격으로 학사공지를 손쉽게 조회해 갈 수 있습니다.
    """
    query = db.query(Notice)
    
    # 카테고리 필터
    if category and category != "전체":
        query = query.filter(Notice.category == category)

    # 상단 고정 필터
    if pinned_only is not None:
        query = query.filter(Notice.is_pinned == pinned_only)
        
    # 검색 키워드 필터
    if search:
        query = query.filter(Notice.title.contains(search))
        
    # 기본 정렬: 고정 공지 우선 + 작성일 최신순 + ID 역순
    query = query.order_by(Notice.is_pinned.desc(), Notice.created_at.desc(), Notice.notice_id.desc())
    
    total = query.count()
    offset = (page - 1) * size
    notices = query.offset(offset).limit(size).all()
    
    return {
        "total_items": total,
        "page": page,
        "size": size,
        "total_pages": (total + size - 1) // size if total > 0 else 0,
        "items": [n.to_dict() for n in notices]
    }

@app.get("/notices/{notice_id}")
def get_notice_detail(notice_id: str, db: Session = Depends(get_db)):
    """
    [GET] 특정 공지사항 상세 단건 조회
    """
    notice = db.query(Notice).filter(Notice.notice_id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail=f"Notice with ID {notice_id} not found.")
    return notice.to_dict()

from pydantic import BaseModel
class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat_with_notices(request: ChatRequest, db: Session = Depends(get_db)):
    """
    [POST] 공지사항 기반 RAG 챗봇 Q&A
    사용자 질문에 대하여 관련 공지 검색 및 AI 답변 생성
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    from api.rag_service import search_similar_notices, generate_rag_answer
    
    # 1. 유사 공지 Top 3 검색
    similar = search_similar_notices(db, request.query, top_n=3)
    
    # 2. RAG 답변 생성
    result = generate_rag_answer(request.query, similar)
    return result

if __name__ == "__main__":
    # 포트 및 호스트 환경 변수 로드
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"Starting Campus Notice AI Crawler API Server on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
