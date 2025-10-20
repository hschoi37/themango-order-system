# 🚀 Railway 배포 완전 가이드

## 📋 준비된 파일들

### ✅ 웹 애플리케이션
- `app.py` - Flask 웹 서버
- `templates/index.html` - 웹 인터페이스
- `smart_excel_processor.py` - 엑셀 처리 로직

### ✅ 배포 설정
- `requirements.txt` - Python 의존성
- `Procfile` - Railway 실행 명령
- `railway.json` - Railway 설정
- `env.example` - 환경 변수 예시

## 🚀 배포 단계

### 1단계: GitHub 저장소 생성

```bash
# 현재 디렉토리에서
git init
git add .
git commit -m "Initial commit: The.Mango order management system"

# GitHub에서 새 저장소 생성 후
git remote add origin https://github.com/yourusername/themango-order-system.git
git branch -M main
git push -u origin main
```

### 2단계: Railway 배포

1. [Railway.app](https://railway.app) 접속
2. GitHub 계정으로 로그인
3. "New Project" → "Deploy from GitHub repo"
4. 저장소 선택
5. 자동 배포 시작

### 3단계: 환경 변수 설정

Railway 대시보드 → Variables 탭에서 설정:

```
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
GOOGLE_SPREADSHEET_ID=1FVDp3h0yveJO9_LrPxkuQcm7UBNEnGbwP9TMcRsoIFc
GOOGLE_SHEET_NAME=order
GOOGLE_TOKEN_FILE=token.pickle
```

### 4단계: OAuth 토큰 업로드

1. 로컬에서 `python oauth_setup.py` 실행
2. 생성된 `token.pickle` 파일을 Railway에 업로드
3. 또는 환경 변수로 설정

## 🌐 웹 인터페이스 기능

### ✅ 파일 업로드
- 드래그 앤 드롭 지원
- 클릭하여 파일 선택
- 지원 형식: .xlsx, .xls, .xltx, .htm, .html

### ✅ 실시간 상태 확인
- 구글 스프레드시트 연결 상태
- 현재 주문 수 표시
- 처리 결과 실시간 피드백

### ✅ 사용자 친화적 UI
- 반응형 디자인 (모바일 지원)
- Bootstrap 5 스타일링
- 로딩 인디케이터
- 성공/오류 메시지

## 🔧 문제 해결

### OAuth 인증 오류
```bash
# 로컬에서 토큰 재생성
python oauth_setup.py
```

### 파일 업로드 오류
- 파일 크기 16MB 이하 확인
- 지원 형식 확인
- 네트워크 연결 확인

### 구글 스프레드시트 연결 오류
- 스프레드시트 ID 확인
- 시트 이름 'order' 확인
- OAuth 토큰 유효성 확인

## 📱 사용법

1. Railway URL에 접속
2. 파일을 업로드 영역에 드래그
3. "업로드 및 처리" 클릭
4. 처리 완료 후 구글 스프레드시트 확인

## 🎯 장점

- ✅ **간편한 사용**: 웹 브라우저에서 바로 사용
- ✅ **자동 배포**: GitHub 푸시 시 자동 업데이트
- ✅ **확장성**: Railway의 자동 스케일링
- ✅ **보안**: 환경 변수로 민감한 정보 관리
- ✅ **모바일 지원**: 반응형 웹 디자인

이제 어디서든 웹 브라우저로 파일을 업로드하여 구글 스프레드시트를 자동으로 업데이트할 수 있습니다! 🎉
