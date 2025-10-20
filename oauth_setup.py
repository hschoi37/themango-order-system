#!/usr/bin/env python3
"""
OAuth 인증 설정 스크립트
서비스 계정 키 대신 OAuth를 사용하여 구글 스프레드시트에 접근
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

class OAuthSetup:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials_file = 'oauth_credentials.json'
        self.token_file = 'token.pickle'

    def create_oauth_credentials(self):
        """OAuth 클라이언트 ID 생성 가이드"""
        print("🔧 OAuth 클라이언트 ID 생성 방법:")
        print("=" * 50)
        print("1. Google Cloud Console에서 'API 및 서비스' > '사용자 인증 정보'로 이동")
        print("2. '사용자 인증 정보 만들기' > 'OAuth 클라이언트 ID' 클릭")
        print("3. 애플리케이션 유형: '데스크톱 애플리케이션' 선택")
        print("4. 이름: 'TheMango Automation' 입력")
        print("5. '만들기' 클릭")
        print("6. 다운로드된 JSON 파일을 'oauth_credentials.json'으로 이름 변경")
        print("7. 이 스크립트를 다시 실행하세요")
        print("=" * 50)

    def setup_oauth(self):
        """OAuth 인증 설정"""
        try:
            # OAuth 클라이언트 ID 파일 확인
            if not os.path.exists(self.credentials_file):
                self.create_oauth_credentials()
                return False

            # 기존 토큰 확인
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                
                # 토큰이 유효한지 확인
                if creds and creds.valid:
                    print("✅ 기존 OAuth 토큰이 유효합니다.")
                    return True
                
                # 토큰 갱신 시도
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(creds, token)
                    print("✅ OAuth 토큰이 갱신되었습니다.")
                    return True

            # 새 OAuth 플로우 시작
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.scopes)
            creds = flow.run_local_server(port=0)
            
            # 토큰 저장
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
            
            print("✅ OAuth 인증이 완료되었습니다!")
            return True

        except Exception as e:
            print(f"❌ OAuth 설정 중 오류 발생: {e}")
            return False

    def test_connection(self):
        """구글 스프레드시트 연결 테스트"""
        try:
            import gspread
            from google.auth.transport.requests import Request
            
            # 토큰 로드
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
            
            # gspread 인증
            gc = gspread.authorize(creds)
            
            # 스프레드시트 접근 테스트
            spreadsheet = gc.open_by_key('1FVDp3h0yveJO9_LrPxkuQcm7UBNEnGbwP9TMcRsoIFc')
            worksheet = spreadsheet.worksheet('order')
            
            print("✅ 구글 스프레드시트 연결 성공!")
            print(f"📊 스프레드시트 제목: {spreadsheet.title}")
            print(f"📋 시트 제목: {worksheet.title}")
            print(f"📈 현재 데이터 행 수: {len(worksheet.get_all_records())}")
            
            return True

        except Exception as e:
            print(f"❌ 연결 테스트 실패: {e}")
            return False

def main():
    """메인 함수"""
    print("🔐 OAuth 인증 설정 시작")
    print("=" * 50)
    
    oauth = OAuthSetup()
    
    # OAuth 설정
    if oauth.setup_oauth():
        print("\n🧪 연결 테스트 중...")
        if oauth.test_connection():
            print("\n🎉 OAuth 설정이 완료되었습니다!")
            print("이제 smart_excel_processor.py를 사용할 수 있습니다.")
        else:
            print("\n❌ 연결 테스트에 실패했습니다.")
    else:
        print("\n❌ OAuth 설정에 실패했습니다.")

if __name__ == "__main__":
    main()
