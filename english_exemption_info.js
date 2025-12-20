// 영어 교양필수 이수면제 추가 정보
const ADDITIONAL_ENGLISH_EXEMPTION_INFO = `
# 영어 교양필수 이수면제 구체 기준

## 공인영어시험 성적 기준
- **TOEIC**: 850점 이상
- **TOEFL iBT**: 89점 이상  
- **IELTS (A)**: 6.5점 이상
- **TEPS**: 700점 이상

## 숙명여대 GELT 대체 기준
- GELT R, 1, 2, 3 레벨 중 한 개 이상 취득 시 이수 면제

## 신청 방법
- **기간**: 입학 후 1년 이내만 신청 가능 (2026년 3월, 9월만 가능)
- **방법**: 숙명여자대학교 홈페이지 > 공지 > 장학에서 신청 공지 확인
- **제출서류**: 해당 시험 성적표 (2년 이내 발급)

## 참고사항
- 공인영어시험 성적표는 영문 성명과 일치해야 함
- 성적표 제출 시 이수면제 신청서 함께 제출
- GELT 성적표도 이수면제 신청 가능

## 문의처
- **담당부서**: 순헌칼리지 교학팀
- **전화번호**: 02-2077-7511
- **위치**: 행정관 201호
- **홈페이지**: sunheon.sookmyung.ac.kr
`;

// 챗봇 지식 베이스에 추가
function updateEnglishExemptionInfo() {
    // 현재 knowledge_base.js에 새로운 정보 추가
    console.log("영어 교양필수 이수면제 기준 정보 업데이트");
}

// 다운로드 가능한 상세 안내서 생성
function generateDetailedGuide() {
    const detailedGuide = `
# 2026학년도 신입생 영어 교양필수 이수면제 상세 안내

## 기본 정보
PDF에 포함된 기준 외에 추가적인 기준 정보가 필요하신 경우 아래 내용을 참고해주세요.

## 상세 기준
${ADDITIONAL_ENGLISH_EXEMPTION_INFO}

## 자주 묻는 질문
Q: TOEIC 845점은 가능한가요?
A: 850점 이상이 필요하므로 845점은 불가능합니다.

Q: 2년 전 성적표는 가능한가요?
A: 2년 이내 발급된 성적표만 인정됩니다.

Q: IELTS General은 가능한가요?
A: IELTS Academic(A) 기준만 인정됩니다.
`;
    return detailedGuide;
}