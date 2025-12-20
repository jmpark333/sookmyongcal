import fitz  # PyMuPDF
import re
import json
from typing import List, Dict
import os


def extract_pdf_text_from_file(pdf_path: str) -> str:
    """
    로컬 PDF 파일에서 텍스트 내용을 추출합니다.
    """
    try:
        text = ""

        # PyMuPDF (fitz) 사용
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()
            if page_text:
                text += page_text + "\n"
        doc.close()

        if text.strip():
            print(f"PyMuPDF로 텍스트 추출 성공: {len(text)} 문자")
            return text.strip()
        else:
            print("텍스트 추출 결과가 비어있습니다.")
            return ""

    except Exception as e:
        print(f"PDF 처리 중 오류 발생: {e}")
        return ""


def clean_text(text: str) -> str:
    """
    추출된 텍스트를 정제합니다.
    """
    # 널문자 제거
    text = re.sub(r"\x00", "", text)

    # 여러 공백을 하나로
    text = re.sub(r"\s+", " ", text)

    # 줄바꿈 정리
    text = re.sub(r"\n+", "\n", text)

    # 불필요한 특수문자 정리 (한글, 영문, 숫자, 기본 구두점 유지)
    text = re.sub(r"[^\w\sㄱ-ㅎㅏ-ㅣ가-힣\.\,\:\-\(\)\[\]\/\?\!\%\$\'\n]", "", text)

    return text.strip()


def extract_sections(text: str) -> List[Dict]:
    """
    텍스트에서 섹션별로 내용을 추출합니다.
    """
    sections = []

    # 기본 키워드 기반으로 내용 분류
    keywords = {
        "등록금": ["등록금", "납부", "고지서", "가상계좌", "신한은행"],
        "영어배치고사": ["영어배치고사", "GELT", "배치고사", "접수", "응시"],
        "신체검사": ["신체검사", "건강검사", "흉부X선", "B형간염", "보건의료센터"],
        "입학식": ["입학식", "신입생환영회", "환영회"],
        "오리엔테이션": ["오리엔테이션", "신입생오리엔테이션"],
        "기숙사": ["기숙사", "생활관", "명재관", "입사"],
        "장학금": ["장학금", "장학", "순헌", "청파", "매화", "국가장학금"],
        "수강신청": ["수강신청", "수강", "신청"],
        "학자금대출": ["학자금대출", "대출", "정부보증"],
        "도서관": ["도서관", "대출", "이용"],
        "영어교양필수이수면제": [
            "영어",
            "교양필수",
            "이수면제",
            "TOEIC",
            "TOEFL",
            "IELTS",
            "토플",
            "아이엘츠",
        ],
    }

    # 각 키워드에 해당하는 내용 추출
    for section_name, section_keywords in keywords.items():
        content_parts = []

        # 문장 단위로 분리
        sentences = re.split(r"[.!?]\s*", text)

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and any(keyword in sentence for keyword in section_keywords):
                content_parts.append(sentence)

        if content_parts:
            content = ". ".join(content_parts)
            if len(content) > 1000:  # 너무 길면 자르기
                content = content[:1000] + "..."

            sections.append({"title": section_name, "content": content})

    # 섹션을 찾지 못하면 전체 텍스트에서 기본 정보만 추출
    if not sections:
        # 날짜 정보 추출
        date_pattern = r"(\d{4}\.?\s*\d{1,2}\.?\s*\d{1,2}\.?\s*[\(]?\s*[월화수목금토일]\s*[\)]?\s*)"
        dates = re.findall(date_pattern, text)

        if dates:
            content = f"주요 일정: {', '.join(dates[:5])}"  # 상위 5개 날짜
            sections.append({"title": "일정", "content": content})

    return sections


