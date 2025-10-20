#!/usr/bin/env python3
"""
The.Mango 주문 관리 웹 애플리케이션
Railway 배포용 Flask 웹 서버
"""

import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path
from smart_excel_processor import SmartExcelProcessor

# Flask 앱 설정
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 업로드 설정
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'xltx', 'htm', 'html'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 업로드 폴더 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """허용된 파일 확장자인지 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """파일 업로드 및 처리"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '파일이 선택되지 않았습니다.'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '파일이 선택되지 않았습니다.'})
        
        if file and allowed_file(file.filename):
            # 파일명 보안 처리
            filename = secure_filename(file.filename)
            
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{filename.split(".")[-1]}') as tmp_file:
                file.save(tmp_file.name)
                temp_file_path = tmp_file.name
            
            try:
                # 스마트 엑셀 프로세서로 처리
                processor = SmartExcelProcessor()
                result = processor.process_file(temp_file_path)
                
                if result:
                    return jsonify({
                        'success': True, 
                        'message': '파일이 성공적으로 처리되었습니다!',
                        'data': {
                            'total_orders': len(processor.get_existing_data_from_sheets() or []),
                            'file_name': filename
                        }
                    })
                else:
                    return jsonify({'success': False, 'message': '파일 처리 중 오류가 발생했습니다.'})
            
            finally:
                # 임시 파일 삭제
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        else:
            return jsonify({'success': False, 'message': '지원되지 않는 파일 형식입니다. (xlsx, xls, xltx, htm, html만 지원)'})
    
    except Exception as e:
        logger.error(f"파일 업로드 처리 중 오류: {e}")
        return jsonify({'success': False, 'message': f'서버 오류가 발생했습니다: {str(e)}'})

@app.route('/status')
def status():
    """시스템 상태 확인"""
    try:
        processor = SmartExcelProcessor()
        if processor.worksheet:
            records = processor.get_existing_data_from_sheets()
            return jsonify({
                'success': True,
                'status': 'connected',
                'total_orders': len(records) if records is not None else 0,
                'sheet_name': processor.sheet_name
            })
        else:
            return jsonify({
                'success': False,
                'status': 'disconnected',
                'message': '구글 스프레드시트에 연결할 수 없습니다.'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'message': f'상태 확인 중 오류: {str(e)}'
        })

@app.route('/health')
def health():
    """헬스 체크"""
    return jsonify({'status': 'healthy', 'service': 'themango-order-processor'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
