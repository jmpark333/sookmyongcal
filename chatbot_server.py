from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from rag_system import get_rag_context
import logging
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Z.AI API 설정
ZAI_API_KEY = "6e74659313a8456da1b4881d29dc098f.SgJrKDIG5qoTW9YO"
ZAI_API_URL = "https://api.z.ai/api/paas/v4/chat/completions"


def generate_glm_response(prompt: str, context: str = "") -> str:
    """
    Z.AI HTTP API를 사용하여 GLM-4.6 모델 응답 생성
    """
    try:
        headers = {
            "Authorization": f"Bearer {ZAI_API_KEY}",
            "Content-Type": "application/json",
            "Accept-Language": "ko-KR,ko",
        }

        system_prompt = """당신은 숙명여자대학교 2026학년도 신입생 합격자 안내사항 전문 챗봇입니다.
제공된 문맥 정보를 바탕으로 사용자의 질문에 정확하고 간결하게 답변해주세요.

답변 규칙:
1. 문맥 정보를 최대한 활용하여 답변하세요.
2. 질문에 대한 핵심 정보를 먼저 제공하세요.
3. 불필요한 분석이나 사고 과정은 제외하고 바로 답변하세요.
4. 1-3문장 이내로 간결하게 답변하세요.
5. 문맥에 정보가 없으면 "해당 정보는 문서에 없습니다. 담당 부서에 문의해주세요."라고 답변하세요."""

        messages = []
        if context and context != "관련 정보를 찾을 수 없습니다.":
            messages.append(
                {
                    "role": "system",
                    "content": f"{system_prompt}\n\n문서 정보:\n{context}",
                }
            )
        else:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": "glm-4.6",
            "messages": messages,
            "max_tokens": 200,
            "temperature": 0.1,
        }

        response = requests.post(ZAI_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()

        # 응답 디버깅
        logger.info(f"API 응답 상태: {response.status_code}")

        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]
            content = message.get("content", "")
            reasoning_content = message.get("reasoning_content", "")

            # content가 비어있으면 reasoning_content 사용
            final_content = content if content else reasoning_content

            if final_content:
                return final_content.strip()
            else:
                logger.warning("API 응답 내용이 비어있습니다.")
                return "죄송합니다. 응답을 받지 못했습니다. 잠시 후 다시 시도해주세요."
        else:
            logger.error(f"API 응답 형식 오류: {result}")
            return "죄송합니다. 응답 처리 중 오류가 발생했습니다."

    except Exception as e:
        logger.error(f"GLM 응답 생성 오류: {e}")
        return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"


@app.route("/")
def index():
    """
    메인 페이지
    """
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    챗봇 API 엔드포인트
    """
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "메시지가 없습니다."}), 400

        user_message = data["message"].strip()

        # RAG 컨텍스트 검색
        context = get_rag_context(user_message)

        # GLM-4.6 모델로 응답 생성
        bot_response = generate_glm_response(user_message, context)

        return jsonify(
            {
                "response": bot_response,
                "context_used": bool(
                    context and context != "관련 정보를 찾을 수 없습니다."
                ),
            }
        )

    except Exception as e:
        logger.error(f"챗봇 처리 중 오류: {e}")
        return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500


@app.route("/health")
def health_check():
    """
    헬스 체크
    """
    return jsonify({"status": "healthy", "service": "sookmyong-chatbot"})


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "페이지를 찾을 수 없습니다."}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500


if __name__ == "__main__":
    # templates 디렉토리 생성
    if not os.path.exists("templates"):
        os.makedirs("templates")

    # 환경 변수에 따라 개발/프로덕션 환경 결정
    if os.environ.get("FLASK_ENV") == "development":
        # 개발 환경에서 실행
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        # 프로덕션 환경에서 실행
        app.run()
