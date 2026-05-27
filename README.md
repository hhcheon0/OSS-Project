# Campus Notice AI

2026 대구대학교 오픈소스소프트웨어 팀 프로젝트 19조

학사공지, 장학금, 수강신청 등 흩어져 있는 대학교 공지사항을 놓치지 않도록 자동 수집(크롤링)하고, AI 기반 요약과 키워드 구독, 검색 및 북마크 기능을 제공하는 통합 학사공지 플랫폼입니다.

---

## 🌟 핵심 기능

- **학사공지 통합 조회**: 대구대 학사공지 게시판(`DG159`) 데이터를 수집하여 한 곳에서 리스트 제공
- **공지 상세 조회**: 상세 모달창을 통해 본문, 첨부파일 다운로드 링크, 이미지 출력
- **AI 요약 & 태그**: 공지사항의 3줄 요약 및 핵심 태그 자동 생성 제공 (예정)
- **키워드 구독**: 관심 키워드(예: 장학금, 졸업) 등록 시 맞춤 공지 추적
- **북마크**: 중요 공지사항을 스크랩하여 보관함에 저장 (LocalStorage 기반)
- **다크/라이트 모드**: 사용자의 환경에 맞춘 편안한 다크 모드 지원

---

## 📂 프로젝트 구조

```text
├── app/                      # Next.js 프론트엔드 UI 페이지
│   ├── page.js               # 메인 대시보드
│   └── globals.css           # 글로벌 CSS (Tailwind)
├── components/               # React 컴포넌트
│   ├── NoticeCard.js         # 공지 카드 컴포넌트
│   ├── DetailModal.js        # 상세 보기 모달
│   ├── BookmarkList.js       # 북마크 보관함
│   └── SubscriptionWidget.js # 키워드 구독 위젯
├── campus_notice_crawler/   # Scrapy 프로젝트 패키지 (크롤러)
│   ├── items.py             # 공지사항 수집 Item 정의
│   ├── settings.py          # Scrapy 설정 (딜레이, 미들웨어 등)
│   ├── spiders/
│   │   └── daegu_notice_spider.py # 대구대 학사공지 전용 스파이더
│   ├── utils/
│   │   ├── html_cleaner.py  # HTML 텍스트 정제 유틸리티
│   │   └── db_connection.py # SQLAlchemy DB 연결 및 스키마 정의
│   └── pipelines.py         # 정제, 중복제거, DB 적재 파이프라인
├── run_scheduler.py        # 크롤러 자동 스케줄러 실행 스크립트
├── main.py                  # 협업용 경량 FastAPI 제어 서버
├── requirements.txt         # 파이썬 라이브러리 의존성
├── package.json             # Next.js 프론트엔드 의존성
└── PRD.md                   # 제품 요구사항 정의서 (PRD)
```

---

## 🚀 실행 가이드

### 1. 백엔드 및 크롤러 실행 (Python)

#### 의존성 패키지 설치
```bash
python -m venv venv
venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

#### 환경 변수 설정 (`.env`)
프로젝트 루트 폴더에 `.env` 파일을 생성하거나 `.env.example`을 참고해 다음과 같이 구성합니다.
```ini
DB_TYPE=sqlite
DB_PATH=campus_notices.db
CRAWL_INTERVAL_MINUTES=60
API_PORT=8000
API_HOST=0.0.0.0
```

#### FastAPI 백엔드 서버 구동
서버가 기동되면 SQLite 데이터베이스 스키마가 자동 생성되며, 크롤러 제어 및 데이터 연동을 위한 API가 활성화됩니다.
```bash
python main.py
```
- **Swagger UI**: `http://localhost:8000/docs`
- **`GET /notices`**: 수집된 학사공지 목록 조회
- **`POST /crawl`**: 크롤러 즉시 가동 트리거 (비동기)

#### 크롤러 스케줄러 단독 가동 (백그라운드 자동 수집)
```bash
python run_scheduler.py
```

---

### 2. 프론트엔드 실행 (Next.js)

#### 의존성 설치 및 실행
```bash
npm install
npm run dev
```
- 브라우저에서 `http://localhost:3000`으로 접속하여 통합 학사공지 대시보드를 확인할 수 있습니다.

---

## 🛠 GitHub Flow 워크플로우

본 프로젝트는 GitHub Flow 방식을 준수합니다.

1. **브랜치 생성**: 최신 `main`에서 기능 단위로 분기합니다. (`feature/기능명`)
2. **작업 및 커밋**: 작은 단위로 커밋하여 원격에 Push합니다.
3. **PR 생성**: 리뷰 및 통합 테스트를 위해 PR을 개설합니다.
4. **리뷰 & CI 통과**: 코드 품질을 검증합니다.
5. **병합 (Merge)**: 검증된 코드를 `main`에 병합합니다.
6. **브랜치 삭제**: 병합 완료 후 로컬 및 원격 브랜치를 정리합니다.

