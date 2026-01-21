const https = require('https');

// Z.AI API 설정
const ZAI_API_KEY = process.env.ZAI_API_KEY || "6e74659313a8456da1b4881d29dc098f.SgJrKDIG5qoTW9YO";
const ZAI_API_URL = "https://api.z.ai/api/paas/v4/chat/completions";

// 간단한 지식 베이스 (하드코딩된 응답)
const KNOWLEDGE_BASE = {
  "등록금": "2026년 본등록금 납부 기간은 2026년 2월 3일(화) 10:00 ~ 2월 5일(목) 16:00 입니다. 신한은행 및 국내 모든 은행에서 납부 가능합니다.",
  "입학식": "입학식 및 신입생 환영회는 2026년 2월 23일(월) 예정입니다. 장소는 미정입니다.",
  "영어배치고사": "영어배치고사는 다음과 같습니다:\n1차: 1월 23일(금) 24:00\n2차: 2월 6일(금) 24:00, 2월 19일(목) 10:00~24:00\n3차: 2월 24일(화) 10:00~24:00\n4차: 3월 1일(일) 24:00, 3월 4일(수) 10:00~16:00",
  "기숙사": "학생생활관(명재관) 입사 안내는 2026학년도 신입생 합격자 안내사항 9페이지를 참조해주세요.",
  "신체검사": "신체검사는 2026년 2월 24일(화) ~ 2월 26일(목) 예정이며, 보건의료센터에서 실시합니다.",
  "오리엔테이션": "신입생 오리엔테이션은 2026년 2월 25일(수) ~ 2월 26일(목)에 실시됩니다."
};

function findContext(query) {
  const lowerQuery = query.toLowerCase();
  
  for (const [keyword, response] of Object.entries(KNOWLEDGE_BASE)) {
    if (lowerQuery.includes(keyword.toLowerCase())) {
      return response;
    }
  }
  
  return "관련 정보를 찾을 수 없습니다. 더 구체적인 질문을 해주세요.";
}

function generateResponse(prompt, context) {
  return new Promise((resolve, reject) => {
    const headers = {
      'Authorization': `Bearer ${ZAI_API_KEY}`,
      'Content-Type': 'application/json',
      'Accept-Language': 'en-US,en'
    };

    const messages = [];
    if (context && context !== "관련 정보를 찾을 수 없습니다. 더 구체적인 질문을 해주세요.") {
      // 클라이언트에서 온 전체 지식 베이스 컨텍스트 또는 간단 매칭 결과
      messages.push({
        "role": "system",
        "content": `당신은 숙명여자대학교 학생 도우미 챗봇입니다. 신입생 합격자 안내사항과 재학생 수강가이드 정보를 모두 제공합니다. 다음 지식 베이스를 기반으로 답변해주세요.

${context}

**중요 지침:**
1. 위 지식 베이스에 있는 정보만 정확하게 바탕으로 답변하세요
2. 지식 베이스에 없는 내용(특정 인물, 개인 정보 등)에 대해서는 솔직하게 "그 정보는 제가 가진 자료에 없습니다"라고 답변하세요
3. 숙명여대 신입생 및 재학생 관련 일반적인 질문에 대해서는 지식 베이스의 내용을 활용하여 친절하게 답변하세요
4. 한국어로, 친절하고 전문적인 어조로 답변하세요
5. 질문의 의도를 정확히 파악하여 관련 있는 정보만 제공하세요`
      });
    } else {
      messages.push({
        "role": "system",
        "content": "당신은 숙명여자대학교 신입생 안내 챗봇입니다. 친절하고 정확하게 답변해주세요."
      });
    }
    
    messages.push({
      "role": "user",
      "content": prompt
    });

    const data = {
      "model": "glm-4.6",
      "messages": messages,
      "max_tokens": 500,
      "temperature": 0.3
    };

    const postData = JSON.stringify(data);

    const options = {
      hostname: 'api.z.ai',
      port: 443,
      path: '/api/paas/v4/chat/completions',
      method: 'POST',
      headers: {
        ...headers,
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = https.request(options, (res) => {
      let responseData = '';

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        try {
          const result = JSON.parse(responseData);
          
          if (result.choices && result.choices.length > 0) {
            const message = result.choices[0].message;
            const content = message.content || message.reasoning_content || '';
            
            if (content) {
              resolve(content.trim());
            } else {
              resolve("죄송합니다. 응답을 받지 못했습니다. 잠시 후 다시 시도해주세요.");
            }
          } else {
            resolve("죄송합니다. 응답 처리 중 오류가 발생했습니다.");
          }
        } catch (error) {
          console.error('Parse error:', error);
          reject(error);
        }
      });
    });

    req.on('error', (error) => {
      console.error('Request error:', error);
      reject(error);
    });

    req.write(postData);
    req.end();
  });
}

exports.handler = async function(event, context) {
  try {
    const method = event.httpMethod || event.method || 'GET';
    
    if (method === 'GET') {
      return {
        statusCode: 200,
        body: JSON.stringify({ status: 'healthy', service: 'sookmyong-chatbot' }),
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      };
    }

    if (method === 'POST') {
      let body;
      try {
        body = JSON.parse(event.body);
      } catch (e) {
        return {
          statusCode: 400,
          body: JSON.stringify({ error: 'Invalid JSON' }),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        };
      }

      if (!body || !body.message) {
        return {
          statusCode: 400,
          body: JSON.stringify({ error: '메시지가 없습니다.' }),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        };
      }

      const userMessage = body.message.trim();

      // 클라이언트에서 보낸 컨텍스트 사용 (우선), 없으면 하드코딩된 매칭 사용
      let context = body.context;
      if (!context) {
        context = findContext(userMessage);
      }

      try {
        const botResponse = await generateResponse(userMessage, context);
        
        return {
          statusCode: 200,
          body: JSON.stringify({
            response: botResponse,
            context_used: context !== "관련 정보를 찾을 수 없습니다. 더 구체적인 질문을 해주세요."
          }),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        };
      } catch (apiError) {
        console.error('API Error:', apiError);
        
        // API 실패시 컨텍스트 응답 반환
        const fallbackResponse = typeof context === 'string' ? context : '관련 정보를 찾을 수 없습니다. 더 구체적인 질문을 해주세요.';
        return {
          statusCode: 200,
          body: JSON.stringify({
            response: fallbackResponse,
            context_used: true
          }),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        };
      }
    }

    return {
      statusCode: 405,
      body: JSON.stringify({ error: '허용되지 않는 메소드입니다.' }),
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    };

  } catch (error) {
    console.error('Handler error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: '서버 내부 오류가 발생했습니다.' }),
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    };
  }
};