# Claude Code를 위한 프로젝트 가이드

이 문서는 Claude Code가 이 프로젝트를 빠르게 파악하고 수정하기 위한 참고 문서입니다.

## 프로젝트 핵심 이해

### 배포 구조
```
GitHub → Netlify → 자동 빌드 → 배포
```

1. **GitHub에 push** → Netlify가 자동으로 감지
2. **Netlify가 build.py 실행** → `output/` 디렉토리 생성
3. **Netlify가 output/ 배포** → 정적 파일 서빙
4. **netlify/functions/ 자동 배포** → 서버리스 함수 배포

### ⚠️ 절대 혼동하지 말아야 할 디렉토리 구조

```
sookmyongcal/
├── output/              # 빌드 결과물 (Netlify의 publish 디렉토리)
│   └── *.html, *.js, *.pdf  # 이게 실제로 배포되는 파일들
├── netlify/
│   ├── functions/       # ⭐ Netlify 서버리스 함수 (여기에 있어야 배포됨)
│   │   └── chat.js      # /.netlify/functions/chat 로 접근
│   └── *.pdf            # (과거: 정적 파일 보관용)
├── index.html           # 소스 파일 (build.py가 output/으로 복사)
├── knowledge_base.js    # 소스 파일 (build.py가 output/으로 복사)
└── *.pdf                # 소스 파일 (build.py가 output/으로 복사)
```

### 🔥 치명적인 함정 정리

| 함정 | 증상 | 원인 | 해결 |
|------|------|------|------|
| **함수 404** | `/.netlify/functions/chat`가 404 | 함수가 `functions/`에 있음 | `netlify/functions/`로 이동 |
| **PDF 404** | PDF가 HTML로 반환됨 | PDF가 `output/`에 없음 | `build.py`의 `static_files`에 추가 |
| **CORS 에러** | 외부 API 호출 차단 | 다른 도메인의 프록시 사용 | 로컬 Netlify 함수 사용 |
| **함수 변경 안됨** | 수정해도 반영 안됨 | `output/functions/`를 수정함 | `netlify/functions/`를 수정 |

## Netlify 설정 (netlify.toml)

```toml
[build]
  command = "python3 build.py"  # 빌드 스크립트
  publish = "output"            # 배포할 디렉토리

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
```

