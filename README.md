# 숙명여자대학교 2026학년도 신입생 안내 챗봇

숙명여자대학교 2026학년도 신입생 합격자 안내사항을 위한 AI 챗봇 시스템입니다.

## 프로젝트 개요

이 프로젝트는 숙명여대 신입생들이 입학 관련 정보를 쉽게 찾을 수 있도록 AI 챗봇과 일정 달력을 제공합니다.

- **AI 챗봇**: RAG(검색 증강 생성) 시스템을 활용하여 문서 기반 질의응답 제공
- **일정 달력**: 2026학년도 신입생 주요 일정을 한눈에 확인 가능
- **반응형 디자인**: 모바일/데스크톱 환경 모두 지원

## 주요 기능

### 챗봇 시스템
- Z.AI GLM-4.6 모델 기반 자연어 응답 생성
- TF-IDF 벡터화를 활용한 문서 검색
- 관련 문서 컨텍스트를 활용한 정확한 답변
- 캐싱을 통한 빠른 응답 속도

### 일정 관리
- 월별 일정 달력 뷰
- TOEIC 일정 포함
- 반응형 테이블 디자인

## 시스템 구조

```
sookmyongcal/
├── chatbot_server.py      # Flask 챗봇 서버
├── rag_system.py          # RAG 검색 시스템
├── index.html             # 메인 일정 달력 페이지
├── knowledge_base.json    # 검색을 위한 지식 베이스
├── templates/
│   └── index.html         # 챗봇 웹 인터페이스
└── requirements.txt       # Python 의존성
```

## 설치 방법

### 사전 요구사항
- Python 3.8+
- pip

### 설치 단계

1. 리포지토리 클론:
```bash
git clone <repository-url>
cd sookmyongcal
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정 (선택사항):
```bash
export ZAI_API_KEY="your-api-key"
export FLASK_ENV="development"
export LOG_LEVEL="INFO"
```

## 실행 방법

### 개발 모드
```bash
python chatbot_server.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

### 정적 웹페이지만 실행
챗봇 기능 없이 일정 달력만 확인하려면 브라우저에서 `index.html`을 직접 엽니다.

## API 엔드포인트

### POST /chat
챗봇 질문에 대한 답변을 받습니다.

**요청:**
```json
{
  "message": "등록금 납부 기간은 언제인가요?"
}
```

**응답:**
```json
{
  "response": "2026년 2월 16일(월) ~ 2월 18일(수)입니다.",
  "context_used": true
}
```

### GET /health
서버 상태 확인.

### GET /
챗봇 웹 인터페이스 페이지.

## 기술 스택

- **Backend**: Flask, Python 3.8+
- **AI/ML**: GLM-4.6 (Z.AI API), TF-IDF, scikit-learn
- **Frontend**: HTML, CSS, JavaScript
- **배포**: Netlify (정적 웹페이지)

## 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `ZAI_API_KEY` | Z.AI API 키 | (내장 기본값) |
| `FLASK_ENV` | Flask 실행 모드 | - |
| `LOG_LEVEL` | 로깅 레벨 | `INFO` |
| `API_TIMEOUT` | API 타임아웃(초) | `30` |

## 개발 참고사항

### RAG 시스템 커스터마이징
`rag_system.py`에서 검색 알고리즘을 수정하여 검색 정확도를 개선할 수 있습니다.

### 지식 베이스 업데이트
`knowledge_base.json` 파일에 새로운 문서 정보를 추가하여 챗봇의 지식 범위를 확장할 수 있습니다.

### 챗봇 프롬프트 수정
`chatbot_server.py`의 `SYSTEM_PROMPT` 변수를 수정하여 챗봇의 응답 스타일을 변경할 수 있습니다.

## 라이선스

숙명여자대학교 내부 사용 프로젝트

## 문의

담당 부서에 문의해 주세요.
