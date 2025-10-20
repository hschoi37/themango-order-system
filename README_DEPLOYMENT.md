# The.Mango 주문 관리 시스템 - Railway 배포 가이드

## 🚀 Railway 배포 방법

### 1. GitHub 저장소 준비

1. 이 프로젝트를 GitHub 저장소에 푸시합니다:
```bash
git init
git add .
git commit -m "Initial commit: The.Mango order management system"
git branch -M main
git remote add origin https://github.com/yourusername/themango-order-system.git
git push -u origin main
```

### 2. Railway 계정 설정

1. [Railway.app](https://railway.app)에 가입합니다
2. GitHub 계정과 연결합니다

### 3. 프로젝트 배포

1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. GitHub 저장소 선택
4. 자동으로 배포가 시작됩니다

### 4. 환경 변수 설정

Railway 대시보드에서 다음 환경 변수들을 설정합니다:

#### 필수 환경 변수:
```
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
GOOGLE_SPREADSHEET_ID=1FVDp3h0yveJO9_LrPxkuQcm7UBNEnGbwP9TMcRsoIFc
GOOGLE_SHEET_NAME=order
```

#### OAuth 설정:
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-app-name.railway.app/auth/callback
```

### 5. Google OAuth 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. Google Sheets API와 Google Drive API 활성화
3. OAuth 2.0 클라이언트 ID 생성
4. 승인된 리디렉션 URI에 Railway URL 추가:
   - `https://your-app-name.railway.app/auth/callback`

### 6. OAuth 토큰 생성

로컬에서 OAuth 토큰을 생성합니다:

```bash
python oauth_setup.py
```

생성된 `token.pickle` 파일을 Railway에 업로드하거나, 환경 변수로 설정합니다.

## 🌐 웹 인터페이스 사용법

1. Railway에서 제공하는 URL에 접속합니다
2. 파일 업로드 영역에 엑셀 파일을 드래그하거나 클릭하여 선택합니다
3. "업로드 및 처리" 버튼을 클릭합니다
4. 처리 완료 후 구글 스프레드시트가 자동으로 업데이트됩니다

## 📁 지원 파일 형식

- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)
- `.xltx` (Excel 템플릿)
- `.htm`, `.html` (HTML 테이블)

## 🔧 문제 해결

### OAuth 인증 오류
- Google Cloud Console에서 OAuth 설정을 확인하세요
- 리디렉션 URI가 정확한지 확인하세요

### 파일 업로드 오류
- 파일 크기가 16MB를 초과하지 않는지 확인하세요
- 지원되는 파일 형식인지 확인하세요

### 구글 스프레드시트 연결 오류
- 스프레드시트 ID가 정확한지 확인하세요
- 시트 이름이 'order'인지 확인하세요
- OAuth 토큰이 유효한지 확인하세요

## 📞 지원

문제가 발생하면 GitHub Issues에 문의하세요.
