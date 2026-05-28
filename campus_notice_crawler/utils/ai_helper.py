import os
import json
import re
import requests
import threading
import time
from typing import List, Dict
from campus_notice_crawler.utils.env_loader import load_project_env
VECTOR_ENABLED = False
VECTOR_DIM = 768

load_project_env()

# Gemini API lock and timer to rate limit free tier requests (max 15 RPM, ~1 per 4 seconds)
gemini_lock = threading.Lock()
last_call_time = 0.0

def _call_gemini_with_rate_limit(url: str, payload: dict, headers: dict, timeout: float = 10.0) -> requests.Response:
    global last_call_time
    with gemini_lock:
        now = time.time()
        elapsed = now - last_call_time
        if elapsed < 4.0:
            time.sleep(4.0 - elapsed)
        last_call_time = time.time()
        
    return requests.post(url, json=payload, headers=headers, timeout=timeout)

CATEGORIES = [
    "수업학적", 
    "장학", 
    "등록", 
    "복지", 
    "교육봉사", 
    "도서관", 
    "학생모집", 
    "예비군", 
    "행정안내"
]

def analyze_notice_with_heuristics(title: str, content: str) -> dict:
    """
    룰 기반 휴리스틱을 사용하여 공지의 카테고리, 요약, 태그를 자동 생성하는 폴백 함수
    """
    # 1. 카테고리 매핑
    combined = (title + " " + content).lower()
    category = "행정안내"
    
    if any(k in combined for k in ["장학", "기금", "장학생"]):
        category = "장학"
    elif any(k in combined for k in ["수강", "학적", "폐강", "계절학기", "졸업", "휴학", "복학", "시간표"]):
        category = "수업학적"
    elif any(k in combined for k in ["등록금", "납부", "재무", "분할납부", "등록"]):
        category = "등록"
    elif any(k in combined for k in ["복지", "건강", "검진", "상담", "의료", "식당", "기숙사", "생활관"]):
        category = "복지"
    elif any(k in combined for k in ["봉사", "사회봉사", "교육봉사"]):
        category = "교육봉사"
    elif any(k in combined for k in ["도서관", "열람실", "대출", "학술정보", "도서"]):
        category = "도서관"
    elif any(k in combined for k in ["모집", "대학원", "입학", "편입", "신입생", "전형"]):
        category = "학생모집"
    elif any(k in combined for k in ["예비군", "훈련", "대원신고", "병무"]):
        category = "예비군"

    # 2. 3줄 요약 생성
    # 줄바꿈 때문에 끊긴 문장을 먼저 복원한 뒤 핵심 문장을 추출합니다.
    raw_lines = [ln.strip() for ln in (content or "").splitlines() if ln.strip()]

    merged_lines = []
    for ln in raw_lines:
        if not merged_lines:
            merged_lines.append(ln)
            continue

        prev = merged_lines[-1]
        # 이전 줄이 조사/어미로 끝나면 다음 줄과 이어붙여 문장 복원 (예: "입금자명은" + "홍길동(학번)")
        if re.search(r"(은|는|을|를|이|가|로|으로|및|와|과|:)$", prev) and len(prev) <= 40:
            merged_lines[-1] = f"{prev} {ln}"
        else:
            merged_lines.append(ln)

    # 문장 단위 후보 생성 (줄 + 구두점 분리)
    candidates = []
    for ln in merged_lines:
        parts = re.split(r"[.!?]", ln)
        for p in parts:
            p = p.strip()
            if p:
                candidates.append(p)

    def is_bad_sentence(s: str) -> bool:
        if len(s) < 12:
            return True
        if any(x in s for x in ["아래와 같이", "참고하시기", "바랍니다", "문의사항", "첨부", "붙임"]):
            return True
        # 끝이 어색하게 끊긴 조각 방지
        if re.search(r"(은|는|을|를|이|가|및|와|과|로|으로)$", s) and len(s) < 35:
            return True
        return False

    cleaned_sentences = []
    for s in candidates:
        if is_bad_sentence(s):
            continue
        cleaned_sentences.append(s)
        if len(cleaned_sentences) >= 3:
            break

    # 부족하면 완화된 기준으로 채우기
    if len(cleaned_sentences) < 3:
        for s in candidates:
            s = s.strip()
            if len(s) >= 6 and s not in cleaned_sentences:
                cleaned_sentences.append(s)
            if len(cleaned_sentences) >= 3:
                break

    while len(cleaned_sentences) < 3:
        cleaned_sentences.append("상세 내용은 공지 원문을 참조해 주시기 바랍니다.")

    # 3. 핵심 키워드 (태그) 추출
    key_points = []
    # 카테고리 기반 태그
    if category == "장학":
        key_points = ["장학금", "한국장학재단", "학자금"]
    elif category == "수업학적":
        key_points = ["학사일정", "수강신청", "학적변동"]
    elif category == "등록":
        key_points = ["등록금", "분할납부", "납부안내"]
    elif category == "복지":
        key_points = ["학생복지", "건강검진", "무료상담"]
    elif category == "교육봉사":
        key_points = ["교육봉사", "사회봉사", "멘토링"]
    elif category == "도서관":
        key_points = ["도서관", "열람실이용", "스마트열람실"]
    elif category == "학생모집":
        key_points = ["신입생모집", "대학원전형", "모집요강"]
    elif category == "예비군":
        key_points = ["학생예비군", "대원신고", "예비군훈련"]
    else:
        key_points = ["공지사항", "행정안내", "대구대학교"]

    # 타이틀에서 한글 명사구 대략 추출하여 보강
    words = re.findall(r'[가-힣]{2,8}', title)
    for w in words:
        if w not in key_points and w not in ["안내", "공지", "및", "일정", "실시", "관한", "대한", "제"]:
            key_points.append(w)
            if len(key_points) >= 5:
                break
                
    return {
        "category": category,
        "summary": cleaned_sentences[:3],
        "keyPoints": key_points[:5]
    }