### 중요한 점
- **publish = "output"**: `output/` 디렉토리만 배포됨
- **netlify/functions/**: Netlify가 자동으로 감지하고 배포 (build.py에서 복사 ❌)
- **functions/**: Netlify가 감지 못함 → 무조건 `netlify/functions/` 사용

## 빌드 스크립트 (build.py)의 역할

```python
# 정적 파일 복사
static_files = [
    "index.html",
    "knowledge_base.js",
    "emblem-1_Color.png",
    "img-logo01.png",
    "course-registration-guide-2026-1.pdf",     # PDF 추가 시 여기에
    "2026학년도신입생합격자안내사항(20251212).pdf",
]

# ⚠️ 복사하지 않는 것
# - netlify/functions/ → Netlify가 자동 처리
# - output/ → 빌드 결과물 디렉토리
# - netlify/ → PDF 보관용 (과거 호환)
```

## 챗봇 API 요청/응답 형식

### 클라이언트 (index.html) → 서버 (chat.js)

**요청:**
```javascript
POST /.netlify/functions/chat
Content-Type: application/json

{
  "message": "수강신청 마감이 언제야?",
  "context": "전체 지식 베이스 문자열..."  // buildKnowledgeContext() 생성
}
```

**응답:**
```json
{
  "response": "2026년 1학기 수강신청 일정은..."
}
```

### 🚫 과거 요청 형식 (사용하지 않음)
```javascript
// 이 형식은 외부 프록시용 - 로컬 함수와 호환 안됨
{
  "model": "glm-4.6",
  "messages": [...],
  "stream": false
}
```

## Z.AI API 설정 (chat.js)

```javascript
const response = await fetch("https://api.z.ai/api/paas/v4/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${process.env.ZAI_API_KEY}`
  },
  body: JSON.stringify({
    model: "glm-4.7",                    // ⭐ 최신 모델
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: userMessage + "\n\n" + context }
    ],
    thinking: { type: "disabled" },      // ⭐ 추론 출력 비활성화
    max_tokens: 2000,
    temperature: 0.7
  })
});
```

### ⚠️ thinking 모드 주의
```javascript
// ❌ 추론 과정까지 출력됨 (사용자에게 노출)
thinking: { type: "enabled" }  // 기본값

// ✅ 깔끔한 답변만 출력
thinking: { type: "disabled" }
```

## 수정 시 체크리스트

### 챗봇 응답 수정
- [ ] `netlify/functions/chat.js` 수정 (❌ `output/functions/chat.js` 아님)
- [ ] 커밋 후 푸시 → Netlify 자동 배포 확인

### 지식 베이스 추가
- [ ] `knowledge_base.js`에 항목 추가
- [ ] 배포 후 챗봇에서 테스트

### PDF 파일 추가
- [ ] 루트 디렉토리에 PDF 배치
- [ ] `build.py`의 `static_files`에 PDF 추가
- [ ] 커밋 및 푸시
- [ ] `https://sookmyongcal.netlify.app/파일명.pdf` 확인

### UI/CSS 수정
- [ ] `index.html` 수정
- [ ] 커밋 후 푸시

### 마크다운 파싱
- [ ] `index.html`의 `parseMarkdown()` 함수 확인
- [ ] `**굵게**`, `*기울임*`, `【하이라이트】` 지원

## 로컬 테스트 방법

### 빌드 테스트
```bash
python3 build.py
ls -la output/  # 결과 확인
```

### 정적 파일 테스트
```bash
# 간단한 HTTP 서버
cd output/
python3 -m http.server 8000
# http://localhost:8000 접근
```

### Netlify 함수 로컬 테스트
```bash
cd netlify/functions/
npm install
node chat.js  # 또는 netlify-dev
```

## 자주 발생하는 에러와 해결

### 1. "Failed to fetch" / CORS 에러
```
Access to fetch at 'https://external-proxy.com' has been blocked by CORS policy
```
**해결:** `API_URL`을 `/.netlify/functions/chat`로 변경

### 2. "API 호출 실패: 404"
```
POST https://sookmyongcal.netlify.app/.netlify/functions/chat 404
```
**해결:** 함수가 `netlify/functions/chat.js`에 있는지 확인

### 3. "API 호출 실패: 400"
```
The request was malformed
```
**해결:** 요청 형식이 `{ message, context }`인지 확인

### 4. PDF가 다운로드되지 않고 HTML 페이지가 뜸
```
Content-Type: text/html (예상: application/pdf)
```
**해결:** `build.py`의 `static_files`에 PDF 추가

### 5. 챗봇이 추론 과정을 출력함
```
1. 사용자 질문 분석: ...
2. 지식 베이스 검색: ...
```
**해결:** `thinking: { type: "disabled" }` 추가

## 환경 변수

### Netlify Dashboard에서 설정
- `ZAI_API_KEY`: Z.AI API 키 (필수)
- `NODE_VERSION`: 18 (권장)

## 파일 수정 위치 요약

| 수정 내용 | 파일 위치 | ⚠️ 주의 |
|----------|----------|---------|
| 챗봇 API 로직 | `netlify/functions/chat.js` | `output/functions/` 수정 금지 |
| 지식 베이스 | `knowledge_base.js` | |
| UI/HTML | `index.html` | |
| CSS 스타일 | `index.html` 내 `<style>` | |
| 빌드 설정 | `build.py` | PDF 추가 시 수정 |
| 배포 설정 | `netlify.toml` | |
| 마크다운 파싱 | `index.html` 내 `parseMarkdown()` | |

## 빠른 참조

### 배포 확인
```
https://sookmyongcal.netlify.app/
```

### Netlify Dashboard
```
https://app.netlify.com/sites/sookmyongcal/overview
```

### 함수 로그 확인
1. Netlify Dashboard 접속
2. Functions → chat → Deployments
3. 로그 확인

### PDF 직접 링크 예시
```
https://sookmyongcal.netlify.app/course-registration-guide-2026-1.pdf
```
