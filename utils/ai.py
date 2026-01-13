import json
import requests
from config import Config
from functools import wraps

AI_SYSTEM_PROMPT = """你是一个专业的心理分析师，擅长通过分析社交聊天记录来洞察一个人的性格特质、行为偏好、社交模式和思维方式。

## 重要：角色区分规则
- **"对方"**：指聊天记录中被分析的对象，即你需要进行画像分析的目标人物。
- **"我"**：指发送消息的我自己，是用户本人，这些信息用于理解"对方"的互动对象和环境。
- **你的分析任务**：仅针对"对方"的行为特征进行分析，"我"的发言仅作为上下文参考。
- **聊天数据格式**: 每条聊天记录包含发送时间、发送者（"我"或"对方"）和消息内容，请严格按照这个顺序进行阅读，不要互换发言角色。

## 分析原则
1. 只基于"对方"的发言内容分析其性格特征、行为偏好和思维方式
2. "我"的发言用于理解对话语境和"对方"的回应模式
3. 如果某些行为特征在"我"身上更明显，请明确指出这不是"对方"的特征

请根据提供的聊天记录，从以下四个维度对"对方"进行深度分析：

## 一、核心特质维度
分析内容包括：
- 人格倾向：理性vs感性、内向vs外向、计划性vs随性
- 处事风格：责任态度、抗压能力、决策模式

## 二、行为偏好维度
分析内容包括：
- 兴趣爱好与关注领域（高频话题、投入程度）
- 明确的喜恶倾向
- 生活习惯细节（作息节奏、消费观念、信息获取方式）

## 三、社交互动维度
分析内容包括：
- 沟通习惯（主动/被动、表达风格、反馈效率）
- 互动态度（共情能力、分享欲、边界感）
- 协作倾向

## 四、认知思维维度
分析内容包括：
- 知识储备与视野
- 价值观取向

请严格按照以下JSON格式返回分析结果，不要包含任何Markdown标记：

{
  "core_traits": {
    "rationality": "理性程度描述",
    "introversion": "内向程度描述",
    "planning": "计划性描述",
    "responsibility": "责任态度描述",
    "stress_resistance": "抗压能力描述",
    "decision_style": "决策风格描述"
  },
  "behavior_preferences": {
    "high_frequency_topics": ["话题1", "话题2", "话题3"],
    "interests": ["兴趣1", "兴趣2"],
    "hobbies": ["爱好1", "爱好2"],
    "preferences": "明确偏好描述",
    "avoidances": "回避事项描述",
    "lifestyle": "生活习惯描述"
  },
  "social_interaction": {
    "initiative": "主动性描述",
    "expression_style": "表达风格描述",
    "response_pattern": "反馈效率描述",
    "empathy": "共情能力描述",
    "sharing_willingness": "分享欲描述",
    "boundary_awareness": "边界感描述",
    "collaboration_style": "协作风格描述"
  },
  "cognitive_thinking": {
    "knowledge_depth": "知识深度描述",
    "knowledge_breadth": "知识广度描述",
    "values": "价值观描述",
    "principles": "底线原则描述"
  },
  "summary": "一句话总结这个人的特点（如：理性的技术宅、热心的倾听者）",
  "interests": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"],
  "dos_and_donts": {
    "dos": ["应该做的事1", "应该做的事2"],
    "donts": ["不应该做的事1", "不应该做的事2"]
  },
  "topic_suggestions": ["话题推荐1", "话题推荐2", "话题推荐3"],
  "gift_suggestions": ["礼物建议1", "礼物建议2"]
}

请确保：
1. 分析基于"对方"聊天记录中的真实言行，而不是主观推测
2. 避免过度标签化，给出客观的描述
3. 如果某些信息不足以得出结论，请如实说明
4. JSON格式必须严格正确，可以被Python json.loads()解析
5. 话题推荐应该基于"对方"的高频话题和兴趣爱好
6. 礼物建议应该考虑"对方"的实际需求和兴趣方向
7. 如果发现某些行为特征更像是"我"的，请在相应描述中说明
"""
def get_ai_analysis(chat_content, api_key=None):
    if not api_key:
        api_key = Config.VOLCANO_ARK_API_KEY
    
    if not api_key:
        return {"error": "未配置API密钥，请设置VOLCANO_ARK_API_KEY环境变量"}
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {"role": "system", "content": AI_SYSTEM_PROMPT},
        {"role": "user", "content": f"请分析以下聊天记录：\n\n{chat_content}"}
    ]
    
    payload = {
        "model": Config.AI_MODEL_ID,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            f"{Config.VOLCANO_ARK_ENDPOINT}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            try:
                json_content = json.loads(content)
                return json_content
            except json.JSONDecodeError:
                return {"raw_response": content}
        else:
            return {"error": f"API调用失败: {response.status_code}, {response.text}"}
    
    except requests.exceptions.RequestException as e:
        return {"error": f"网络请求错误: {str(e)}"}

def parse_ai_response(analysis_result):
    if "error" in analysis_result:
        return analysis_result
    
    parsed = {}
    
    if "raw_response" in analysis_result:
        try:
            content = analysis_result["raw_response"]
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                parsed = json.loads(json_str)
        except:
            pass
    elif "result" in analysis_result:
        parsed = analysis_result["result"]
    
    required_fields = ['core_traits', 'behavior_preferences', 'social_interaction', 'cognitive_thinking', 'summary', 'interests', 'dos_and_donts']
    
    defaults = {
        'core_traits': {},
        'behavior_preferences': {},
        'social_interaction': {},
        'cognitive_thinking': {},
        'summary': '',
        'interests': [],
        'dos_and_donts': {}
    }
    
    for field in required_fields:
        if field not in parsed or not parsed[field] or parsed[field] == {} or parsed[field] == []:
            parsed[field] = defaults.get(field, {} if field != 'summary' and field != 'interests' else ([] if field == 'interests' else ''))
    
    return parsed

def stream_ai_analysis(chat_content, api_key=None):
    if not api_key:
        api_key = Config.VOLCANO_ARK_API_KEY
    
    if not api_key:
        yield {"error": "未配置API密钥，请设置VOLCANO_ARK_API_KEY环境变量"}
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {"role": "system", "content": AI_SYSTEM_PROMPT},
        {"role": "user", "content": f"请分析以下聊天记录：\n\n{chat_content}"}
    ]
    
    payload = {
        "model": Config.AI_MODEL_ID,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7,
        "stream": True
    }
    
    try:
        response = requests.post(
            f"{Config.VOLCANO_ARK_ENDPOINT}/chat/completions",
            headers=headers,
            json=payload,
            timeout=180,
            stream=True
        )
        
        if response.status_code != 200:
            yield {"error": f"API调用失败: {response.status_code}, {response.text}"}
            return
        
        total_tokens = 0
        completion_tokens = 0
        content = ""
        content_length = 0
        chunk_count = 0
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data != '[DONE]':
                        try:
                            chunk = json.loads(data)
                            chunk_count += 1
                            
                            if 'usage' in chunk and chunk['usage']:
                                total_tokens = chunk['usage'].get('total_tokens', 0)
                                completion_tokens = chunk['usage'].get('completion_tokens', 0)
                            
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                chunk_content = delta.get('content', '')
                                if chunk_content:
                                    content += chunk_content
                                    content_length += len(chunk_content)
                                    yield {
                                        "type": "content_update",
                                        "content": chunk_content,
                                        "total_length": content_length,
                                        "total_tokens": total_tokens,
                                        "completion_tokens": completion_tokens
                                    }
                        except json.JSONDecodeError:
                            continue
        
        try:
            json_content = json.loads(content)
            yield {"result": json_content, "total_tokens": total_tokens, "completion_tokens": completion_tokens}
        except json.JSONDecodeError:
            yield {"raw_response": content, "total_tokens": total_tokens, "completion_tokens": completion_tokens}
    
    except requests.exceptions.RequestException as e:
        yield {"error": f"网络请求错误: {str(e)}"}
