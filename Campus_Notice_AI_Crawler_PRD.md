# 대학생 대상 AI 학사공지 웹 크롤러 시스템 PRD (재작성본)

## 1. 프로젝트 개요

### 프로젝트명
**Campus Notice AI Crawler**

### 프로젝트 목적
- Scrapy GitHub Repository: https://github.com/hhcheon0/scrapy.git
- 대구대학교 학사공지 게시판: https://www.daegu.ac.kr/article/DG159/list

대구대학교 학사공지 게시판의 공지를 자동 수집하고,  
AI 요약 시스템과 쉽게 연동 가능한 “독립형 웹 크롤링 모듈”을 구축한다.

본 프로젝트는:
- 웹 크롤링 기능만 구현
- 다른 프로젝트에 병합 가능한 구조 제공
- AI 요약 서버에 전달 가능한 데이터 포맷 제공
- 대학생 대상 공지 자동화 시스템의 기반 역할 수행

을 목표로 한다.

---

# 2. 프로젝트 목표

## Primary Goal
대구대학교 학사공지 데이터를 안정적으로 수집 가능한 Scrapy 기반 크롤러 구축

## Secondary Goal
AI 요약 및 외부 서비스 연동이 쉬운 구조 설계

---

# 3. 5W1H 분석

| 항목 | 내용 |
|---|---|
| Who | 대학생, 학교 공지 서비스 개발자 |
| What | 학사 공지 자동 수집 크롤러 |
| When | 일정 주기 자동 실행 |
| Where | 대구대학교 학사공지 게시판 |
| Why | 긴 공지를 AI로 빠르게 요약 제공하기 위함 |
| How | Scrapy 기반 웹 크롤링 + 데이터 가공 + API 전달 |

---

# 4. 서비스 범위

## 포함 범위
- 학사공지 목록 크롤링
- 상세 공지 크롤링
- 첨부파일 링크 추출
- 공지 데이터 저장
- 중복 제거
- AI 요약 시스템 전달용 데이터 생성

## 제외 범위
- AI 모델 개발
- 모바일 앱
- 사용자 인증
- 알림 기능
- 프론트엔드 UI

---

# 5. 핵심 기능 상세 정의

## 5.1 공지 목록 크롤링

### 설명
학사공지 게시판 목록 데이터를 자동 수집한다.

### 대상 URL
```text
https://www.daegu.ac.kr/article/DG159/list
```

### 수집 항목

| 필드 | 설명 |
|---|---|
| notice_id | 공지 번호 |
| title | 공지 제목 |
| url | 상세 URL |
| author | 작성자 |
| created_at | 작성일 |
| is_pinned | 상단 고정 여부 |

### 기능 요구사항
- 페이지네이션 자동 탐색
- 최신 공지 우선 수집
- 중복 공지 제외

---

## 5.2 공지 상세 크롤링

### 설명
공지 상세 페이지 내부 데이터를 수집한다.

### 수집 항목

| 필드 | 설명 |
|---|---|
| content | 공지 본문 |
| attachments | 첨부파일 링크 |
| images | 이미지 링크 |
| view_count | 조회수 |

### 처리 요구사항
- HTML 정제
- 불필요 태그 제거
- 본문 normalize

---

## 5.3 중복 제거 시스템

### 설명
이미 저장된 공지를 재수집하지 않도록 처리한다.

### 중복 기준
- notice_id
- URL hash
- title + created_at 조합

---

## 5.4 데이터 저장 모듈

### 저장 포맷(JSON)

```json
{
  "notice_id": "12345",
  "title": "2026학년도 수강신청 안내",
  "content": "공지 본문",
  "attachments": [],
  "created_at": "2026-05-22",
  "source": "daegu_university"
}
```

### 저장 방식
- JSON Export
- SQLite
- PostgreSQL
- Supabase 호환 구조

---

## 5.5 AI 요약 인터페이스

### 목적
AI 서버에 전달 가능한 구조 제공

### 전달 포맷

```json
{
  "title": "수강신청 안내",
  "content": "공지 원문",
  "summary_target": true
}
```

### 연동 대상
- OpenAI API
- Claude API
- Gemini API
- FastAPI 기반 AI 서버

---

# 6. UX Flow

## 시스템 Flow

```text
대학교 공지 등록
    ↓
Scrapy Spider 실행
    ↓
공지 목록 수집
    ↓
상세 페이지 크롤링
    ↓
중복 검사
    ↓
데이터 저장
    ↓
AI 요약 서버 전달
    ↓
외부 서비스 활용
```

---