def analyze_notice_with_ai(title: str, content: str) -> dict:
    """
    Gemini API를 사용하여 공지사항을 분석하여 JSON 결과를 반환합니다.
    API Key가 없거나 오류 발생 시 휴리스틱 분석으로 안전하게 폴백합니다.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return analyze_notice_with_heuristics(title, content)
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    
    prompt = f"""
다음은 대학교 학사공지사항입니다.
제목: {title}
본문:
{content[:2000]}

이 공지사항을 분석하여 아래의 JSON 형식으로만 응답해 주세요. 다른 텍스트는 일체 포함하지 마세요.

JSON 규격:
{{
  "category": "수업학적, 장학, 등록, 복지, 교육봉사, 도서관, 학생모집, 예비군, 행정안내 중 가장 알맞은 단 하나",
  "summary": [
    "핵심 요약 1문장 (50자 이내)",
    "핵심 요약 2문장 (50자 이내)",
    "핵심 요약 3문장 (50자 이내)"
  ],
  "keyPoints": [
    "핵심태그1 (해시태그 제외)",
    "핵심태그2",
    "핵심태그3",
    "핵심태그4"
  ]
}}
"""

    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = _call_gemini_with_rate_limit(url, payload=payload, headers=headers, timeout=8.0)
        if response.status_code == 200:
            res_data = response.json()
            text_response = res_data['candidates'][0]['content']['parts'][0]['text']
            
            # JSON 파싱
            result = json.loads(text_response.strip())
            
            # 카테고리 검증 및 보정
            if result.get("category") not in CATEGORIES:
                result["category"] = "행정안내"
                
            # 요약 검증
            if not isinstance(result.get("summary"), list) or len(result["summary"]) < 3:
                heuristics = analyze_notice_with_heuristics(title, content)
                result["summary"] = heuristics["summary"]
                
            # 키 포인트 검증
            if not isinstance(result.get("keyPoints"), list):
                result["keyPoints"] = ["공지사항"]
                
            return result
        else:
            print(f"Gemini API returned error code {response.status_code}. Using fallback.")
            return analyze_notice_with_heuristics(title, content)
    except Exception as e:
        print(f"Error during Gemini API call: {e}. Using fallback.")
        return analyze_notice_with_heuristics(title, content)


def call_gemini_answer(query: str) -> str:
    """
    간단한 질문-응답을 위해 Gemini API를 호출합니다. API 키가 없으면 빈 문자열을 반환합니다.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return ""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    prompt = f"""
다음 질문에 성실하게 한국어로 답변해 주세요.
질문: {query}
짧고 명확하게 답해주세요.
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 512}
    }

    try:
        r = _call_gemini_with_rate_limit(url, payload=payload, headers=headers, timeout=8.0)
        if r.status_code == 200:
            data = r.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            return text.strip()
        else:
            print(f"Gemini answer API returned status {r.status_code}")
            return ""
    except Exception as e:
        print(f"Error calling Gemini for answer: {e}")
        return ""


def call_gemini_embedding(_: str) -> List[float]:
    # Vector DB 기능 제거(로컬 SQLite 전용 모드)
    return []

def _tokenize_korean(text: str) -> List[str]:
    tokens = re.findall(r"[가-힣A-Za-z0-9]{2,}", (text or "").lower())
    return [t for t in tokens if t not in {"공지", "안내", "사항", "관련", "대해", "문의"}]


def _is_casual_chat(query: str) -> bool:
    """인사·감사 등 일반 대화성 질문 여부"""
    q = (query or "").strip().lower()
    if not q:
        return False
    casual_keywords = (
        "안녕", "하이", "hello", "hi", "반가", "고마", "감사", "잘가", "bye",
        "누구", "이름", "뭐해", "도움", "help",
    )
    if len(q) <= 30 and any(k in q for k in casual_keywords):
        return True
    return len(q) <= 12 and q.endswith(("?", "요", "야", "다"))


def _offline_conversational_reply(query: str) -> str:
    """API 키 없을 때 간단한 일반 대화 응답"""
    q = (query or "").strip()
    if "안녕" in q:
        return "안녕하세요! 대구대 학사공지 도우미입니다. 장학·수강·졸업 등 공지 관련 질문을 해 보세요."
    if "고마" in q or "감사" in q:
        return "천만에요. 다른 궁금한 점이 있으면 편하게 물어보세요."
    if "누구" in q or "이름" in q:
        return "저는 Campus Notice AI 챗봇이에요. 수집된 학사공지를 바탕으로 답변해 드립니다."
    if _is_casual_chat(q):
        return "네, 무엇을 도와드릴까요? 학사공지 관련 질문을 입력해 주세요."
    return ""


def _retrieve_relevant_notices(query: str, db, top_k: int = 5) -> List[Dict]:
    """
    경량 RAG 검색 단계:
    - SQL 1차 후보 검색 (제목/본문 LIKE)
    - 토큰 중첩 점수로 Top-K 랭킹
    """
    from campus_notice_crawler.utils.db_connection import Notice

    q_tokens = _tokenize_korean(query)
    if not q_tokens:
        q_tokens = [query.strip().lower()] if query.strip() else []

    sql_candidates = (
        db.query(Notice)
        .filter((Notice.title.contains(query)) | (Notice.content.contains(query)))
        .order_by(Notice.is_pinned.desc(), Notice.created_at.desc())
        .limit(30)
        .all()
    )

    # 전체 문장 매칭이 없으면 최근 공지에서 토큰 유사도 검색
    if not sql_candidates:
        sql_candidates = (
            db.query(Notice)
            .order_by(Notice.is_pinned.desc(), Notice.created_at.desc())
            .limit(100)
            .all()
        )

    ranked = []
    for n in sql_candidates:
        title = n.title or ""
        content = n.content or ""
        combined = f"{title} {content}".lower()
        token_score = sum(2 if tk in title.lower() else 1 for tk in q_tokens if tk and tk in combined)
        if token_score <= 0:
            continue

        snippet = None
        if n.summary and isinstance(n.summary, (list, tuple)) and len(n.summary) > 0:
            snippet = " ".join(n.summary[:2])
        elif content:
            snippet = (content[:300] + "...") if len(content) > 300 else content

        ranked.append(
            {
                "score": token_score,
                "notice_id": n.notice_id,
                "title": title,
                "summary": n.summary,
                "snippet": snippet,
                "url": n.url,
                "content": content,
                "created_at": n.created_at,
            }
        )

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]


def _generate_rag_answer_with_gemini(query: str, matches: List[Dict]) -> str:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return ""

    contexts = []
    for idx, m in enumerate(matches, 1):
        contexts.append(
            f"[문서 {idx}]\n제목: {m.get('title')}\n"
            f"작성일: {m.get('created_at')}\n"
            f"요약: {' '.join(m.get('summary') or [])}\n"
            f"본문 발췌: {(m.get('content') or '')[:800]}\n"
            f"출처: {m.get('url')}"
        )

    prompt = f"""
