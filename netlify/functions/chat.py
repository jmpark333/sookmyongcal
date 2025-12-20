import json
import os
import sys

# 현재 디렉토리를 Python 경로에 추가 (rag_system을 찾기 위함)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_system import get_rag_context
import logging
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Z.AI API 설정
ZAI_API_KEY = os.environ.get(
    "ZAI_API_KEY", "6e74659313a8456da1b4881d29dc098f.SgJrKDIG5qoTW9YO"
)
ZAI_API_URL = "https://api.z.ai/api/paas/v4/chat/completions"


def generate_glm_response(prompt: str, context: str = "") -> str:
    """
    Z.AI HTTP API를 사용하여 GLM-4.6 모델 응답 생성
    """
    try:
        headers = {
            "Authorization": f"Bearer {ZAI_API_KEY}",
            "Content-Type": "application/json",
            "Accept-Language": "en-US,en",
        }

        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": "glm-4.6",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.3,
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


def handler(event, context):
    """
    Netlify serverless function handler
    """
    try:
        # 요청 정보 추출
        method = event.get("httpMethod", event.get("method", "GET"))
        body = event.get("body", event.get("json", {}))
        if isinstance(body, str):
            body = json.loads(body)

        if method == "POST":
            # POST 요청 (채팅)

            if not body or "message" not in body:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "메시지가 없습니다."}),
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                }

            user_message = body["message"].strip()

            # RAG 컨텍스트 검색
            context = get_rag_context(user_message)

            # GLM-4.6 모델로 응답 생성
            bot_response = generate_glm_response(user_message, context)

            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "response": bot_response,
                        "context_used": bool(
                            context and context != "관련 정보를 찾을 수 없습니다."
                        ),
                    }
                ),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            }

        elif method == "GET":
            # GET 요청 (헬스 체크)
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"status": "healthy", "service": "sookmyong-chatbot"}
                ),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            }

        else:
            return {
                "statusCode": 405,
                "body": json.dumps({"error": "허용되지 않는 메소드입니다."}),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
            }

    except Exception as e:
        logger.error(f"처리 중 오류: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "서버 내부 오류가 발생했습니다."}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
        }


# 로컬 테스트용
if __name__ == "__main__":
    # 임베딩 생성 확인
    print("서버리스 함수 테스트")
    result = generate_glm_response("안녕하세요", "당신은 친절한 어시스턴트입니다")
    print(f"테스트 응답: {result}")
