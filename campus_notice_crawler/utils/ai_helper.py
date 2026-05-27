import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

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
    # 본문에서 문장 단위로 분할하여 핵심적인 내용을 추출
    sentences = re.split(r'[.!?\n]', content)
    cleaned_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) > 10 and not any(x in s for x in ["아래와 같이", "참고하시기", "바랍니다", "문의사항"]):
            cleaned_sentences.append(s)
            if len(cleaned_sentences) >= 3:
                break
                
    # 문장이 너무 부족할 시의 안전 장치
    if len(cleaned_sentences) < 3:
        # 일반적인 문장 수집
        cleaned_sentences = [s.strip() for s in sentences if len(s.strip()) > 5][:3]
        
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
        response = requests.post(url, json=payload, headers=headers, timeout=8.0)
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

