import requests

url = "http://127.0.0.1:8000/chat/rag"

test_cases = [
    # 1. Matching academic/notice question
    "2026 계절학기 학점교류 신청 기간 알려줘",
    
    # 2. Non-matching academic/notice question
    "컴퓨터공학과 기계학습 기말고사 일정 알려줘",
    
    # 3. Casual chat
    "안녕하세요 반가워요!"
]

for idx, q in enumerate(test_cases, 1):
    print(f"\n==================== Test Case {idx} ====================")
    print(f"Query: {q}")
    r = requests.get(url, params={"q": q, "top_k": 5})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Source: {data.get('source')}")
        print(f"Answer: {data.get('answer')}")
        matches = data.get('matches', [])
        print(f"Matches count: {len(matches)}")
        for idx_m, m in enumerate(matches[:2], 1):
            print(f"  Match {idx_m}: {m.get('title')} ({m.get('url')})")
    else:
        print("Error:", r.text)
