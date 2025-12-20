from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from rag_system import get_rag_context
import logging
from zai import ZaiClient

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
        # 시스템 프롬프트와 컨텍스트 결합
        system_prompt = """당신은 숙명여자대학교 2026학년도 신입생 합격자 안내사항 전문 챗봇입니다.
다음 지침을 반드시 따라주세요:

1. 제공된 컨텍스트 정보를 기반으로 답변하세요.
2. 컨텍스트에 정보가 없는 경우, "해당 정보는 제공된 자료에 없습니다. 입학처나 관련 부서에 직접 문의해주세요."라고 답변하세요.
3. 항상 정중하고 친절한 말투를 사용하세요.
4. 신입생에게 꼭 필요한 정보를 우선적으로 제공하세요.
5. 구체적인 날짜, 시간, 장소, 연락처 등을 정확하게 전달하세요.
6. 필요한 경우 관련 부서의 연락처를 안내하세요.

컨텍스트 정보:
""" + context

        # Z.AI SDK를 사용한 챗 완료 생성
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        # 응답 추출
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            logger.error(f"API 응답 형식 오류: {response}")
            return "죄송합니다. 응답 처리 중 오류가 발생했습니다."
            
    except Exception as e:
        logger.error(f"응답 생성 중 오류: {e}")
        return "죄송합니다. 응답 처리 중 오류가 발생했습니다."

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
        
        if not user_message:
            return jsonify({'error': '메시지가 비어있습니다.'}), 400
        
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
    헬스 체크 엔드포인트
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
    
    # 개발 모드에서 실행
    app.run(debug=True, host='0.0.0.0', port=5000)