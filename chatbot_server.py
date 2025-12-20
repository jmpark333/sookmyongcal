from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from rag_system import get_rag_context
import logging
try:
    from zai import ZaiClient
except ImportError:
    from zai._client import ZaiClient

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Z.AI 클라이언트 초기화
client = ZaiClient(api_key="6e74659313a8456da1b4881d29dc098f.SgJrKDIG5qoTW9YO")

def generate_glm_response(prompt: str, context: str = "") -> str:
    """
    Z.AI SDK를 사용하여 GLM-4.6 모델 응답 생성
    """
    try:
        # 스트리밍 응답 생성
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
            stream=True
        )
        
        # 스트리밍 응답 수집
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        
        return full_response.strip()
            
    except Exception as e:
        logger.error(f"GLM 응답 생성 오류: {e}")
        return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"

@app.route('/')
def index():
    """
    메인 페이지
    """
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """
    챗봇 API 엔드포인트
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': '메시지가 없습니다.'}), 400
        
        user_message = data['message'].strip()
        
        # RAG 컨텍스트 검색
        context = get_rag_context(user_message)
        
        # GLM-4.6 모델로 응답 생성
        bot_response = generate_glm_response(user_message, context)
        
        return jsonify({
            'response': bot_response,
            'context_used': bool(context and context != "관련 정보를 찾을 수 없습니다.")
        })
        
    except Exception as e:
        logger.error(f"챗봇 처리 중 오류: {e}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@app.route('/health')
def health_check():
    """
    헬스 체크
    """
    return jsonify({'status': 'healthy', 'service': 'sookmyong-chatbot'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '페이지를 찾을 수 없습니다.'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

if __name__ == '__main__':
    # templates 디렉토리 생성
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 환경 변수에 따라 개발/프로덕션 환경 결정
    if os.environ.get('FLASK_ENV') == 'development':
        # 개발 환경에서 실행
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        # 프로덕션 환경에서 실행
        app.run()
