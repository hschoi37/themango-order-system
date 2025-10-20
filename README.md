# The.Mango 주문관리시스템 자동화

매일 오전 6시에 The.Mango 주문관리시스템에서 주문 데이터를 자동으로 다운로드하여 구글 스프레드시트에 업데이트하는 자동화 서비스입니다.

## 🚀 기능

- **자동 로그인**: The.Mango 관리자 계정으로 자동 로그인
- **데이터 업데이트**: 전체마켓 가져오기로 최신 주문 데이터 수집
- **엑셀 다운로드**: 주문 데이터를 엑셀 파일로 자동 다운로드
- **구글 스프레드시트 연동**: 다운로드한 데이터를 구글 스프레드시트에 자동 업데이트
- **스케줄링**: 매일 오전 6시 자동 실행

## 📋 데이터 구조

다음 22개 컬럼의 주문 데이터를 처리합니다:

1. 마켓아이디
2. 마켓주문일자
3. 마켓주문번호
4. 마켓명
5. 마켓상품명
6. 결제수량
7. 수령인명
8. 휴대폰번호
9. 배송주소
10. 상세주소
11. 통관고유부호
12. 국내송장번호 택배사
13. 국내송장번호
14. 구매사이트명
15. 더망고주문상태
16. 결제일자
17. 결제시간
18. 결제카드
19. 결제금액합계(원)
20. 구매가격
21. 국제운송료
22. 정산예정금액(원)

## 🛠️ 설치 및 설정

### 1. 저장소 클론 및 의존성 설치

```bash
# 저장소 클론
git clone <repository-url>
cd themango

# Python 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate  # Windows

# 자동 설정 실행
python setup.py
```

### 2. 구글 클라우드 설정

#### 2.1 Google Cloud Console에서 프로젝트 생성
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Google Sheets API와 Google Drive API 활성화

#### 2.2 서비스 계정 생성
1. IAM 및 관리자 > 서비스 계정으로 이동
2. "서비스 계정 만들기" 클릭
3. 서비스 계정 이름 입력 (예: "themango-automation")
4. 역할: "편집자" 또는 "소유자" 선택
5. "키 만들기" > "JSON" 선택하여 키 파일 다운로드

#### 2.3 서비스 계정 키 설정
1. 다운로드한 JSON 파일을 `google_credentials.json`으로 이름 변경
2. 프로젝트 루트 디렉토리에 저장

#### 2.4 구글 스프레드시트 공유
1. 대상 구글 스프레드시트 열기
2. "공유" 버튼 클릭
3. 서비스 계정 이메일 주소 추가 (편집 권한 부여)

### 3. 설정 확인

```bash
# 테스트 실행
python order_automation.py
```

## 📅 스케줄링 설정

### Mac/Linux (cron 사용)

```bash
# crontab 편집
crontab -e

# 매일 오전 6시 실행 (프로젝트 디렉토리에서)
0 6 * * * cd /path/to/themango && python order_automation.py
```

### Windows (작업 스케줄러)

1. 작업 스케줄러 열기
2. "기본 작업 만들기" 선택
3. 트리거: 매일 오전 6시
4. 동작: 프로그램 시작
5. 프로그램: `python`
6. 인수: `order_automation.py`
7. 시작 위치: 프로젝트 디렉토리

## 📁 프로젝트 구조

```
themango/
├── order_automation.py      # 메인 자동화 스크립트
├── setup.py                 # 설치 및 설정 스크립트
├── requirements.txt         # Python 의존성
├── google_credentials.json  # 구글 서비스 계정 키 (생성 필요)
├── downloads/               # 다운로드된 엑셀 파일 저장
├── logs/                    # 로그 파일 저장
└── README.md               # 이 파일
```

## 🔧 설정 옵션

`order_automation.py` 파일에서 다음 설정을 변경할 수 있습니다:

```python
class OrderAutomation:
    def __init__(self):
        self.login_url = "https://tmg4431.mycafe24.com/mall/admin/admin_login.php"
        self.username = "htag_hs"  # 로그인 아이디
        self.password = "Tm3705!"  # 로그인 비밀번호
        self.spreadsheet_id = "1FVDp3h0yveJO9_LrPxkuQcm7UBNEnGbwP9TMcRsoIFc"  # 구글 스프레드시트 ID
        self.sheet_name = "Sheet1"  # 시트 이름
```

## 📊 로그 확인

실행 로그는 다음 위치에서 확인할 수 있습니다:

- 콘솔 출력: 실시간 로그
- `order_automation.log`: 파일 로그
- `logs/` 디렉토리: 상세 로그

## ⚠️ 주의사항

1. **보안**: `google_credentials.json` 파일은 절대 공개 저장소에 커밋하지 마세요.
2. **네트워크**: 안정적인 인터넷 연결이 필요합니다.
3. **브라우저**: Playwright가 Chromium 브라우저를 사용합니다.
4. **권한**: 구글 스프레드시트에 대한 편집 권한이 필요합니다.

## 🐛 문제 해결

### 로그인 실패
- 아이디/비밀번호 확인
- 네트워크 연결 상태 확인
- 사이트 접근 제한 확인

### 구글 스프레드시트 업데이트 실패
- 서비스 계정 키 파일 확인
- 스프레드시트 공유 권한 확인
- Google Sheets API 활성화 확인

### 엑셀 다운로드 실패
- 브라우저 설정 확인
- 다운로드 권한 확인
- 파일 경로 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:

1. 로그 파일 확인
2. 네트워크 연결 상태
3. 구글 서비스 계정 설정
4. 스프레드시트 권한 설정

## 📝 라이선스

이 프로젝트는 개인 사용을 위한 자동화 도구입니다.
