#!/usr/bin/env python3
"""
스마트 엑셀 파일 처리 및 구글 스프레드시트 업데이트 시스템
매일 다운로드한 엑셀 파일을 분석하여 신규/변경 데이터를 구글 스프레드시트에 업데이트
"""

import os
import sys
import logging
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
import json
import hashlib

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_excel_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartExcelProcessor:
    def __init__(self):
        self.spreadsheet_id = os.environ.get('GOOGLE_SPREADSHEET_ID', "1FVDp3h0yveJO9_LrPxkuQcm7UBNEnGbwP9TMcRsoIFc")
        self.sheet_name = os.environ.get('GOOGLE_SHEET_NAME', "order")
        
        # 구글 스프레드시트 컬럼 구조 (22개 컬럼)
        self.columns = [
            "마켓아이디", "마켓주문일자", "마켓주문번호", "마켓명", "마켓상품명",
            "결제수량", "수령인명", "휴대폰번호", "배송주소", "상세주소",
            "통관고유부호", "국내송장번호 택배사", "국내송장번호", "구매사이트명",
            "더망고주문상태", "결제일자", "결제시간", "결제카드", "결제금액합계(원)",
            "구매가격", "국제운송료", "정산예정금액(원)"
        ]
        
        # 데이터 저장 디렉토리
        self.data_dir = Path("./data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 상태 파일 경로
        self.state_file = self.data_dir / "last_processed.json"
        
        # 구글 스프레드시트 연결
        self.worksheet = self.setup_google_sheets()

    def setup_google_sheets(self):
        """구글 스프레드시트 API 설정"""
        try:
            # 1. 서비스 계정 키 시도
            service_account_file = "google_credentials.json"
            if os.path.exists(service_account_file):
                try:
                    scope = [
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                    credentials = Credentials.from_service_account_file(service_account_file, scopes=scope)
                    gc = gspread.authorize(credentials)
                    logger.info("서비스 계정 키로 구글 스프레드시트 연결 성공!")
                except Exception as e:
                    logger.warning(f"서비스 계정 키 연결 실패: {e}")
                    gc = None
            else:
                gc = None
            
            # 2. OAuth 인증 시도 (서비스 계정 키 실패 시)
            if gc is None:
                try:
                    import pickle
                    import base64
                    from google.auth.transport.requests import Request
                    
                    # 환경 변수에서 Base64 토큰 확인
                    token_base64 = os.environ.get('GOOGLE_TOKEN_BASE64')
                    if token_base64:
                        # Base64 토큰을 디코딩하여 사용
                        token_data = base64.b64decode(token_base64)
                        credentials = pickle.loads(token_data)
                        
                        # 토큰 갱신 시도
                        if credentials and credentials.expired and credentials.refresh_token:
                            credentials.refresh(Request())
                        
                        gc = gspread.authorize(credentials)
                        logger.info("OAuth 인증으로 구글 스프레드시트 연결 성공! (Base64 토큰 사용)")
                    else:
                        # 기존 파일 방식 시도
                        token_file = os.environ.get('GOOGLE_TOKEN_FILE', 'token.pickle')
                        
                        if os.path.exists(token_file):
                            with open(token_file, 'rb') as token:
                                credentials = pickle.load(token)
                            
                            # 토큰 갱신 시도
                            if credentials and credentials.expired and credentials.refresh_token:
                                credentials.refresh(Request())
                                with open(token_file, 'wb') as token:
                                    pickle.dump(credentials, token)
                            
                            gc = gspread.authorize(credentials)
                            logger.info("OAuth 인증으로 구글 스프레드시트 연결 성공! (파일 토큰 사용)")
                        else:
                            logger.error("인증 파일을 찾을 수 없습니다. oauth_setup.py를 실행하거나 환경 변수를 설정하세요.")
                            return None
                    
                except Exception as e:
                    logger.error(f"OAuth 인증 실패: {e}")
                    logger.error("oauth_setup.py를 실행하여 OAuth 인증을 설정하세요.")
                    return None
            
            # 스프레드시트 열기
            spreadsheet = gc.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(self.sheet_name)
            
            logger.info("구글 스프레드시트 연결 성공!")
            return worksheet
            
        except Exception as e:
            logger.error(f"구글 스프레드시트 설정 중 오류 발생: {e}")
            return None

    def find_latest_excel_file(self):
        """가장 최근의 엑셀 파일 찾기"""
        try:
            # 현재 디렉토리에서 엑셀 파일 찾기
            excel_files = []
            
            # .xlsx, .xls, .xltx 파일 찾기
            for ext in ['*.xlsx', '*.xls', '*.xltx']:
                excel_files.extend(Path('.').glob(ext))
            
            if not excel_files:
                logger.error("엑셀 파일을 찾을 수 없습니다.")
                return None
            
            # 가장 최근 파일 선택
            latest_file = max(excel_files, key=os.path.getctime)
            logger.info(f"최신 엑셀 파일 발견: {latest_file}")
            return latest_file
            
        except Exception as e:
            logger.error(f"엑셀 파일 찾기 중 오류 발생: {e}")
            return None

    def read_excel_file(self, file_path):
        """엑셀 파일 읽기 및 데이터 정리"""
        try:
            # 파일 형식 확인
            file_ext = Path(file_path).suffix.lower()
            
            # HTML 파일인지 확인
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('<html') or first_line.startswith('<!DOCTYPE') or first_line.startswith('<head>'):
                    logger.info("HTML 파일을 감지했습니다. HTML 테이블을 읽습니다.")
                    # HTML 테이블 읽기 (첫 번째 행을 헤더로 사용)
                    df = pd.read_html(file_path, encoding='utf-8', header=0)[0]
                else:
                    # 엑셀 파일 읽기 (파일 확장자에 따라 엔진 지정)
                    if file_ext == '.xls':
                        df = pd.read_excel(file_path, engine='xlrd')
                    elif file_ext == '.xlsx':
                        df = pd.read_excel(file_path, engine='openpyxl')
                    else:
                        # 기본적으로 모든 엔진을 시도
                        try:
                            df = pd.read_excel(file_path, engine='openpyxl')
                        except:
                            df = pd.read_excel(file_path, engine='xlrd')
            
            logger.info(f"엑셀 파일 읽기 완료: {len(df)}행, {len(df.columns)}열")
            logger.info(f"컬럼명: {list(df.columns)}")
            
            # 컬럼명 정리 (필요시)
            if len(df.columns) != len(self.columns):
                logger.warning(f"컬럼 수가 일치하지 않습니다. 예상: {len(self.columns)}, 실제: {len(df.columns)}")
                
                # 컬럼명 매핑 시도
                if len(df.columns) >= len(self.columns):
                    df = df.iloc[:, :len(self.columns)]
                    df.columns = self.columns
                else:
                    logger.error("컬럼 수가 부족합니다.")
                    return None
            
            # 데이터 정리
            df = df.fillna('')  # 빈 값 처리
            
            # 금액 관련 컬럼을 숫자로 변환
            amount_columns = ['결제수량', '결제금액합계(원)', '구매가격', '국제운송료', '정산예정금액(원)']
            for col in amount_columns:
                if col in df.columns:
                    # 문자열에서 숫자만 추출하여 변환
                    df[col] = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # NaN 값을 0으로 변경
                    df[col] = df[col].fillna(0)
                    logger.info(f"금액 컬럼 '{col}'을 숫자 형식으로 변환했습니다.")
            
            # 나머지 컬럼은 문자열로 변환
            for col in df.columns:
                if col not in amount_columns:
                    df[col] = df[col].astype(str)
            
            # 고유 키 생성 (마켓주문번호 + 마켓명)
            df['unique_key'] = df['마켓주문번호'].astype(str) + '_' + df['마켓명'].astype(str)
            
            # 데이터 해시 생성 (변경 감지용)
            df['data_hash'] = df.apply(lambda row: hashlib.md5(str(row).encode()).hexdigest(), axis=1)
            
            logger.info(f"데이터 정리 완료: {len(df)}행")
            return df
            
        except Exception as e:
            logger.error(f"엑셀 파일 읽기 중 오류 발생: {e}")
            return None

    def get_existing_data_from_sheets(self):
        """구글 스프레드시트에서 기존 데이터 가져오기"""
        try:
            if not self.worksheet:
                logger.error("구글 스프레드시트 연결이 없습니다.")
                return None
            
            # 모든 데이터 가져오기
            all_data = self.worksheet.get_all_records()
            
            if not all_data:
                logger.info("구글 스프레드시트에 데이터가 없습니다.")
                return pd.DataFrame()
            
            # DataFrame으로 변환
            df = pd.DataFrame(all_data)
            
            # 고유 키 생성
            df['unique_key'] = df['마켓주문번호'].astype(str) + '_' + df['마켓명'].astype(str)
            
            # 데이터 해시 생성
            df['data_hash'] = df.apply(lambda row: hashlib.md5(str(row).encode()).hexdigest(), axis=1)
            
            logger.info(f"구글 스프레드시트에서 기존 데이터 가져오기 완료: {len(df)}행")
            return df
            
        except Exception as e:
            logger.error(f"구글 스프레드시트 데이터 가져오기 중 오류 발생: {e}")
            return None

    def compare_data(self, new_df, existing_df):
        """새 데이터와 기존 데이터 비교"""
        try:
            if existing_df.empty:
                logger.info("기존 데이터가 없으므로 모든 데이터를 신규로 처리합니다.")
                return new_df, pd.DataFrame(), pd.DataFrame()
            
            # 신규 데이터 찾기 (unique_key가 기존 데이터에 없는 경우)
            new_keys = set(new_df['unique_key'])
            existing_keys = set(existing_df['unique_key'])
            
            new_orders = new_df[new_df['unique_key'].isin(new_keys - existing_keys)]
            
            # 기존 데이터와 교집합인 데이터
            common_keys = new_keys & existing_keys
            common_new = new_df[new_df['unique_key'].isin(common_keys)]
            common_existing = existing_df[existing_df['unique_key'].isin(common_keys)]
            
            # 변경된 데이터 찾기 (unique_key는 같지만 data_hash가 다른 경우)
            updated_orders = []
            for key in common_keys:
                new_row = common_new[common_new['unique_key'] == key].iloc[0]
                existing_row = common_existing[common_existing['unique_key'] == key].iloc[0]
                
                if new_row['data_hash'] != existing_row['data_hash']:
                    updated_orders.append(new_row)
            
            updated_df = pd.DataFrame(updated_orders) if updated_orders else pd.DataFrame()
            
            # 기존 데이터에서 제거되지 않은 데이터 (유지할 데이터)
            remaining_keys = existing_keys - new_keys
            remaining_df = existing_df[existing_df['unique_key'].isin(remaining_keys)]
            
            logger.info(f"데이터 비교 완료:")
            logger.info(f"  - 신규 주문: {len(new_orders)}건")
            logger.info(f"  - 변경된 주문: {len(updated_df)}건")
            logger.info(f"  - 유지되는 주문: {len(remaining_df)}건")
            
            return new_orders, updated_df, remaining_df
            
        except Exception as e:
            logger.error(f"데이터 비교 중 오류 발생: {e}")
            return None, None, None

    def update_google_sheets(self, new_orders, updated_orders, remaining_orders):
        """구글 스프레드시트 업데이트 (신규 주문 우선, 마켓주문일자 최신순)"""
        try:
            if not self.worksheet:
                logger.error("구글 스프레드시트 연결이 없습니다.")
                return False
            
            # 기존 데이터 모두 지우기
            self.worksheet.clear()
            
            # 헤더 추가
            self.worksheet.append_row(self.columns)
            
            # 데이터 추가 순서: 신규 → 변경된 → 유지되는 (각 그룹 내에서 마켓주문일자 최신순)
            all_data = []
            
            # 1. 신규 데이터 추가 (맨 위에, 마켓주문일자 최신순)
            if not new_orders.empty:
                # 마켓주문일자를 datetime으로 변환 후 최신순으로 정렬
                new_orders_copy = new_orders.copy()
                new_orders_copy['마켓주문일자'] = pd.to_datetime(new_orders_copy['마켓주문일자'], errors='coerce')
                new_orders_sorted = new_orders_copy.sort_values('마켓주문일자', ascending=False, na_position='last')
                logger.info(f"신규 주문 {len(new_orders)}건을 맨 위에 추가합니다. (마켓주문일자 최신순)")
                for _, row in new_orders_sorted.iterrows():
                    data_row = [row[col] for col in self.columns]
                    # datetime을 문자열로 변환
                    if '마켓주문일자' in self.columns:
                        date_idx = self.columns.index('마켓주문일자')
                        if pd.notna(data_row[date_idx]):
                            data_row[date_idx] = str(data_row[date_idx])
                    all_data.append(data_row)
            
            # 2. 변경된 데이터 추가 (마켓주문일자 최신순)
            if not updated_orders.empty:
                # 마켓주문일자를 datetime으로 변환 후 최신순으로 정렬
                updated_orders_copy = updated_orders.copy()
                updated_orders_copy['마켓주문일자'] = pd.to_datetime(updated_orders_copy['마켓주문일자'], errors='coerce')
                updated_orders_sorted = updated_orders_copy.sort_values('마켓주문일자', ascending=False, na_position='last')
                logger.info(f"변경된 주문 {len(updated_orders)}건을 추가합니다. (마켓주문일자 최신순)")
                for _, row in updated_orders_sorted.iterrows():
                    data_row = [row[col] for col in self.columns]
                    # datetime을 문자열로 변환
                    if '마켓주문일자' in self.columns:
                        date_idx = self.columns.index('마켓주문일자')
                        if pd.notna(data_row[date_idx]):
                            data_row[date_idx] = str(data_row[date_idx])
                    all_data.append(data_row)
            
            # 3. 유지되는 데이터 추가 (맨 아래에, 마켓주문일자 최신순)
            if not remaining_orders.empty:
                # 마켓주문일자를 datetime으로 변환 후 최신순으로 정렬
                remaining_orders_copy = remaining_orders.copy()
                remaining_orders_copy['마켓주문일자'] = pd.to_datetime(remaining_orders_copy['마켓주문일자'], errors='coerce')
                remaining_orders_sorted = remaining_orders_copy.sort_values('마켓주문일자', ascending=False, na_position='last')
                logger.info(f"유지되는 주문 {len(remaining_orders)}건을 추가합니다. (마켓주문일자 최신순)")
                for _, row in remaining_orders_sorted.iterrows():
                    data_row = [row[col] for col in self.columns]
                    # datetime을 문자열로 변환
                    if '마켓주문일자' in self.columns:
                        date_idx = self.columns.index('마켓주문일자')
                        if pd.notna(data_row[date_idx]):
                            data_row[date_idx] = str(data_row[date_idx])
                    all_data.append(data_row)
            
            # 구글 스프레드시트에 일괄 추가
            if all_data:
                self.worksheet.append_rows(all_data)
                logger.info(f"구글 스프레드시트 업데이트 완료: {len(all_data)}행")
                logger.info("데이터 순서: 신규 주문(최신순) → 변경된 주문(최신순) → 유지되는 주문(최신순)")
            
            return True
            
        except Exception as e:
            logger.error(f"구글 스프레드시트 업데이트 중 오류 발생: {e}")
            return False

    def save_processing_state(self, file_path, processed_count):
        """처리 상태 저장"""
        try:
            state = {
                "last_processed_file": str(file_path),
                "last_processed_time": datetime.now().isoformat(),
                "processed_count": processed_count
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            logger.info(f"처리 상태 저장 완료: {self.state_file}")
            
        except Exception as e:
            logger.error(f"처리 상태 저장 중 오류 발생: {e}")

    def process_excel_file(self, file_path=None):
        """엑셀 파일 처리 메인 함수"""
        try:
            logger.info("=== 스마트 엑셀 파일 처리 시작 ===")
            
            # 1. 엑셀 파일 찾기
            if file_path is None:
                excel_file = self.find_latest_excel_file()
                if not excel_file:
                    return False
            else:
                excel_file = Path(file_path)
                if not excel_file.exists():
                    logger.error(f"지정된 파일이 존재하지 않습니다: {file_path}")
                    return False
            
            # 2. 엑셀 파일 읽기
            new_data = self.read_excel_file(excel_file)
            if new_data is None:
                return False
            
            # 3. 기존 데이터 가져오기
            existing_data = self.get_existing_data_from_sheets()
            if existing_data is None:
                return False
            
            # 4. 데이터 비교
            new_orders, updated_orders, remaining_orders = self.compare_data(new_data, existing_data)
            if new_orders is None:
                return False
            
            # 5. 구글 스프레드시트 업데이트
            success = self.update_google_sheets(new_orders, updated_orders, remaining_orders)
            if not success:
                return False
            
            # 6. 처리 상태 저장
            total_processed = len(new_orders) + len(updated_orders)
            self.save_processing_state(excel_file, total_processed)
            
            logger.info("=== 스마트 엑셀 파일 처리 완료 ===")
            return True
            
        except Exception as e:
            logger.error(f"엑셀 파일 처리 중 오류 발생: {e}")
            return False

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="스마트 엑셀 파일 처리 및 구글 스프레드시트 업데이트")
    parser.add_argument("--file", "-f", help="처리할 엑셀 파일 경로 (지정하지 않으면 최신 파일 자동 선택)")
    
    args = parser.parse_args()
    
    processor = SmartExcelProcessor()
    
    if processor.worksheet is None:
        print("❌ 구글 스프레드시트 연결 실패!")
        print("   google_credentials.json 파일을 확인하세요.")
        sys.exit(1)
    
    success = processor.process_excel_file(args.file)
    
    if success:
        print("✅ 엑셀 파일 처리 성공!")
        sys.exit(0)
    else:
        print("❌ 엑셀 파일 처리 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main()