# 7. 시스템 아키텍처

```text
[Daegu University Notice]
              ↓
       [Scrapy Spider]
              ↓
      [HTML Parsing]
              ↓
     [Data Cleaning]
              ↓
    [Duplicate Filter]
              ↓
         [Storage]
              ↓
    [AI Summary API]
              ↓
  [External Services]
```

---

# 8. 기술 스택

## Backend

| 영역 | 기술 |
|---|---|
| Language | Python 3.11 |
| Crawling | Scrapy |
| Parsing | BeautifulSoup4 |
| HTTP | Requests |
| Async | Asyncio |
| Scheduler | APScheduler |

---

## Database

| 영역 | 기술 |
|---|---|
| Local DB | SQLite |
| Production DB | PostgreSQL |
| Cloud DB | Supabase |

---

## DevOps

| 영역 | 기술 |
|---|---|
| Version Control | GitHub |
| Container | Docker |
| Env Management | dotenv |
| CI/CD | GitHub Actions |

---

# 9. 폴더 구조 제안

```text
scrapy/
├── spiders/
│   └── daegu_notice_spider.py
├── pipelines/
├── parsers/
├── services/
│   ├── storage_service.py
│   └── summary_interface.py
├── utils/
├── config/
├── tests/
└── outputs/
```

---

# 10. 병합 친화적 설계 전략

## 목표
크롤러를 독립 모듈로 유지하여 다양한 서비스에 쉽게 연결 가능하도록 구성한다.

---

## 병합 방식

### 1. REST API 방식

```text
Crawler → FastAPI → Frontend/App
```

---

### 2. DB 공유 방식

```text
Crawler → Supabase → App/Web
```

---

### 3. Queue 방식

```text
Crawler → Redis Queue → AI Service
```

---

# 11. MVP 로드맵

## Phase 1 — 기본 크롤러
기간: 1주

기능:
- 공지 목록 수집
- 상세 페이지 수집
- JSON 저장

---

## Phase 2 — 자동화
기간: 1주

기능:
- Scheduler 추가
- 중복 제거
- Logging 시스템

---

## Phase 3 — AI 연동 준비
기간: 1주

기능:
- AI 전달 포맷
- API Interface
- DB 연동

---

## Phase 4 — 확장성 개선
기간: 1주

기능:
- 다중 대학 지원
- Docker 구성
- FastAPI 연동

---

# 12. 리스크 및 대응 전략

| 리스크 | 설명 | 대응 전략 |
|---|---|---|
| HTML 구조 변경 | 사이트 구조 변경 가능 | Selector 모듈화 |
| 과도한 요청 차단 | 서버 차단 가능성 | Delay 및 Retry 적용 |
| 중복 데이터 | 동일 공지 반복 저장 | Hash 기반 필터링 |
| 첨부파일 구조 변경 | 파일 링크 변경 가능 | 예외 처리 로깅 |
| 유지보수 복잡성 | 크롤러 증가 시 복잡화 | Spider 분리 설계 |
| AI 비용 증가 | 요약 API 비용 문제 | 중요 공지 필터링 |

---

# 13. 개발 우선순위

| 우선순위 | 기능 |
|---|---|
| P0 | 공지 목록 크롤링 |
| P0 | 상세 공지 크롤링 |
| P1 | 데이터 저장 |
| P1 | 중복 제거 |
| P2 | AI 전달 인터페이스 |
| P2 | Scheduler |
| P3 | 다중 대학 확장 |

---

# 14. 성공 지표(KPI)

| 항목 | 목표 |
|---|---|
| 공지 수집 성공률 | 95% 이상 |
| 신규 공지 반영 속도 | 10분 이내 |
| 중복 제거 정확도 | 99% 이상 |
| 크롤링 실패율 | 5% 이하 |

---

# 15. 향후 확장 방향

## 확장 가능 기능
- 다중 대학 지원
- 학과별 공지 분류
- 중요도 AI 분석
- Discord/카카오 알림
- 벡터 검색
- RAG 챗봇 연동

---

# 16. Scrapy 라이선스 전문 (BSD-3-Clause)

```text
Copyright (c) 2008-2026, Scrapy developers
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of Scrapy nor the names of its contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

---

# 17. 최종 요약

본 프로젝트는 Scrapy 기반의 대학 학사공지 웹 크롤러를 구축하여:

- 공지를 자동 수집하고
- AI 요약 시스템과 연결 가능하며
- 외부 서비스와 쉽게 병합 가능한 구조를 제공하는

“독립형 대학 공지 크롤링 모듈” 개발 프로젝트이다.
