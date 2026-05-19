# Status: In Progress

# Weather-OSS-Project
 - 2026 대구대학교 오픈소스소프트웨어 팀 프로젝트 19조

# 1. 프로젝트 목적: "오픈소스 데이터를 활용한 직관적인 날씨 웹 서비스"
 - GitHub Flow 방식으로 진행

### 🛠 GitHub Flow 워크플로우 (6단계)

### 1. 브랜치 생성
항상 최신 main에서 분기합니다.

의미 있는 브랜치 이름 사용

기능(feature) 단위 격리

Bash
git switch -c feature/add-auth

### 2. 작업 및 커밋
로컬 작업 후 원격에 Push합니다.

작은 단위로 자주 커밋

Push로 원격 백업 및 공유

Bash
git push origin feature/add-auth

### 3. PR 생성 (개설)
도움 요청 또는 병합 준비가 완료된 상태입니다.

💬 "코드에 대한 대화의 시작점"

### 4. 리뷰 & CI 통과
코드 품질 검증 단계입니다.

✅ Tests Passing

✅ Review Approved

### 5. 병합 (Merge)
검증된 코드를 main에 반영합니다.

즉시 배포 가능 상태 유지

자동 배포(CD) 트리거됨

### 6. 브랜치 삭제
역할이 끝난 브랜치는 정리합니다.

Bash
git branch -d feature/add-auth

# 2. 역할 분담

🌦️ 추천 역할 분담 (3인 체제)
1. UI/UX 및 프론트엔드 개발 (Frontend & Design)

사용자가 직접 보는 날씨 화면과 인터페이스를 담당합니다.

주요 임무
메인 날씨 대시보드 구현
현재 날씨 / 주간 예보 UI 제작
반응형 웹 디자인 적용
다크모드 및 테마 설정
날씨 아이콘 및 애니메이션 적용
기술 포인트
HTML/CSS/JavaScript
React/Vue 등 프론트엔드 프레임워크
CSS Grid/Flexbox
Chart.js 또는 Recharts 활용
Git 브랜치 추천
feature/main-ui
feature/weather-dashboard
feature/dark-mode

2. 날씨 데이터 처리 및 API 연동 (Weather Data Engineer)

외부 날씨 데이터를 가져오고 가공하는 핵심 기능을 담당합니다.

주요 임무
OpenAPI 연동 (날씨)
지역 검색 기능 구현
실시간 날씨 데이터 처리
기온/습도/풍속 데이터 가공
API 오류 및 예외 처리
기술 포인트
Fetch/Axios 비동기 통신
REST API
JSON 데이터 처리
환경 변수(API Key) 관리
Git 브랜치 추천
feature/weather-api
feature/location-search
feature/data-parser

3. 백엔드 및 시스템 관리 (Backend & System Engineer)

프로젝트의 서버 및 데이터 저장 기능을 담당합니다.

주요 임무
사용자 즐겨찾기 지역 저장
로그인 기능 구현(Optional)
서버 구축 및 배포
캐싱 및 성능 최적화
CI/CD 및 GitHub 협업 환경 관리
기술 포인트
Node.js / Express
Firebase 또는 MongoDB
GitHub Actions
Vercel / Render / AWS 배포
Git 브랜치 추천
feature/backend
feature/auth
feature/deployment
