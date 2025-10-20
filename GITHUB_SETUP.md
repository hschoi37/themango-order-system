# 🚀 GitHub 저장소 설정 및 Railway 배포 가이드

## 1단계: GitHub 저장소 생성

### 방법 1: GitHub 웹사이트에서 생성
1. [GitHub.com](https://github.com)에 로그인
2. "New repository" 클릭
3. 저장소 정보 입력:
   - **Repository name**: `themango-order-system`
   - **Description**: `The.Mango 주문 관리 시스템 - 웹 인터페이스로 엑셀 파일을 업로드하여 구글 스프레드시트를 자동 업데이트`
   - **Public** 선택
   - **Add a README file** 체크 해제 (이미 있음)
4. "Create repository" 클릭

### 방법 2: GitHub CLI 사용
```bash
# GitHub CLI 로그인
gh auth login

# 저장소 생성
gh repo create themango-order-system --public --description "The.Mango 주문 관리 시스템"
```

## 2단계: 로컬 저장소와 GitHub 연결

```bash
# GitHub 저장소 URL을 원격 저장소로 추가
git remote add origin https://github.com/yourusername/themango-order-system.git

# 메인 브랜치로 푸시
git push -u origin main
```

## 3단계: Railway 배포

### Railway 계정 설정
1. [Railway.app](https://railway.app) 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭
4. "Deploy from GitHub repo" 선택
5. `themango-order-system` 저장소 선택
6. 자동 배포 시작

### 환경 변수 설정
Railway 대시보드 → Variables 탭에서 다음 변수들을 설정:

```
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
GOOGLE_SPREADSHEET_ID=1FVDp3h0yveJO9_LrPxkuQcm7UBNEnGbwP9TMcRsoIFc
GOOGLE_SHEET_NAME=order
GOOGLE_TOKEN_FILE=token.pickle
```

### OAuth 토큰 업로드
1. 로컬에서 `python oauth_setup.py` 실행하여 `token.pickle` 생성
2. Railway 대시보드 → Files 탭에서 `token.pickle` 업로드

## 4단계: 배포 확인

1. Railway에서 제공하는 URL에 접속
2. 웹 인터페이스가 정상적으로 로드되는지 확인
3. 파일 업로드 테스트

## 🎯 완성된 기능들

- ✅ **웹 인터페이스**: 드래그 앤 드롭 파일 업로드
- ✅ **다양한 파일 형식 지원**: .xlsx, .xls, .xltx, .htm, .html
- ✅ **자동 정렬**: 신규 주문 우선, 마켓주문일자 최신순
- ✅ **실시간 상태 확인**: 구글 스프레드시트 연결 상태
- ✅ **반응형 디자인**: 모바일 지원
- ✅ **자동 배포**: GitHub 푸시 시 자동 업데이트

## 📱 사용법

1. Railway URL에 접속
2. 파일을 업로드 영역에 드래그
3. "업로드 및 처리" 버튼 클릭
4. 구글 스프레드시트 자동 업데이트 완료!

이제 어디서든 웹 브라우저로 파일을 업로드하여 주문 관리를 할 수 있습니다! 🎉
