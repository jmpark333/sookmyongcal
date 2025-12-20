import json
import numpy as np
from typing import List, Dict, Tuple
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimpleRAGSystem:
    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        """
        간단한 RAG 시스템 초기화
        """
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words=None, ngram_range=(1, 2)
        )
        self.embeddings = None
        self._build_embeddings()

    def load_knowledge_base(self, path: str) -> List[Dict]:
        """
        지식 베이스 로드
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"지식 베이스 로드 실패: {e}")
            return []

    def _build_embeddings(self):
        """
        문서 임베딩 생성
        """
        if not self.knowledge_base:
            print("지식 베이스가 비어있습니다.")
            return

        # 모든 문서 내용 추출
        documents = [chunk["content"] for chunk in self.knowledge_base]

        # 텍스트 전처리
        processed_docs = [self._preprocess_text(doc) for doc in documents]

        # TF-IDF 벡터화
        self.embeddings = self.vectorizer.fit_transform(processed_docs)
        print(f"임베딩 생성 완료: {self.embeddings.shape}")

    def _preprocess_text(self, text: str) -> str:
        """
        텍스트 전처리
        """
        # 널문자 및 특수문자 제거 및 정규화
        text = re.sub(r"\x00", "", text)  # 널문자 제거
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        관련 문서 검색 (부분 문자열 매칭)
        """
        if not self.knowledge_base:
            return []

        processed_query = self._preprocess_text(query)
        query_terms = processed_query.split()

        results = []
        for idx, doc in enumerate(self.knowledge_base):
            doc_content = self._preprocess_text(doc["content"])

            # 부분 문자열 매칭 점수 계산
            score = 0
            for term in query_terms:
                if term in doc_content:  # 정확히 일치
                    score += 1
                else:
                    # 부분 문자열 검색
                    for word in doc_content.split():
                        if term in word or word in term:
                            score += 0.5
                            break

            if score > 0:
                similarity = score / len(query_terms)
                result = {**doc, "similarity": similarity}
                results.append((result, similarity))

        # 유사도로 정렬
        results.sort(key=lambda x: x[1], reverse=True)

        # 상위 k개 반환
        return [result for result, _ in results[:top_k]]

    def get_context_for_query(self, query: str, max_context_length: int = 1000) -> str:
        """
        쿼리에 대한 컨텍스트 생성
        """
        relevant_docs = self.search(query, top_k=3)

        if not relevant_docs:
            return "관련 정보를 찾을 수 없습니다."

        context_parts = []
        current_length = 0

        for doc in relevant_docs:
            content = doc["content"]
            title = doc.get("title", "")

            # 문서 포맷팅
            formatted_doc = f"[{title}] {content}"

            if current_length + len(formatted_doc) <= max_context_length:
                context_parts.append(formatted_doc)
                current_length += len(formatted_doc)
            else:
                break

        return "\n\n".join(context_parts)


# 전역 RAG 시스템 인스턴스
rag_system = SimpleRAGSystem()
rag_system._build_embeddings()  # 임베딩 재생성


def get_rag_context(query: str) -> str:
    """
    쿼리에 대한 RAG 컨텍스트 반환
    """
    return rag_system.get_context_for_query(query)


def test_rag_system():
    """
    RAG 시스템 테스트
    """
    test_queries = [
        "등록금 납부 기간은?",
        "영어배치고사는 언제?",
        "장학금 신청 방법",
        "입학식 일정",
        "기숙사 입사 신청",
    ]

    for query in test_queries:
        print(f"\n쿼리: {query}")
        context = get_rag_context(query)
        print(f"컨텍스트: {context[:200]}...")


if __name__ == "__main__":
    test_rag_system()
