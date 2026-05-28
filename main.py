import os
import sys
import uvicorn
import subprocess
import threading
from pathlib import Path
from fastapi import FastAPI, Depends, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from campus_notice_crawler.utils.db_connection import init_db, SessionLocal, Notice, get_db, DB_TYPE, DATABASE_URL

PROJECT_ROOT = Path(__file__).resolve().parent
print(PROJECT_ROOT)
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

@app.get("/", response_class=HTMLResponse, tags=["service"])
def root():
    """브라우저 접근용 서비스 홈"""
    return """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Campus Notice AI Crawler API</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; margin: 0; background: #0b1020; color: #e6edf3; }
    .wrap { max-width: 920px; margin: 48px auto; padding: 0 20px; }
    .card { background: #121a2b; border: 1px solid #24324a; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
    h1 { margin: 0 0 12px; font-size: 28px; }
    p { margin: 8px 0; line-height: 1.5; color: #c8d1dc; }
    ul { margin: 8px 0; padding-left: 20px; }
    li { margin: 6px 0; }
    a { color: #7cc8ff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .pill { display: inline-block; padding: 4px 10px; border-radius: 999px; background: #1d2b45; border: 1px solid #34517e; font-size: 12px; }
    code { background: #0d1526; border: 1px solid #2a3852; padding: 2px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <span class="pill">RUNNING</span>
      <h1>Campus Notice AI Crawler API</h1>
      <p>백엔드 서버가 정상 실행 중입니다. 아래 링크에서 API 문서와 상태를 바로 확인할 수 있습니다.</p>
    </div>

    <div class="card">
      <h2>Quick Links</h2>
      <ul>
        <li><a href="/docs" target="_blank" rel="noreferrer">/docs</a> - Swagger API 문서/테스트 UI</li>
        <li><a href="/status" target="_blank" rel="noreferrer">/status</a> - 크롤러 실행 상태</li>
        <li><a href="/notices" target="_blank" rel="noreferrer">/notices</a> - 수집된 공지 목록</li>
      </ul>
    </div>

    <div class="card">
      <h2>How To Use</h2>
      <p>크롤링 즉시 실행: <code>POST /crawl</code></p>
      <p>브라우저에서 테스트하려면 <code>/docs</code> 에서 각 엔드포인트의 <code>Try it out</code>을 사용하세요.</p>
    </div>
  </div>
</body>
</html>
"""

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
        subprocess.run(
            [sys.executable, "-m", "scrapy", "crawl", "daegu_notice"],
            cwd=str(PROJECT_ROOT),
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

@app.post("/crawl", status_code=202, tags=["crawler"])
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

@app.get("/status", tags=["crawler"])
def get_crawler_status():
    """
    [GET] 크롤러 실행 상태 및 마지막 가동 정보 확인
    """
    return crawler_status


@app.get("/health", tags=["service"])
def health_check(db: Session = Depends(get_db)):
    """
    API 및 DB 연결 상태 확인용 헬스 체크.
    """
    try:
        notice_count = db.query(Notice).count()
        return {
            "status": "ok",
            "db_connected": True,
            "db_type": DB_TYPE,
            "db_target": DATABASE_URL,
            "notice_count": notice_count,
            "crawler": crawler_status
        }
    except Exception as e:
        return {
            "status": "degraded",
            "db_connected": False,
            "db_type": DB_TYPE,
            "db_target": DATABASE_URL,
            "error": str(e),
            "crawler": crawler_status
        }

@app.get("/notices", tags=["notices"])
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

@app.get("/notices/{notice_id}", tags=["notices"])
def get_notice_detail(notice_id: str, db: Session = Depends(get_db)):
    """
    [GET] 특정 공지사항 상세 단건 조회
    """
    notice = db.query(Notice).filter(Notice.notice_id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail=f"Notice with ID {notice_id} not found.")
    return notice.to_dict()


@app.get("/chat", tags=["chat"])
def chat(
    q: str = Query(..., description="질문 텍스트"),
    use_db_first: bool = Query(True, description="DB 우선 조회 여부"),
    db: Session = Depends(get_db)
):
    """
    [GET] 간단한 챗봇 엔드포인트.
    - `use_db_first`가 True이면 DB에서 먼저 관련 공지를 찾고, 없을 경우 LLM에 질의합니다.
    """
    try:
        from campus_notice_crawler.utils.ai_helper import answer_query
        if use_db_first:
            result = answer_query(q, db=db)
        else:
            result = answer_query(q, db=None)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {e}")


@app.get("/chat/rag", tags=["chat"])
def chat_rag(
    q: str = Query(..., description="질문 텍스트"),
    top_k: int = Query(5, ge=1, le=10, description="검색할 관련 공지 개수"),
    db: Session = Depends(get_db)
):
    """
    [GET] 공지 기반 경량 RAG 질의 엔드포인트.
    """
    try:
        from campus_notice_crawler.utils.ai_helper import answer_query_rag
        return answer_query_rag(q, db=db, top_k=top_k)
    except Exception as e:
        # RAG 경로 실패 시에도 서비스가 멈추지 않도록 기존 chat 경로로 폴백
        try:
            from campus_notice_crawler.utils.ai_helper import answer_query
            fallback = answer_query(q, db=db)
            fallback["rag_error"] = str(e)
            return fallback
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=f"RAG and fallback failed: {fallback_error}")

if __name__ == "__main__":
    # 포트 및 호스트 환경 변수 로드
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"Starting Campus Notice AI Crawler API Server on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=False)
