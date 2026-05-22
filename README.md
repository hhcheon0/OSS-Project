# Campus Notice AI Crawler

대구대학교 학사공지 게시판의 데이터를 자동으로 수집하고, 정제 및 중복 제거를 거쳐 로컬 데이터베이스 또는 Supabase(PostgreSQL)에 적재하고 타 팀원의 AI 요약 시스템에 Webhook 형태로 공지를 전달할 수 있는 **독립형 웹 크롤링 모듈**입니다.

## 🌟 핵심 기능
- **공지사항 수집**: 대구대 학사공지 게시판(`DG159`) 파싱. 상단 고정(Pinned) 공지와 일반 공지를 분리 수집합니다.
- **상세 데이터 추출**: 본문 텍스트 정제, 조회수, 첨부파일 및 이미지 링크 자동 추출.
- **데이터 정제(Cleaning)**: HTML 구조 정제, 불필요 태그 제거, 텍스트 Normalize.
- **중복 수집 방지**: `notice_id` 기반 중복 체크 필터 적용.
- **유연한 저장소**: SQLite 로컬 적재 및 Supabase(PostgreSQL) 호환 스키마 제공.
- **AI 요약 연동**: 크롤링 후 타 팀원의 AI 요약 서버로 즉시 데이터 전송(Webhook) 기능 포함.
- **경량 관리 API**: FastAPI를 탑재하여 외부(App/UI 파트)에서 손쉽게 크롤링 트리거 및 수집 데이터 목록을 JSON으로 가져갈 수 있습니다.
- **자동화 스케줄러**: APScheduler를 사용하여 정해진 분 주기마다 자동으로 백그라운드 크롤링을 수행합니다.

---

## 📂 폴더 구조

```text
├── campus_notice_crawler/   # Scrapy 프로젝트 패키지
│   ├── items.py             # 공지사항 수집 Item 정의
│   ├── settings.py          # Scrapy 설정 (딜레이, 미들웨어 등)
│   ├── spiders/
│   │   └── daegu_notice_spider.py # 대구대 학사공지 전용 스파이더
│   ├── utils/
│   │   ├── html_cleaner.py  # HTML 텍스트 정제 유틸리티
│   │   └── db_connection.py # SQLAlchemy DB 연결 및 스키마 정의
│   └── pipelines.py         # 정제, 중복제거, DB 적재, Webhook 발송 파이프라인
├── scrapy.cfg               # Scrapy 설정 루트
├── requirements.txt         # 파이썬 라이브러리 의존성
├── .env.example             # 환경 변수 설정 템플릿
├── .env                     # 실제 설정값 (SQLite/PostgreSQL 등)
├── run_scheduler.py        # 크롤러 자동 스케줄러 실행 스크립트
├── main.py                  # 협업용 경량 FastAPI 제어 서버
└── LICENSE                  # Scrapy BSD-3-Clause 라이선스 전문
```

---

## 🚀 빠른 시작 가이드

### 1. 가상환경 및 의존성 패키지 설치
```bash
python -m venv venv
venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (`.env`)
`.env` 파일을 편집하여 사용하고자 하는 DB 정보와 AI 요약 서버 API 경로를 설정합니다. 기본 설정은 로컬 SQLite를 사용하도록 셋팅되어 있습니다.

```ini
DB_TYPE=sqlite
DB_PATH=campus_notices.db
AI_SUMMARY_WEBHOOK_URL=http://localhost:8000/api/summarize
CRAWL_INTERVAL_MINUTES=60
```

### 3. 크롤러 단독 실행
```bash
scrapy crawl daegu_notice
```

### 4. 협업용 FastAPI 서버 구동 (추천)
서버 및 프론트엔드 담당 팀원이 크롤러를 쉽게 제어하고 데이터를 API 형태로 편하게 가져갈 수 있도록 REST API를 제공합니다.
```bash
python main.py
```
서버가 실행되면 다음 API들을 즉시 연동할 수 있습니다.
- **`GET /notices`**: 현재까지 수집된 학사공지 목록 조회 (JSON 형식)
- **`POST /crawl`**: 크롤러 즉시 가동 트리거 (비동기 수행)
- **`GET /notices/{notice_id}`**: 특정 공지 상세 정보 조회

### 5. 백그라운드 자동 주기적 수집기 구동
스케줄러를 백그라운드에 구동시켜 두고 싶을 때 실행합니다.
```bash
python run_scheduler.py
```

---

## 📄 데이터 규격

### 1. 기본 수집 포맷 (JSON)
```json
{
  "notice_id": "12345",
  "title": "2026학년도 수강신청 안내",
  "url": "https://www.daegu.ac.kr/article/DG159/detail/12345",
  "author": "학사지원팀",
  "created_at": "2026-05-22",
  "is_pinned": false,
  "content": "공지 본문 텍스트...",
  "attachments": [
    {"name": "수강안내문.pdf", "url": "https://www.daegu.ac.kr/download/..."}
  ],
  "images": [
    "https://www.daegu.ac.kr/images/..."
  ],
  "view_count": 142
}
```

### 2. AI 요약 Webhook 포맷
크롤링된 공지는 AI 요약 Pipeline을 거쳐 지정된 서버로 아래 형태로 자동 POST 전송됩니다.
```json
{
  "title": "2026학년도 수강신청 안내",
  "content": "공지 본문 텍스트...",
  "summary_target": true
}
```

---

## ⚖️ 라이선스
본 프로젝트에서 사용하는 웹 크롤러 프레임워크 Scrapy는 BSD-3-Clause 라이선스를 따르며, 자세한 라이선스 전문은 [LICENSE](./LICENSE) 파일을 참고하십시오.
