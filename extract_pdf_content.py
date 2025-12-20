import requests
import re
import json
from typing import List, Dict
import os
import subprocess
import sys

def extract_pdf_text_from_url(pdf_url: str) -> str:
    """
    PDF URL에서 텍스트 내용을 추출합니다. 여러 방법을 시도합니다.
    """
    try:
        # PDF 다운로드
        response = requests.get(pdf_url)
        response.raise_for_status()
        
        # 파일로 저장
        pdf_path = 'temp_pdf.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        
        text = ""
        
        # 방법 1: pdfplumber 사용 (더 나은 한글 지원)
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
                return text
                
        except ImportError:
            print("pdfplumber가 설치되지 않았습니다. 다른 방법을 시도합니다.")
        except Exception as e:
            print(f"pdfplumber 추출 실패: {e}")
        
        # 방법 2: pdftotext 사용 (시스템 명령어)
        try:
            result = subprocess.run(['pdftotext', pdf_path, '-'],
                                  capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout
                print("pdftotext로 텍스트 추출 성공")
                os.remove(pdf_path)
                return text
        except FileNotFoundError:
            print("pdftotext가 설치되지 않았습니다. 다른 방법을 시도합니다.")
        except Exception as e:
            print(f"pdftotext 추출 실패: {e}")
        
        # 방법 3: PyPDF2 사용 (기존 방법)
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                print("PyPDF2로 텍스트 추출 성공")
                os.remove(pdf_path)
                return text
                
        except Exception as e:
            print(f"PyPDF2 추출 실패: {e}")
        
        # 임시 파일 삭제
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        
        return text
    
    except Exception as e:
        print(f"PDF 처리 중 오류 발생: {e}")
        return ""

def preprocess_text(text: str) -> List[Dict]:
    """
    추출된 텍스트를 전처리하여 문서 단위로 분할합니다.
    """
    # 텍스트 정제
    text = re.sub(r'\s+', ' ', text)  # 여러 공백을 하나로
    text = re.sub(r'\n\s*\n', '\n\n', text)  # 문단 구분
    
    # 문서를 섹션으로 분할
    sections = []
    current_section = ""
    current_title = ""
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 제목 패턴 감지 (예: "1. 입학 절차", "가. 등록금 납부")
        if re.match(r'^[0-9가-힣]+\.\s+', line) or re.match(r'^[가-나다라마바사]\.\s+', line):
            if current_section:
                sections.append({
                    "title": current_title,
                    "content": current_section.strip()
                })
            current_title = line
            current_section = line + "\n"
        else:
            current_section += line + "\n"
    
    # 마지막 섹션 추가
    if current_section:
        sections.append({
            "title": current_title,
            "content": current_section.strip()
        })
    
    return sections

def create_knowledge_base(sections: List[Dict]) -> List[Dict]:
    """
    RAG 시스템을 위한 지식 베이스를 생성합니다.
    """
    knowledge_base = []
    
    for i, section in enumerate(sections):
        # 각 섹션을 더 작은 청크로 분할
        content = section['content']
        chunk_size = 500  # 문자 단위
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
        
        for j, chunk in enumerate(chunks):
            knowledge_base.append({
                "id": f"section_{i}_chunk_{j}",
                "title": section['title'],
                "content": chunk,
                "metadata": {
                    "section_index": i,
                    "chunk_index": j,
                    "total_chunks": len(chunks)
                }
            })
    
    return knowledge_base

def save_knowledge_base(knowledge_base: List[Dict], filename: str = "knowledge_base.json"):
    """
    지식 베이스를 JSON 파일로 저장합니다.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)
    
    print(f"지식 베이스가 {filename}에 저장되었습니다.")
    print(f"총 {len(knowledge_base)}개의 청크가 생성되었습니다.")

if __name__ == "__main__":
    # PDF URL
    pdf_url = "https://sookmyongcal.netlify.app/2026학년도신입생합격자안내사항(20251212).pdf"
    
    print("PDF 내용 추출 중...")
    raw_text = extract_pdf_text_from_url(pdf_url)
    
    if raw_text:
        print("텍스트 전처리 중...")
        sections = preprocess_text(raw_text)
        
        print("지식 베이스 생성 중...")
        knowledge_base = create_knowledge_base(sections)
        
        print("지식 베이스 저장 중...")
        save_knowledge_base(knowledge_base)
        
        print("처리 완료!")
    else:
        print("PDF 내용 추출에 실패했습니다.")