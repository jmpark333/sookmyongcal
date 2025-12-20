#!/usr/bin/env python3
import json
import os


def update_knowledge_base_with_english_exemption():
    """영어 교양필수 이수면제 관련 상세 정보 추가"""

    # 기존 knowledge_base.js 읽기
    js_file = "output/knowledge_base.js"

    try:
        with open(js_file, "r", encoding="utf-8") as f:
            content = f.read()

        # KNOWLEDGE_BASE 배열 찾기
        start = content.find("[")
        end = content.rfind("]") + 1
        knowledge_base_json = content[start:end]
        knowledge_base = json.loads(knowledge_base_json)

        # 영어 교양필수 이수면제 항목 추가
        english_exemption_item = {
            "id": "영어교양필수이수면제",
            "keywords": [
                "영어교양필수",
                "이수면제",
                "TOEIC",
                "TOEFL",
                "IELTS",
                "GELT",
                "공인영어",
                "성적기준",
            ],
            "content": "영어 교양필수 이수면제는 다음과 같습니다:\n• 공인영어시험 성적기준: TOEIC 850점, TOEFL iBT 89점, IELTS(A) 6.5점 이상인 경우 1과목 면제\n• 숙명여대학교 GELT 시험으로 대체 가능: GELT 성적에 따라 R, 1, 2, 3 레벨로 수업 진행\n• 신청 기간: 입학 후 1년 이내에만 신청 가능 (2026년 3월, 9월)\n• 신청 방법: 순헌칼리지 홈페이지 공지사항 확인 후 온라인 신청\n• 성적표 제출: 공인영어시험 성적표 제출 필요\n• 문의처: 순헌칼리지 교학팀 (행정관 201호, ☎ 2077-7511)\n• 참고: 자세한 기준은 매 학년도 다를 수 있으니 반드시 공지사항 확인",
        }

        # 기존 영어 관련 항목 찾아서 업데이트
        updated = False
        for i, item in enumerate(knowledge_base):
            if "영어" in item["id"] or "GELT" in item["id"]:
                # 기존 항목에 이수면제 정보 추가
                if "이수면제" not in item["content"]:
                    knowledge_base[i]["content"] += (
                        f"\n\n{english_exemption_item['content']}"
                    )
                    updated = True
                # 키워드도 확장
                if "이수면제" not in item["keywords"]:
                    knowledge_base[i]["keywords"].extend(
                        ["이수면제", "공인영어", "성적기준"]
                    )

        # 새로운 이수면제 항목이 없는 경우 추가
        if not any(item["id"] == "영어교양필수이수면제" for item in knowledge_base):
            knowledge_base.append(english_exemption_item)
            updated = True

        if updated:
            # JavaScript 파일로 저장
            js_content = "// 지식 베이스 데이터 (PDF에서 추출)\n"
            js_content += f"const KNOWLEDGE_BASE = {json.dumps(knowledge_base, ensure_ascii=False, indent=2)};\n\n"

            # 기존 함수들 추가
            js_content += """// 질문과 관련된 지식 베이스 항목 찾기
function findRelevantKnowledge(query) {
    const lowerQuery = query.toLowerCase();
    let bestMatch = null;
    let bestScore = 0;
    
    for (const item of KNOWLEDGE_BASE) {
        let score = 0;
        
        // 키워드 매칭
        for (const keyword of item.keywords) {
            if (lowerQuery.includes(keyword.toLowerCase())) {
                score += 2; // 키워드 매칭은 높은 점수
            }
        }
        
        // 내용 부분 매칭
        for (const keyword of item.keywords) {
            if (item.content.toLowerCase().includes(keyword.toLowerCase())) {
                score += 1;
            }
        }
        
        if (score > bestScore) {
            bestScore = score;
            bestMatch = item;
        }
    }
    
    return bestMatch && bestScore > 0 ? bestMatch : null;
}

// 지식 베이스 기반 응답 생성
function generateResponse(query, knowledge) {
    if (!knowledge) {
        return "안녕하세요! 숙명여자대학교 2026학년도 신입생 합격자 안내사항 전문 챗봇입니다. 등록금, 입학식, 영어배치고사, 기숙사, 신체검사, 오리엔테이션, 장학금, 수강신청, 영어 교양필수 이수면제 등에 대해 질문해 주세요.";
    }
    
    const lowerQuery = query.toLowerCase();
    
    // 질문 유형에 따라 응답 형식 조정
    if (lowerQuery.includes('언제') || lowerQuery.includes('일정') || lowerQuery.includes('기간')) {
        return `${knowledge.content}`;
    } else if (lowerQuery.includes('어떻게') || lowerQuery.includes('방법') || lowerQuery.includes('신청')) {
        return `${knowledge.content}`;
    } else {
        return `${knowledge.content}`;
    }
}
"""

            # 파일 저장
            with open(js_file, "w", encoding="utf-8") as f:
                f.write(js_content)

            # output 디렉토리에도 복사
            os.makedirs("output", exist_ok=True)
            with open("output/knowledge_base.js", "w", encoding="utf-8") as f:
                f.write(js_content)

            print(
                "✅ knowledge_base.js가 영어 교양필수 이수면제 정보로 업데이트되었습니다."
            )
            print("📋 추가된 정보:")
            print("   - 공인영어시험 성적기준 (TOEIC 850, TOEFL 89, IELTS 6.5)")
            print("   - GELT 대체 방법 및 레벨 안내")
            print("   - 신청 기간: 입학 후 1년 이내")
            print("   - 문의처 정보 (순헌칼리지 교학팀)")

        else:
            print("ℹ️ 이미 최신 정보가 포함되어 있습니다.")

    except Exception as e:
        print(f"❌ 업데이트 중 오류 발생: {e}")


if __name__ == "__main__":
    update_knowledge_base_with_english_exemption()
