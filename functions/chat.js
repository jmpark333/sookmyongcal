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
      messages.push({
        "role": "system",
        "content": `당신은 숙명여자대학교 신입생 안내 챗봇입니다. 다음 정보를 바탕으로 질문에 답변해주세요: ${context}`
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
      
      // 먼저 간단한 매칭으로 응답 시도
      const context = findContext(userMessage);
      
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
        
        // API 실패시 하드코딩된 응답 반환
        return {
          statusCode: 200,
          body: JSON.stringify({
            response: context,
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