def create_knowledge_base_js(sections: List[Dict]):
    """
    JavaScript 형식의 knowledge_base.js 파일 생성
    """
    knowledge_items = []

    for section in sections:
        # 키워드 추출
        title = section["title"]
        content = section["content"]

        # 기본 키워드 설정
        keyword_mapping = {
            "등록금": ["등록금", "납부", "등록", "고지서"],
            "영어배치고사": ["영어배치고사", "영어", "배치고사", "GELT"],
            "신체검사": ["신체검사", "검사", "건강검사"],
            "입학식": ["입학식", "환영회", "입학", "식"],
            "오리엔테이션": ["오리엔테이션", "신입생오리엔테이션", "입학"],
            "기숙사": ["기숙사", "생활관", "명재관", "입사"],
            "장학금": ["장학금", "장학", "지원"],
            "수강신청": ["수강신청", "수강", "신청"],
            "학자금대출": ["학자금", "대출", "정부보증"],
            "도서관": ["도서관", "대출", "이용"],
            "일정": ["일정", "언제", "날짜"],
        }

        keywords = keyword_mapping.get(title, [title])

        knowledge_items.append({"id": title, "keywords": keywords, "content": content})

    # JavaScript 파일로 저장
    js_content = "// 지식 베이스 데이터 (PDF에서 추출)\n"
    js_content += (
        "const KNOWLEDGE_BASE = "
        + json.dumps(knowledge_items, ensure_ascii=False, indent=2)
        + ";\n\n"
    )

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
        return "안녕하세요! 숙명여자대학교 2026학년도 신입생 합격자 안내사항 전문 챗봇입니다. 등록금, 입학식, 영어배치고사, 기숙사, 신체검사, 오리엔테이션, 장학금, 수강신청 등에 대해 질문해 주세요.";
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

    with open("knowledge_base.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    # output 디렉토리에도 복사
    os.makedirs("output", exist_ok=True)
    with open("output/knowledge_base.js", "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"knowledge_base.js 파일이 생성되었습니다.")
    print(f"총 {len(knowledge_items)}개의 섹션이 포함되었습니다.")


def create_rag_knowledge_base(sections: List[Dict]):
    """
    RAG 시스템용 JSON 지식 베이스 생성
    """
    knowledge_base = []

    for i, section in enumerate(sections):
        # 각 섹션을 더 작은 청크로 분할
        content = section["content"]
        chunk_size = 500
        chunks = [
            content[i : i + chunk_size] for i in range(0, len(content), chunk_size)
        ]

        for j, chunk in enumerate(chunks):
            if chunk.strip():
                knowledge_base.append(
                    {
                        "id": f"section_{i}_chunk_{j}",
                        "title": section["title"],
                        "content": chunk.strip(),
                        "metadata": {
                            "section_index": i,
                            "chunk_index": j,
                            "total_chunks": len(chunks),
                        },
                    }
                )

    with open("knowledge_base.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

    print(f"knowledge_base.json 파일이 생성되었습니다.")
    print(f"총 {len(knowledge_base)}개의 청크가 생성되었습니다.")


if __name__ == "__main__":
    pdf_path = "2026학년도신입생합격자안내사항(20251212).pdf"

    print("PDF 파일에서 텍스트 추출 중...")
    raw_text = extract_pdf_text_from_file(pdf_path)

    if raw_text:
        print("텍스트 전처리 중...")
        cleaned_text = clean_text(raw_text)

        print("섹션 분석 중...")
        sections = extract_sections(cleaned_text)

        print("JavaScript 지식 베이스 생성 중...")
        create_knowledge_base_js(sections)

        print("RAG 지식 베이스 생성 중...")
        create_rag_knowledge_base(sections)

        print("처리 완료!")
        print(f"추출된 텍스트 길이: {len(raw_text)} 문자")
        print(f"생성된 섹션 수: {len(sections)}")

        # 일부 내용 샘플 출력
        print("\n=== 추출된 내용 샘플 ===")
        for section in sections[:3]:
            print(f"\n[{section['title']}]")
            print(
                section["content"][:200] + "..."
                if len(section["content"]) > 200
                else section["content"]
            )
    else:
        print("PDF 텍스트 추출에 실패했습니다.")
