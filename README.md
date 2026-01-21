# 숙명여자대학교 2026학년도 신입생 안내 챗봇

숙명여자대학교 2026학년도 신입생 합격자 안내사항을 위한 AI 챗봇 시스템입니다.

## 배포 주소

- **웹사이트**: https://sookmyongcal.netlify.app/
- **GitHub**: https://github.com/jmpark333/sookmyongcal

## 프로젝트 개요

이 프로젝트는 숙명여대 신입생과 재학생들이 입학 및 수강신청 관련 정보를 쉽게 찾을 수 있도록 AI 챗봇과 일정 달력을 제공합니다.

- **AI 챗봇**: Z.AI GLM-4.7 모델 기반 질의응답
- **지식 베이스**: 수강신청 일정, 영어 면제, 신입생 오리엔테이션 등
- **일정 달력**: 2026학년도 주요 일정 확인
- **반응형 디자인**: 모바일/데스크톱 환경 모두 지원

## 프로젝트 구조

```
sookmyongcal/
├── index.html                 # 메인 페이지 (채팅창 + 일정 달력)
├── knowledge_base.js          # 챗봇 지식 베이스
├── build.py                   # 빌드 스크립트 (output/ 생성)
├── netlify.toml               # Netlify 배포 설정
├── netlify/functions/
│   ├── chat.js                # Netlify 서버리스 함수 (챗봇 API)
│   └── package.json           # 함수 의존성
├── output/                    # 빌드 결과물 (Netlify publish 디렉토리)
│   ├── index.html
│   └── *.pdf                  # PDF 파일들
├── course-registration-guide-2026-1.pdf    # 수강신청 가이드 PDF
├── 2026학년도신입생합격자안내사항(20251212).pdf  # TOEIC 안내 PDF
├── chatbot_server.py          # (로컬 테스트용) Flask 서버
├── rag_system.py              # (로컬 테스트용) RAG 시스템
└── requirements.txt           # Python 의존성
```

## 핵심 파일 설명

### index.html
- 메인 웹페이지이자 챗봇 인터페이스
- `KNOWLEDGE_BASE` 배열: 지식 베이스 데이터 (knowledge_base.js에서 로드)
- `buildKnowledgeContext()`: 지식 베이스를 문자열로 변환하여 API로 전송
- `parseMarkdown()`: 마크다운을 HTML로 변환 (**굵게**, *기울임*, 줄바꿈)
- `sendMessage()`: 챗봇 API 요청 처리
- 챗봇 창 설정: 높이 700px (모바일) / 650px (PC), 하단 위치

### knowledge_base.js
- 챗봇의 지식 베이스 데이터
- `KNOWLEDGE_BASE` 배열: 각 항목은 `{id, category, keywords, content}` 형태
- 주요 카테고리:
  - `registration_schedule_2026_1`: 2026-1학기 수강신청 일정
  - `english_exemption_2026`: 영어 면제 관련
  - `toeic_schedule_2026`: TOEIC 일정
  - `freshman_guide_2026`: 신입생 안내

### build.py
- 정적 사이트 빌드 스크립트
- `output/` 디렉토리에 배포용 파일 생성
- 복사 대상: index.html, knowledge_base.js, PDF 파일, 이미지
- **주의**: `netlify/functions/`는 Netlify가 자동 처리하므로 복사하지 않음

### netlify/functions/chat.js
- Netlify 서버리스 함수
- API 엔드포인트: `/.netlify/functions/chat`
- 요청 형식: `{ message: string, context: string }`
- 응답 형식: `{ response: string }`
- Z.AI GLM-4.7 모델 사용 (thinking 모드 비활성화)

### netlify.toml
```toml
[build]
  command = "python3 build.py"
  publish = "output"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

## 빌드 및 배포

### 로컬 빌드 테스트
```bash
python3 build.py
```

### 배포 (자동)
GitHub에 push하면 Netlify가 자동으로 빌드하고 배포합니다.
1. `git commit`
2. `git push`
3. Netlify에서 `build.py` 실행
4. `output/` 디렉토리 배포
5. `netlify/functions/` 자동 감지 및 배포

## 최근 수정 이력

### 2026-01-21: 챗봇 CORS/배포 문제 해결
1. **PDF 배포 수정**: `build.py`에 PDF 파일 추가
2. **CORS 문제 해결**: 외부 프록시 대신 로컬 Netlify 함수 사용
3. **함수 위치 수정**: `functions/` → `netlify/functions/`
4. **요청 형식 수정**: `{model, messages, stream}` → `{message, context}`
5. **모델 변경**: glm-4.6 → glm-4.7, thinking 모드 비활성화
6. **마크다운 파싱 추가**: `**굵게**`, `*기울임*`, 줄바꿈 처리
7. **챗봇 창 크기 증가**: 높이 700px/650px, 하단 위치 조정

## 알려진 문제 및 해결 방법

### PDF가 404/HTML로 반환됨
- **원인**: PDF가 `output/` 디렉토리에 없음
- **해결**: `build.py`의 `static_files` 리스트에 PDF 추가

### 챗봇 첫 요청 실패 (CORS 에러)
- **원인**: 외부 프록시 사용 시 CORS preflight/cold start
- **해결**: 로컬 Netlify 함수 (`/.netlify/functions/chat`) 사용

### 챗봇 404 에러
- **원인**: 함수가 `functions/`에 있어서 Netlify가 감지 못함
- **해결**: `netlify/functions/`로 이동

### 챗봇 400 에러
- **원인**: 요청 형식 불일치
- **해결**: `{message, context}` 형식으로 변경

### 챗봇 답변에 추론 과정 출력
- **원인**: GLM-4.6의 thinking 모드 기본 활성화
- **해결**: `thinking: { type: "disabled" }` 추가

### 마크다운 형식이 그대로 출력됨
- **원인**: 마크다운 파싱 없음
- **해결**: `parseMarkdown()` 함수 추가

## 챗봇 지식 베이스 업데이트

`knowledge_base.js`의 `KNOWLEDGE_BASE` 배열에 새로운 항목 추가:

```javascript
{
  id: "unique_id",
  category: "카테고리명",
  keywords: ["키워드1", "키워드2"],
  content: "내용"
}
```

## 환경 변수

Netlify 함수 환경 변수 (Netlify Dashboard에서 설정):
- `ZAI_API_KEY`: Z.AI API 키

## 기술 스택

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: Netlify Functions (Node.js)
- **AI**: Z.AI GLM-4.7 모델
- **배포**: Netlify (정적 호스팅 + 서버리스 함수)
- **빌드**: Python 3 (build.py)

## 라이선스

숙명여자대학교 내부 사용 프로젝트
