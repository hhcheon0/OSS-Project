# Campus Notice AI

Campus Notice AI는 대학생들이 학사공지, 장학금, 수강신청, 비교과 프로그램 등의 중요한 공지를 놓치지 않도록 대학 홈페이지 공지를 자동으로 수집하고, AI 기반 요약, 키워드 구독 및 북마크 기능을 제공하는 통합 학사공지 플랫폼입니다.

본 저장소는 **Next.js 기반의 프론트엔드 웹 UI 클라이언트**와 **Python Scrapy/FastAPI 기반의 데이터 수집 및 관리 API 서비스**가 통합되어 즉시 배포 및 구동 가능한 모노레포 형태의 프로젝트입니다.

---

## 🌟 핵심 기능

### 1. Frontend Web Client (Next.js)
- **공지사항 피드**: 수집 완료된 공지를 깔끔한 리스트와 다양한 필터(수업학적, 장학, 등록, 복지, 교육봉사, 도서관, 학생모집, 예비군, 행정안내)로 신속 조회.
- **상세 뷰 & AI 요약**: 공지 본문 내용의 구조적 가시화, 첨부파일 및 이미지 뷰 기능과 더불어 AI가 핵심 요점을 3줄로 요약해 주는 스마트 기능 탑재.
- **키워드 구독**: 관심 있는 키워드(예: `장학금`, `수강신청`, `졸업`)를 등록하여 관련된 공지가 있을 시 즉시 하이라이팅 및 추적.
- **북마크 (보관함)**: 중요한 공지를 보관함에 담아 언제든지 빠르고 간편하게 재참조.
- **하이브리드 다크/라이트 테마**: 사용자 환경에 최적화된 Sleek HSL 다크 모드와 고대비 라이트 모드 지원.

### 2. Crawler & Backend API (Python, Scrapy & FastAPI)
- **자동 수집 크롤러**: 대구대학교 학사공지 게시판을 타겟으로 하여 상단 고정(Pinned) 공지와 일반 공지를 분리 수집합니다.
- **상세 데이터 추출**: 본문 텍스트 정제, 조회수, 첨부파일 다운로드 경로 및 본문 내 이미지 경로 추출.
- **데이터 정제 및 중복 제거**: BeautifulSoup4 기반 HTML 태그 제거 및 텍스트 Normalize. `notice_id` 기반 중복 체크 필터 적용.
- **FastAPI REST API**: 웹 UI에서 실시간 데이터 호출, 크롤링 즉시 트리거 및 개별 공지 상세를 조회하기 위한 API 라우트 제공.
- **APScheduler 백그라운드 자동화**: 주기적인 간격(예: 1시간)으로 크롤러가 구동되어 새로운 공지를 상시 업데이트.

---

## 📂 프로젝트 구조

```text
├── app/                     # Next.js 15 App Router (프론트엔드 페이지 및 레이아웃)
│   ├── favicon.ico
│   ├── globals.css          # 글로벌 스타일 및 테마 정의
│   ├── layout.js
│   └── page.js              # 메인 대시보드
├── components/              # React 재사용 컴포넌트
│   ├── BookmarkList.js      # 북마크 보관함 목록
│   ├── DetailModal.js       # 공지 상세 및 AI 3줄 요약 모달
│   ├── NoticeCard.js        # 개별 공지 카드 및 키워드 하이라이터
│   └── SubscriptionWidget.js# 키워드 구독 관리 위젯
├── utils/
│   └── mockData.js          # 초기 구동 및 폴백용 목업 데이터
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
├── package.json             # Node.js 패키지 의존성 및 스크립트
├── run_scheduler.py        # 크롤러 자동 스케줄러 실행 스크립트
├── main.py                  # 백엔드 FastAPI 제어 서버 및 REST API
└── PRD.md                   # 전체 제품 요구 기획서
```

---

## 🚀 시작하기 및 배포 안내

### 1. 백엔드 API & 크롤러 실행 (Python)

#### 1) 가상환경 구축 및 패키지 설치
```bash
python -m venv venv
venv\Scripts\activate      # Windows PowerShell
source venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
```

#### 2) 환경 변수 설정 (`.env`)
루트 디렉토리에 `.env` 파일을 생성하고 설정을 입력합니다:
```ini
DB_TYPE=sqlite
DB_PATH=campus_notices.db
API_PORT=8000
API_HOST=127.0.0.1
CRAWL_INTERVAL_MINUTES=60
```

#### 3) FastAPI 백엔드 웹 서버 기동 (추천)
```bash
python main.py
```
- FastAPI Swagger 문서: `http://127.0.0.1:8000/docs`
- 수집 데이터 API: `GET http://127.0.0.1:8000/notices`

#### 4) 수동 크롤러 가동 및 스케줄러 실행
- **1회성 즉시 크롤링**: `scrapy crawl daegu_notice`
- **주기적 크롤러 자동 구동**: `python run_scheduler.py`

---

### 2. 프론트엔드 클라이언트 실행 (Node.js)

#### 1) 패키지 설치
```bash
npm install
```

#### 2) 개발 서버 구동
```bash
npm run dev
```
- 로컬 개발 서버: `http://localhost:3000` 에서 즉시 확인 가능합니다.

---

## 📄 기술 스택 (Tech Stack)

### Frontend
- Next.js (App Router)
- React 19
- Framer Motion (부드러운 모달 및 탭 모션 애니메이션)
- Lucide React (아이콘 에셋)
- Tailwind CSS

### Backend & Crawler
- Python 3.11+
- FastAPI & Uvicorn
- Scrapy & BeautifulSoup4
- SQLAlchemy (SQLite & PostgreSQL 지원)
- APScheduler
