import os
import math
import requests
from dotenv import load_dotenv

load_dotenv()

def get_embedding(text: str) -> list:
    """
    Gemini API를 사용하여 텍스트 임베딩 생성 (text-embedding-004 모델)
    API 키가 없거나 실패할 경우, 빈 리스트를 반환하여 로컬 대체 매칭으로 유도합니다.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return []
        
    url = f"https://genergener-not-quite-right-but-standard-generativelanguage" # Let's use the correct standard url
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={gemini_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # 텍스트 크기 제한 안전 처리
    payload = {
        "content": {
            "parts": [{
                "text": text[:4000]
            }]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=8.0)
        if response.status_code == 200:
            res_data = response.json()
            embedding = res_data.get("embedding", {}).get("values", [])
            return embedding
        else:
            print(f"[Vector Helper] Embedding API error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"[Vector Helper] Failed to get embedding: {e}")
        return []

def cosine_similarity(v1: list, v2: list) -> float:
    """두 벡터 간의 코사인 유사도 계산"""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
        
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

def local_keyword_similarity(query: str, document: str) -> float:
    """
    API 키 미설정 시 작동하는 키워드 빈도 및 매칭 기반 로컬 유사도 알고리즘 (TF-IDF/BM25 유사 개념 구현)
    """
    if not query or not document:
        return 0.0
        
    query_words = [w.lower() for w in query.split() if len(w) > 1]
    doc_words = document.lower()
    
    if not query_words:
        # 단일 자모나 짧은 단어 검색 대응
        query_words = [query.lower()]
        
    score = 0.0
    for qw in query_words:
        # 제목 매칭 및 본문 내 등장 횟수 기반 점수 합산
        count = doc_words.count(qw)
        if count > 0:
            score += 1.0 + math.log1p(count)
            
    return score
