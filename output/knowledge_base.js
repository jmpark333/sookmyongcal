// 지식 베이스 데이터 (PDF에서 추출)
const KNOWLEDGE_BASE = [
  {
    "id": "enrollment_period",
    "keywords": ["등록금", "납부", "등록", "고지서"],
    "content": "2026년 본등록금 납부 기간은 2026년 2월 3일(화) 10:00 ~ 2월 5일(목) 16:00까지입니다. 납부 방법은 신한은행(창구납부 또는 계좌이체) 및 우체국 포함, 국내 모든 은행 창구 및 스마트폰뱅킹, CD/ATM기 이체 무통장입금이 가능합니다 (단, KB모바일, 농협 ARS는 불가). 본등록금 고지서는 2026년 2월 3일(화) 10시부터 입학처 홈페이지(admission.sookmyung.ac.kr)에서 출력할 수 있습니다."
  },
  {
    "id": "english_test",
    "keywords": ["영어배치고사", "영어", "배치고사", "GELT"],
    "content": "영어배치고사는 다음과 같습니다:\n• 1차: 1월 23일(금) 24:00 (접수: 1월 6일(화) 10:00 ~ 1월 19일(월) 10:00, 응시: 1월 13일(화) 24:00)\n• 2차: 2월 6일(금) 24:00 (접수: 2월 5일(목) 10:00 ~ 2월 10일(화) 10:00, 응시: 2월 19일(목) 10:00 ~ 24:00)\n• 3차: 2월 24일(화) (접수/응시: 2월 27일(금) 10:00 ~ 3월 4일(수) 16:00)\n• 4차: 3월 1일(일) 24:00 (응시: 3월 4일(수) 10:00 ~ 16:00)\n접수처는 본교 홈페이지 > 주요공지 또는 순헌칼리지 홈페이지(sunheon.sookmyung.ac.kr)입니다."
  },
  {
    "id": "health_check",
    "keywords": ["신체검사", "검사", "건강검사", "흉부X선", "B형간염"],
    "content": "신체검사는 2026년 2월 24일(화) ~ 2월 26일(목) 예정이며 보건의료센터에서 실시합니다. 최근 6개월 이내에 실시한 흉부 X선 검사, B형간염 항원항체 검사 결과지를 3월 중으로 교내 보건의료센터(순헌관 011호)로 반드시 제출해야 합니다. 신체검사비는 선택납부이므로 개인 사정으로 신체검사를 수검하지 않더라도 신체검사비 환불은 불가합니다. 본 검사 결과는 2026학년도 1학기 본교 기숙사 입사 시 제출 서류로 활용 가능합니다."
  },
  {
    "id": "entrance_ceremony",
    "keywords": ["입학식", "환영회", "입학", "식"],
    "content": "입학식 및 신입생 환영회는 2026년 2월 23일(월) 예정이며 장소는 미정입니다. 학생지원센터에서 주관합니다."
  },
  {
    "id": "orientation",
    "keywords": ["오리엔테이션", "신입생오리엔테이션", "입학"],
    "content": "신입생 오리엔테이션은 2026년 2월 25일(수) ~ 2월 26일(목)에 실시됩니다. 학생지원센터에서 주관합니다."
  },
  {
    "id": "dormitory",
    "keywords": ["기숙사", "생활관", "명재관", "입사"],
    "content": "학생생활관(명재관) 입사는 서울, 경인지역을 제외한 지방에 거주하는 2026학번 신입학부생 대상입니다 (단, 경인지역은 주소 내 '읍·면·리'인 경우 신청 가능). 우선 입사 자격: 장애학생, 재외국민(본인 및 보호자가 재외국민이어야 하며, 본인 및 보호자 재외국민등록부 등본 제출), 순헌장학생, 생활보호대상자(기초생활수급자) 및 국가유공자(독립유공자 자녀 및 손자녀, 국가유공자 자녀)입니다. 거주기간은 해당 연도 1년만 거주 가능하며 2026년 1학기 입사 후 퇴사한 경우, 2026년 재입사 불가합니다. 입사 신청 일정은 2026년 예정이며 상세 일정은 추후 안내됩니다."
  }
];

// 질문과 관련된 지식 베이스 항목 찾기
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
        return "안녕하세요! 숙명여자대학교 2026학년도 신입생 합격자 안내사항 전문 챗봇입니다. 등록금, 입학식, 영어배치고사, 기숙사, 신체검사, 오리엔테이션 등에 대해 질문해 주세요.";
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