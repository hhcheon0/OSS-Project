# PRD – Campus Notice AI (RAG 확장 버전)
버전: MVP v1.1 (RAG 기능 포함)  
작성일: 2026-05-28  
대상: 대학생  
형식: Markdown  

---

# 1. 서비스 개요

## 서비스명
Campus Notice AI

## 서비스 설명
대학생이 학교 홈페이지의 학사공지, 장학금, 수강신청 등의 정보를 놓치지 않도록 자동 수집(크롤링)하고, **수집된 공지 데이터를 기반으로 사용자의 질문에 정확히 답변해 주는 AI 기반 RAG(검색 증강 생성) 통합 학사공지 플랫폼**이다.

---

# 2. 5W1H 분석

| 항목 | 내용 |
|---|---|
| Why | 대학 공지는 여러 게시판에 분산되어 있고 양이 많아 원하는 정보를 정확히 찾기 어렵다. 단순 키워드 검색을 넘어 "이번 주에 신청 가능한 장학금 있어?"와 같은 자연어 질문에 데이터 기반으로 정확히 답변하는 서비스가 필요하다. |
| Who | 대학생 전체, 특히 맞춤형 공지 정보(장학금, 졸업요건 등)를 빠르게 확인하고 싶은 재학생 |
| What | 공지 통합 조회, **AI 기반 공지 Q&A (RAG)**, 검색 및 필터, 북마크, 키워드 구독 |
| How | 크롤러 → DB 저장 및 텍스트 임베딩(Vector DB) → LLM 연동(RAG) → 프론트 챗봇 UI 제공 |
| Stack | Frontend(Next.js) / Backend(FastAPI) / AI(OpenAI API, LangChain) / DB(Supabase + Vector) |
| When | MVP 4주 |

---

# 3. 사용자 정의 (Who)

## 핵심 타겟
- 대학생
- 학사공지 의존도가 높은 재학생
- 복잡한 선발 기준(장학금, 비교과)을 쉽고 빠르게 질문으로 확인하고 싶은 학생

---

## Persona A (민수)
이름: 김민수 (22세 / 컴퓨터공학과)  
목표: 나에게 맞는 장학금 공지 요약 및 마감일 놓치지 않기  
Pain Point: 공지 글이 너무 길고 지원 자격 조건(학년, 학점 등)을 일일이 읽기 번거로움  

## Persona B (지은)
이름: 이지은 (24세 / 졸업예정)  
목표: 졸업요건 및 수강신청 예외 조항 빠르게 확인  
Pain Point: 과거 공지나 학사 규정 PDF 파일 내부의 내용을 검색하기 어려움  

---

# 4. 핵심 기능 정의 (우선순위)

| 우선순위 | 기능 | 설명 |
|---|---|---|
| P0 | 공지 데이터 수집 (크롤러) | 대구대 학사공지 자동 수집 및 DB 적재 |
| P0 | **공지 기반 RAG Q&A** | **수집된 공지 본문을 기반으로 사용자 질문에 대답하는 AI 챗봇** |
| P0 | 공지 통합 조회 | 수집된 공지를 리스트 형태로 프론트에 출력 |
| P1 | 검색 및 필터 | 제목 검색 및 태그 필터 |
| P1 | 키워드 구독 및 북마크 | 관심 키워드 등록 시 알림 및 관심 공지 저장 |

---

# 5. UX Flow (How)

## 시나리오 1 – 공지 조회
사용자 접속 → 메인 페이지 진입 → 전체 공지 로딩 → 검색 / 필터 → 공지 선택 → 상세 모달 출력

## 시나리오 2 – 북마크
공지 선택 → 북마크 버튼 클릭 → 보관함 탭 이동 → 스크랩 목록 표시

## 시나리오 3 – 키워드 구독
구독 위젯 진입 → 키워드 입력(장학금, 졸업 등) → 저장 → 신규 공지 매칭 → 구독 목록 반영

## 시나리오 4 – AI 공지 Q&A (RAG)
사용자 챗봇 메뉴 진입  
↓  
자연어 질문 입력 (예: "컴공과 전공자 대상 장학금 있어?")  
↓  
FastAPI 서버가 질문 수신  
↓  
**Vector DB에서 질문과 관련성이 높은 공지사항 본문 Top N개 검색** ↓  
**검색된 공지 본문 + 사용자 질문을 LLM(Prompt)에 전달** ↓  
AI가 출처(공지 링크/제목)와 함께 답변 생성  
↓  
사용자 화면에 챗봇 답변 및 관련 공지 카드 출력  

---

# 6. 기능 상세 정의

## F-01 공지 목록
- 브랜치: `origin/app_UI`
- 구성: `app/page.js`
- 기능: 전체 공지 출력, 다크/라이트 모드, 검색, 탭 전환, 공지 필터링

