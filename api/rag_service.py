import os
import json
import requests
from sqlalchemy.orm import Session
from campus_notice_crawler.utils.db_connection import Notice
from api.vector_helper import get_embedding, cosine_similarity, local_keyword_similarity

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    """텍스트를 적절한 크기로 분할하여 청크 리스트 생성"""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def search_similar_notices(db: Session, query: str, top_n: int = 3) -> list:
    """
    질문에 대한 가장 유사한 공지사항 검색.
    임베딩이 가능할 시 코사인 유사도로, 미설정 시 로컬 키워드 매칭으로 검색합니다.
    """
    query_vector = get_embedding(query)
    notices = db.query(Notice).all()
    
    scored_notices = []
    
    if query_vector:
        # 벡터 기반 코사인 유사도 검색
        for notice in notices:
            if notice.embedding:
                try:
                    # DB에 저장된 embedding은 JSON 형태 (float 배열)
                    embedding_list = notice.embedding
                    if isinstance(embedding_list, str):
                        embedding_list = json.loads(embedding_list)
                    
                    similarity = cosine_similarity(query_vector, embedding_list)
                    scored_notices.append((notice, similarity))
                except Exception as e:
                    print(f"[RAG Service] Cosine calculation failed for {notice.notice_id}: {e}")
                    # 실패 시 키워드 매칭 백업
                    score = local_keyword_similarity(query, (notice.title or "") + " " + (notice.content or ""))
                    scored_notices.append((notice, score * 0.01)) # 스케일링
            else:
                # 임베딩 없는 경우 키워드 매칭 백업
                score = local_keyword_similarity(query, (notice.title or "") + " " + (notice.content or ""))
                scored_notices.append((notice, score * 0.01))
    else:
        # 로컬 키워드 매칭 검색
        for notice in notices:
            score = local_keyword_similarity(query, (notice.title or "") + " " + (notice.content or ""))
            scored_notices.append((notice, score))
            
    # 정렬 및 Top N 선택
    scored_notices.sort(key=lambda x: x[1], reverse=True)
    return scored_notices[:top_n]

def generate_rag_answer(query: str, similar_notices: list) -> dict:
    """
    검색된 공지사항 목록을 컨텍스트로 결합하여 AI 답변을 생성합니다.
    """
    # 컨텍스트 빌드
    context_parts = []
    citations = []
    
    for idx, (notice, score) in enumerate(similar_notices):
        # 텍스트가 너무 길면 잘라내서 전달
        content_snippet = (notice.content or "")[:800]
        context_parts.append(
            f"[{idx + 1}] 제목: {notice.title}\n"
            f"카테고리: {notice.category}\n"
            f"작성일: {notice.created_at}\n"
            f"본문: {content_snippet}\n"
            f"링크: {notice.url}\n"
        )
        citations.append({
            "id": notice.notice_id,
            "title": notice.title,
            "category": notice.category,
            "date": notice.created_at,
            "url": notice.url
        })
        
    context = "\n---\n".join(context_parts)
    
    # API 키 확인 및 요청 분기
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    system_prompt = (
        "당신은 대학교 학사공지사항에 대답하는 전문 AI 비서입니다. "
        "제공된 [학사공지 사항 컨텍스트]에만 전적으로 기반하여 사용자의 질문에 정확하고 공손하게 대답하세요. "
        "만약 컨텍스트에서 답변을 찾을 수 없는 경우, 알 수 없다고 친절히 답변하고 학교 홈페이지를 참고하라고 하세요. "
        "답변을 할 때는 내용 끝부분에 반드시 출처 공지의 인덱스(예: [1] 또는 [2])를 명시해주세요."
    )
    
    user_prompt = f"""
[학사공지 사항 컨텍스트]:
{context}

사용자 질문:
{query}

위의 학사공지 사항 컨텍스트를 활용하여 질문에 대한 친절한 답변을 작성해 주세요.
"""

    if gemini_key:
        # Gemini API를 사용하여 답변 생성
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"{system_prompt}\n\n{user_prompt}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.3
            }
        }
        headers = {"Content-Type": "application/json"}
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=12.0)
            if res.status_code == 200:
                res_data = res.json()
                text = res_data['candidates'][0]['content']['parts'][0]['text']
                return {"answer": text, "citations": citations}
        except Exception as e:
            print(f"[RAG Service] Gemini Q&A failed: {e}")
            
    elif openai_key:
        # OpenAI API fallback
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=12.0)
            if res.status_code == 200:
                text = res.json()["choices"][0]["message"]["content"]
                return {"answer": text, "citations": citations}
        except Exception as e:
            print(f"[RAG Service] OpenAI Q&A failed: {e}")

    # 모든 API 키 누락 또는 에러 시 룰 기반 응답 폴백
    fallback_answer = (
        "현재 AI API 연동이 설정되지 않았거나 원활하지 않습니다.\n\n"
        "질문과 관련이 높은 공지사항은 다음과 같습니다. 아래 공지들의 상세 정보나 링크를 직접 확인해 보세요:\n\n"
    )
    for idx, (notice, _) in enumerate(similar_notices):
        fallback_answer += f"{idx + 1}. **{notice.title}** ({notice.created_at}) - [원문 바로가기]({notice.url})\n"
        
    if not similar_notices:
        fallback_answer = "질문과 관련된 공지사항을 데이터베이스에서 찾을 수 없습니다. 대학교 공식 홈페이지를 직접 방문해 보세요."
        
    return {"answer": fallback_answer, "citations": citations}