너는 대학 공지사항 도우미야.
반드시 아래 '검색된 공지 문맥'에 근거해서만 답변해.
문맥에 근거가 부족하면 "관련 공지를 찾지 못했습니다"라고 말하고, 사용자가 다음에 시도할 만한 검색어/질문 형태를 1~2개 제안해.
답변은 한국어로 친절하고 간결하게 작성하고, 가능하면 근거 문서 번호를 [1], [2] 형태로 표시해.

질문:
{query}

검색된 공지 문맥:
{chr(10).join(contexts)}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": 700}}
    headers = {"Content-Type": "application/json"}
    try:
        r = _call_gemini_with_rate_limit(url, payload=payload, headers=headers, timeout=10.0)
        if r.status_code == 200:
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        pass
    return ""


def answer_query_rag(query: str, db=None, top_k: int = 5) -> dict:
    """
    경량 RAG:
    1) DB 검색으로 관련 공지 Top-K 추출
    2) Gemini 키가 있으면 문맥 기반 생성
    3) 없으면 추출 결과 기반 요약 반환
    """
    used_db_session = False
    try:
        if db is None:
            from campus_notice_crawler.utils.db_connection import SessionLocal
            db = SessionLocal()
            used_db_session = True

        from campus_notice_crawler.utils.db_connection import Notice
        notice_count = db.query(Notice).count()

        # 인사/감사 등 일반 대화는 RAG 검색보다 우선 처리 (원하지 않는 공지 요약 방지)
        if _is_casual_chat(query):
            llm = call_gemini_answer(query)
            answer = llm or _offline_conversational_reply(query) or "안녕하세요! 무엇을 도와드릴까요?"
            return {
                "source": "llm" if llm else "chat",
                "answer": answer,
                "matches": [],
                "notice_count": notice_count,
            }

        matches = _retrieve_relevant_notices(query, db=db, top_k=top_k)

        if not matches:
            # DB 자체가 비어있는 경우: 안내 + 일반 대화/일반 지식 답변 허용
            if notice_count == 0:
                llm = call_gemini_answer(
                    f"사용자 질문: {query}\n"
                    "현재 학사공지 DB가 비어 있습니다. 공지 검색이 필요하면 크롤링(POST /crawl) 후 다시 시도하라고 짧게 안내하고, "
                    "일반 질문이면 친절히 답변하세요."
                )
                base = (
                    "아직 수집된 학사공지가 없습니다.\n"
                    "메인에서 새로고침(크롤링) 또는 백엔드 `POST /crawl` 실행 후 다시 질문해 주세요.\n"
                    "그 전까지는 일반적인 질문에는 답변해 드릴 수 있어요."
                )
                return {
                    "source": "empty_db",
                    "answer": llm or base,
                    "matches": [],
                    "notice_count": 0,
                }

            # 일반 대화는 공지 없어도 응답
            if _is_casual_chat(query):
                llm = call_gemini_answer(query)
                answer = llm or _offline_conversational_reply(query) or "네, 무엇을 도와드릴까요?"
                return {
                    "source": "llm" if llm else "chat",
                    "answer": answer,
                    "matches": [],
                    "notice_count": notice_count,
                }

            # 공지는 있으나 매칭이 약한 경우: LLM 일반 답변 + 안내
            llm = call_gemini_answer(query)
            if llm:
                return {
                    "source": "llm",
                    "answer": f"{llm}\n\n(참고: 질문과 직접 맞는 공지는 아직 찾지 못했습니다. 검색어를 바꿔 보세요.)",
                    "matches": [],
                    "notice_count": notice_count,
                }
            return {
                "source": "none",
                "answer": "질문과 직접 맞는 공지를 찾지 못했어요. 검색어를 조금 바꿔 보시거나 메인에서 공지 목록을 먼저 확인해 주세요.",
                "matches": [],
                "notice_count": notice_count,
            }

        rag_answer = _generate_rag_answer_with_gemini(query, matches)
        if rag_answer:
            # 모델이 번호 표기를 누락한 경우를 위해 출처 인덱스를 하단에 보강
            if "[" not in rag_answer and "]" not in rag_answer:
                refs = " ".join([f"[{idx}] {m['title']}" for idx, m in enumerate(matches, 1)])
                rag_answer = f"{rag_answer}\n\n근거 공지: {refs}"
            return {
                "source": "rag",
                "answer": rag_answer,
                "matches": matches,
                "notice_count": notice_count,
            }

        fallback_lines = []
        for idx, m in enumerate(matches, 1):
            line = f"- [{idx}] {m['title']}"
            if m.get("summary"):
                line += f": {' '.join(m['summary'][:2])}"
            fallback_lines.append(line)
        return {
            "source": "rag_fallback",
            "answer": "관련 공지 기준 요약입니다.\n" + "\n".join(fallback_lines),
            "matches": matches,
            "notice_count": notice_count,
        }
    finally:
        if used_db_session:
            try:
                db.close()
            except Exception:
                pass