## F-02 공지 카드
- 파일: `components/NoticeCard.js`
- 기능: 공지 요약 표시, 태그 출력, 작성일 표시

## F-03 상세 모달
- 파일: `components/DetailModal.js`
- 기능: 본문 출력, 이미지 출력, 첨부파일 링크, 상세 메타정보

## F-04 북마크
- 파일: `components/BookmarkList.js`
- 기능: 사용자 스크랩, 보관함 조회 (MVP는 LocalStorage 사용)

## F-05 키워드 구독
- 파일: `components/SubscriptionWidget.js`
- 기능: 키워드 등록, 관심 공지 추적

## F-06 AI 챗봇 인터페이스 (RAG 프론트)
- 파일: `components/ChatWidget.js` 또는 `app/chat/page.js`
- 기능: 
  - 사용자와 AI 간의 실시간 대화 UI
  - AI가 답변 시 참고한 실제 공지사항 링크(출처)를 하단에 카드 형태로 함께 노출

## F-07 RAG 파이프라인 (AI 백엔드)
- 브랜치: `origin/ai-rag`
- 파일: `api/rag_service.py`, `api/vector_helper.py`
- 기능:
  - **Embedding:** 크롤러가 수집한 신규 공지사항의 본문을 텍스트 임베딩(예: OpenAI `text-embedding-3-small`)하여 Vector DB에 저장
  - **Retrieval:** 사용자 질문이 들어오면 질문을 임베딩하여 유사한 공지 본문을 DB에서 추출
  - **Generation:** 추출된 공지 컨텍스트를 OpenAI(예: `gpt-4o-mini`)에 전달하여 "공지 내용에 기반해서만 답변하라"는 시스템 프롬프트 주입 후 답변 생성

---

# 7. 데이터 수집 및 관리 시스템

- 브랜치: `origin/crawler`
- 기술: Python + Scrapy
- 수집 대상: 대구대학교 학사공지
- 핵심 파일: `campus_notice_crawler/spiders/daegu_notice_spider.py`

## 수집 파이프라인
대학교 홈페이지  
↓  
Scrapy 수집  
↓  
HTML 정제 (`html_cleaner.py`)  
↓  
**[추가] 텍스트 청킹(Chunking) 및 임베딩 생성** ↓  
DB 저장 (`db_connection.py` -> Supabase 일반 테이블 및 Vector 테이블에 적재)  

## 스케줄링
- 파일: `run_scheduler.py`
- 실행 주기: 1시간

---

# 8. 기술 스택 (Stack)

## Frontend
- Next.js
- React
- Tailwind CSS
- 브랜치: `origin/app_UI`

## Backend & AI
- Python Scrapy (크롤러)
- FastAPI (API 서버)
- LangChain 또는 LlamaIndex (RAG 오케스트레이션)
- OpenAI API Key (Embedding 및 gpt-4o-mini 모델 활용)
- 브랜치: `origin/crawler`, `origin/ai-rag`

## Infra
- Supabase (pgvector 활성화 필수)
- Vercel
- GitHub

---

# 9. MVP 개발 일정 (When)

## Week 1: 기본 UI 및 크롤러 뼈대
- 프론트엔드 UI 구축 (공지 목록 + 챗봇 인터페이스 UI 레이아웃)
- Scrapy 크롤러 기본 파싱 기능 구현 및 `mockData` 연결

## Week 2: DB 연동 및 벡터화 (RAG 준비)
- Supabase DB 세팅 및 `pgvector` 활성화
- 크롤링한 데이터를 DB에 적재할 때, 본문을 적절한 길이로 잘라(Chunking) 임베딩 후 Vector DB에 저장하는 파이프라인 구축

## Week 3: RAG 파이프라인 구현 (AI 연동)
- FastAPI 백엔드에 RAG API 라우터 구현
- 사용자 질문 -> Vector DB 유사도 검색 -> OpenAI API 호출을 통한 답변 생성 로직 연동 (이 시점에 OpenAI API Key 필요)
- 프론트엔드 챗봇 UI와 RAG API 연결

## Week 4: 부가 기능 및 통합 테스트
- 출처 표기 기능 보완 (답변에 참고한 공지사항 링크 연결)
- 검색/필터/북마크 기능 고도화 및 최종 배포 (Vercel)

---

# 10. 브랜치 구조

- `origin/app_UI`: 웹 프론트엔드 UI 및 챗봇 인터페이스
- `origin/crawler`: 데이터 수집 및 스케줄러
- `origin/ai-rag`: FastAPI 기반 RAG 백엔드 API, Vector DB 연동 및 OpenAI LLM 통합 세팅