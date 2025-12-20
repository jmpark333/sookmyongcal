import requests
import re
import json
from typing import List, Dict
import os
import subprocess
import sys
import fitz  # PyMuPDF


def extract_pdf_text_from_url(pdf_url: str) -> str:
    """
    PDF URL에서 텍스트 내용을 추출합니다. 여러 방법을 시도합니다.
    """
    try:
        # PDF 다운로드
        response = requests.get(pdf_url)
        response.raise_for_status()

        # 파일로 저장
        pdf_path = "temp_pdf.pdf"
        with open(pdf_path, "wb") as f:
            f.write(response.content)

        text = ""

        # 방법 1: PyMuPDF (fitz) 사용 - 가장 강력한 한글 지원
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    text += page_text + "\n"
            doc.close()

            if text.strip():
                print("PyMuPDF로 텍스트 추출 성공")
                os.remove(pdf_path)
                return text.strip()

        except Exception as e:
            print(f"PyMuPDF 추출 실패: {e}")

        # 방법 2: pdfplumber 사용
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            if text.strip():
                print("pdfplumber로 텍스트 추출 성공")
                os.remove(pdf_path)
                return text.strip()

        except ImportError:
            print("pdfplumber가 설치되지 않았습니다. 다른 방법을 시도합니다.")
        except Exception as e:
            print(f"pdfplumber 추출 실패: {e}")

        # 방법 3: pdftotext 사용 (시스템 명령어)
        try:
            result = subprocess.run(
                ["pdftotext", pdf_path, "-"],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout
                print("pdftotext로 텍스트 추출 성공")
                os.remove(pdf_path)
                return text.strip()
        except FileNotFoundError:
            print("pdftotext가 설치되지 않았습니다. 다른 방법을 시도합니다.")
        except Exception as e:
            print(f"pdftotext 추출 실패: {e}")

        # 방법 4: PyPDF2 사용 (기존 방법)
        try:
            import PyPDF2

            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            if text.strip():
                print("PyPDF2로 텍스트 추출 성공")
                os.remove(pdf_path)
                return text.strip()

        except Exception as e:
            print(f"PyPDF2 추출 실패: {e}")

        # 임시 파일 삭제
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        return text.strip()

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

    # 불필요한 특수문자 정리
    text = re.sub(r"[^\w\sㄱ-ㅎㅏ-ㅣ가-힣\.\,\:\-\(\)\[\]\/]", " ", text)

    # 문단 구분
    text = re.sub(r"\n\s*\n", "\n\n", text)

    return text.strip()


def preprocess_text(text: str) -> List[Dict]:
    """
    추출된 텍스트를 전처리하여 문서 단위로 분할합니다.
    """
    # 텍스트 정제
    text = clean_text(text)

    # 문서를 섹션으로 분할
    sections = []
    current_section = ""
    current_title = ""

    lines = text.split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 제목 패턴 감지 (예: "1. 입학 절차", "가. 등록금 납부")
        if re.match(r"^[0-9가-힣]+\.\s+", line) or re.match(
            r"^[가-나다라마바사]\.\s+", line
        ):
            if current_section:
                sections.append(
                    {"title": current_title, "content": current_section.strip()}
                )
            current_title = line
            current_section = line + "\n"
        else:
            current_section += line + "\n"

    # 마지막 섹션 추가
    if current_section:
        sections.append({"title": current_title, "content": current_section.strip()})

    # 섹션이 없으면 전체 텍스트를 하나로
    if not sections:
        sections.append({"title": "전체 내용", "content": text})

    return sections


def create_knowledge_base(sections: List[Dict]) -> List[Dict]:
    """
    RAG 시스템을 위한 지식 베이스를 생성합니다.
    """
    knowledge_base = []

    for i, section in enumerate(sections):
        # 각 섹션을 더 작은 청크로 분할
        content = section["content"]
        chunk_size = 800  # 문자 단위 (늘려서 더 많은 정보 포함)
        chunks = [
            content[i : i + chunk_size] for i in range(0, len(content), chunk_size)
        ]

        for j, chunk in enumerate(chunks):
            if chunk.strip():  # 빈 청크는 제외
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

    return knowledge_base


def save_knowledge_base(
    knowledge_base: List[Dict], filename: str = "knowledge_base.json"
):
    """
    지식 베이스를 JSON 파일로 저장합니다.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

    print(f"지식 베이스가 {filename}에 저장되었습니다.")
    print(f"총 {len(knowledge_base)}개의 청크가 생성되었습니다.")


def create_simple_knowledge_base_js(sections: List[Dict]):
    """
    간단한 knowledge_base.js 파일 생성 (기존 방식과 호환)
    """
    knowledge_items = []

    # 주요 키워드 기반으로 간단한 지식 베이스 생성
    keyword_mapping = {
        "등록금": ["등록금", "납부", "등록", "고지서"],
        "영어배치고사": ["영어배치고사", "영어", "배치고사", "GELT"],
        "신체검사": ["신체검사", "검사", "건강검사", "흉부X선", "B형간염"],
        "입학식": ["입학식", "환영회", "입학", "식"],
        "오리엔테이션": ["오리엔테이션", "신입생오리엔테이션", "입학"],
        "기숙사": ["기숙사", "생활관", "명재관", "입사"],
        "장학금": ["장학금", "장학", "지원", "신청"],
        "수강신청": ["수강신청", "수강", "신청"],
        "학자금대출": ["학자금", "대출", "정부보증"],
        "도서관": ["도서관", "대출", "이용"],
    }

    for key, keywords in keyword_mapping.items():
        relevant_content = ""
        for section in sections:
            content = section["content"]
            if any(keyword in content for keyword in keywords):
                relevant_content += content + "\n"

        if relevant_content.strip():
            # 내용 정리
            relevant_content = clean_text(relevant_content)
            # 너무 길면 자르기
            if len(relevant_content) > 1000:
                relevant_content = relevant_content[:1000] + "..."

            knowledge_items.append(
                {"id": key, "keywords": keywords, "content": relevant_content}
            )

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

    print(f"간단한 지식 베이스가 knowledge_base.js에 저장되었습니다.")
    print(f"총 {len(knowledge_items)}개의 항목이 생성되었습니다.")


if __name__ == "__main__":
    # PDF URL
    pdf_url = (
        "https://sookmyongcal.netlify.app/2026학년도신입생합격자안내사항(20251212).pdf"
    )

    print("PDF 내용 추출 중...")
    raw_text = extract_pdf_text_from_url(pdf_url)

    if raw_text:
        print("텍스트 전처리 중...")
        sections = preprocess_text(raw_text)

        print("RAG 지식 베이스 생성 중...")
        knowledge_base = create_knowledge_base(sections)

        print("RAG 지식 베이스 저장 중...")
        save_knowledge_base(knowledge_base)

        print("간단한 knowledge_base.js 생성 중...")
        create_simple_knowledge_base_js(sections)

        # output 디렉토리에도 복사
        os.makedirs("output", exist_ok=True)
        with open("output/knowledge_base.js", "w", encoding="utf-8") as f:
            f.write(open("knowledge_base.js", "r", encoding="utf-8").read())

        print("처리 완료!")
        print(f"추출된 텍스트 길이: {len(raw_text)} 문자")
        print(f"생성된 섹션 수: {len(sections)}")
        print(f"생성된 청크 수: {len(knowledge_base)}")
    else:
        print("PDF 내용 추출에 실패했습니다.")