def answer_query(query: str, db=None) -> dict:
    """
    DB에 저장된 공지사항에서 먼저 관련 정보를 검색하고, 결과가 없으면 LLM을 호출하여 응답을 반환합니다.

    반환 형식:
    {
      "source": "db" | "llm" | "none",
      "answer": "응답 텍스트",
      "matches": [ {"notice_id": ..., "title": ..., "summary": [...], "snippet": ...}, ... ]
    }
    """
    results = []
    answer_text = ""
    used_db_session = False

    try:
        if db is None:
            # 로컬 세션을 생성해서 사용
            from campus_notice_crawler.utils.db_connection import SessionLocal
            db = SessionLocal()
            used_db_session = True

        from campus_notice_crawler.utils.db_connection import Notice
        # 간단한 키워드 검색: 제목 또는 본문에 질의어 포함 여부
        query_filter = (Notice.title.contains(query)) | (Notice.content.contains(query))
        matches = db.query(Notice).filter(query_filter).order_by(Notice.is_pinned.desc(), Notice.created_at.desc()).limit(5).all()

        for m in matches:
            snippet = None
            if m.summary and isinstance(m.summary, (list, tuple)) and len(m.summary) > 0:
                snippet = " ".join(m.summary[:2])
            elif m.content:
                snippet = (m.content[:300] + '...') if len(m.content) > 300 else m.content

            results.append({
                "notice_id": m.notice_id,
                "title": m.title,
                "summary": m.summary,
                "snippet": snippet,
                "url": m.url
            })

        if results:
            # DB 기반 응답 조합: 매치된 공지의 요약을 결합하여 답변 생성
            parts = []
            for r in results:
                t = r.get("title")
                s = r.get("summary") or []
                if s:
                    parts.append(f"{t}: {' '.join(s)}")
                else:
                    parts.append(f"{t}")

            answer_text = "\n\n".join(parts)
            return {"source": "db", "answer": answer_text, "matches": results}
        else:
            if _is_casual_chat(query):
                llm_resp = call_gemini_answer(query)
                if llm_resp:
                    return {"source": "llm", "answer": llm_resp, "matches": []}
            return {"source": "none", "answer": "관련 공지사항이 없습니다.", "matches": []}

    finally:
        if used_db_session:
            try:
                db.close()
            except Exception:
                pass

