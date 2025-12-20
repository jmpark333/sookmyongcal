from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)


# JavaScript 방식의 간단한 챗봇 로직
def find_relevant_knowledge(query):
    """JavaScript knowledge_base.js 방식으로 관련 정보 찾기"""

    # knowledge_base.js 파일 읽기
    try:
        with open("output/knowledge_base.js", "r", encoding="utf-8") as f:
            content = f.read()
            # JavaScript에서 KNOWLEDGE_BASE 추출
            start = content.find("[")
            end = content.rfind("]") + 1
            knowledge_base_json = content[start:end]
            knowledge_base = json.loads(knowledge_base_json)
    except:
        return None

    query_lower = query.lower()
    best_match = None
    best_score = 0

    for item in knowledge_base:
        score = 0

        # 키워드 매칭
        for keyword in item["keywords"]:
            if keyword.lower() in query_lower:
                score += 2

        # 내용 매칭
        content_lower = item["content"].lower()
        for keyword in item["keywords"]:
            if keyword.lower() in content_lower:
                score += 1

        if score > best_score:
            best_score = score
            best_match = item

    return best_match if best_score > 0 else None


def generate_simple_response(query, knowledge):
    """간단한 응답 생성"""
    if not knowledge:
        return "안녕하세요! 숙명여자대학교 2026학년도 신입생 합격자 안내사항 전문 챗봇입니다. 등록금, 입학식, 영어배치고사, 기숙사, 신체검사, 오리엔테이션, 장학금, 수강신청, 영어 교양필수 이수면제 등에 대해 질문해 주세요."

    query_lower = query.lower()

    # 영어 교양필수 이수면제 관련 질문은 더 상세한 답변
    if knowledge["id"] == "영어교양필수이수면제" and any(
        keyword in query_lower
        for keyword in [
            "기준",
            "성적",
            "점수",
            "어떻게",
            "어떻게",
            "toeic",
            "toefl",
            "ielts",
            "인정",
        ]
    ):
        return f"""{knowledge["content"]}

💡 추가 안내:
• 구체적인 성적 기준은 학년도별로 다를 수 있습니다.
• 신청 방법과 제출 서류는 순헌칼리지 교학팀으로 문의해주세요.
• 기타 이수면제 관련 공지사항은 숙명여자대학교 공지사항을 참고해주세요."""

    return f"{knowledge['content']}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "메시지가 없습니다."}), 400

        user_message = data["message"].strip()

        # 간단한 키워드 매칭으로 응답
        knowledge = find_relevant_knowledge(user_message)
        bot_response = generate_simple_response(user_message, knowledge)

        return jsonify(
            {"response": bot_response, "context_used": knowledge is not None}
        )

    except Exception as e:
        return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "sookmyong-chatbot"})


if __name__ == "__main__":
    if not os.path.exists("templates"):
        os.makedirs("templates")

    app.run(debug=True, host="0.0.0.0", port=5000)
