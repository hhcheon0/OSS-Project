# Status: In Progress

# OSS-Project
 - 2026 대구대학교 오픈소스소프트웨어 팀 프로젝트 19조

# 1. 프로젝트 목적: "학교 공지 AI 요약 앱"
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

-웹 크롤링 1명
-서버&요약AI 1명
-앱 UI 1명
