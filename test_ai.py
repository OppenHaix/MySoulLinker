"""
AI API 测试用例
完全还原程序中的AI分析过程
"""
import json
import sys
import requests
from config import Config

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

请严格按照以下JSON格式返回分析结果，不要包含任何Markdown标记，关于话题兴趣爱好等个数只是列举，根据情况可以返回更多个：

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


def get_api_headers():
    api_key = Config.VOLCANO_ARK_API_KEY
    if not api_key:
        raise ValueError("未配置 VOLCANO_ARK_API_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


def build_request_payload(chat_content):
    messages = [
        {"role": "system", "content": AI_SYSTEM_PROMPT},
        {"role": "user", "content": f"请分析以下聊天记录：\n\n{chat_content}"}
    ]
    return {
        "model": Config.AI_MODEL_ID,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7
    }


def parse_response(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end != -1:
            return json.loads(content[start:end])
        return {"raw_response": content}


def test_non_streaming(chat_content):
    print("=" * 60)
    print("非流式 AI 分析测试")
    print("=" * 60)
    print(f"聊天记录长度: {len(chat_content)} 字符")
    print("=" * 60)

    headers = get_api_headers()
    payload = build_request_payload(chat_content)

    print("\n发送请求到:", Config.VOLCANO_ARK_ENDPOINT)
    print("使用模型:", Config.AI_MODEL_ID)
    print("\nSystem Prompt 长度:", len(AI_SYSTEM_PROMPT), "字符")
    print("-" * 60)

    try:
        response = requests.post(
            f"{Config.VOLCANO_ARK_ENDPOINT}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )

        print(f"\n响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print("\n" + "-" * 60)
            print("AI原始回复:")
            print("-" * 60)
            print(content)

            parsed = parse_response(content)
            print("\n" + "=" * 60)
            print("解析后的结果:")
            print("=" * 60)
            print(json.dumps(parsed, ensure_ascii=False, indent=2))

            if 'usage' in result:
                print("\n" + "=" * 60)
                print("Token使用情况:")
                print(f"  提示Token: {result['usage'].get('prompt_tokens', 'N/A')}")
                print(f"  完成Token: {result['usage'].get('completion_tokens', 'N/A')}")
                print(f"  总Token: {result['usage'].get('total_tokens', 'N/A')}")

            return parsed
        else:
            print(f"\n请求失败:")
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None

    except Exception as e:
        print(f"\n发生错误: {e}")
        return None


def test_streaming(chat_content):
    print("=" * 60)
    print("流式 AI 分析测试")
    print("=" * 60)
    print(f"聊天记录长度: {len(chat_content)} 字符")
    print("=" * 60)

    headers = get_api_headers()
    payload = build_request_payload(chat_content)
    payload["stream"] = True

    print("\n发送流式请求...")
    print("-" * 60)

    try:
        response = requests.post(
            f"{Config.VOLCANO_ARK_ENDPOINT}/chat/completions",
            headers=headers,
            json=payload,
            timeout=180,
            stream=True
        )

        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            print("\n流式内容接收中:")
            print("-" * 60)

            total_tokens = 0
            completion_tokens = 0
            content = ""
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
                                        print(chunk_content, end='', flush=True)
                            except json.JSONDecodeError:
                                continue

            print("\n")
            print("=" * 60)
            print(f"收到 {chunk_count} 个数据块")
            print(f"总Token: {total_tokens}, 完成Token: {completion_tokens}")
            print("=" * 60)

            parsed = parse_response(content)
            print("\n解析后的结果:")
            print(json.dumps(parsed, ensure_ascii=False, indent=2))

            return parsed
        else:
            print(f"\n请求失败: {response.status_code}")
            print(response.text)
            return None

    except Exception as e:
        print(f"\n发生错误: {e}")
        return None


def load_chat_content_from_db(contact_id):
    """从数据库加载指定联系人的聊天记录"""
    from app import app, db
    from database.models import Contact, ChatLog

    with app.app_context():
        contact = Contact.query.get(contact_id)
        if not contact:
            print(f"联系人 {contact_id} 不存在")
            return None

        chat_logs = ChatLog.query.filter_by(contact_id=contact_id).order_by(
            ChatLog.chat_date, ChatLog.created_at
        ).all()

        if not chat_logs:
            print("没有找到聊天记录")
            return None
        # 这里改过
        chat_content = '\n'.join([
            f"[{log.chat_date}]【我】{log.content}" if log.speaker == '我' else f"[{log.chat_date}]【对方】{log.content}"
            for log in chat_logs
        ])

        print(f"加载了 {len(chat_logs)} 条聊天记录")
        print(f"对方消息: {sum(1 for log in chat_logs if log.speaker == '对方')}")
        print(f"我的消息: {sum(1 for log in chat_logs if log.speaker == '我')}")
        print("-" * 60)

        return chat_content


def print_chat_preview(chat_content, max_lines=20):
    """打印聊天记录预览"""
    print("\n聊天记录预览 (前20行):")
    print("-" * 60)
    lines = chat_content.split('\n')
    for i, line in enumerate(lines[:max_lines], 1):
        print(f"{i:3d}. {line}")
    if len(lines) > max_lines:
        print(f"... 共 {len(lines)} 行")
    print("-" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='AI API 测试工具')
    parser.add_argument('--stream', action='store_true', help='使用流式模式')
    parser.add_argument('--contact', type=int, help='从数据库加载指定联系人的聊天记录')
    parser.add_argument('--text', type=str, help='使用提供的文本作为聊天记录')
    args = parser.parse_args()

    if args.contact:
        chat_content = load_chat_content_from_db(args.contact)
        if not chat_content:
            return
    elif args.text:
        chat_content = args.text
    else:
        chat_content = """
[2024-01-01 10:00]【对方】你好！今天天气真好，适合出去玩玩
[2024-01-01 10:01]【我】是啊，你平时喜欢做什么呢
[2024-01-01 10:02]【对方】我比较喜欢安静在家里看书
[2024-01-01 10:03]【我】看什么类型的书？
[2024-01-01 10:04]【对方】我喜欢推理小说，特别是东野圭吾的
[2024-01-01 10:05]【我】我也喜欢！你看过解忧杂货店吗
[2024-01-01 10:06]【对方】看过看过，特别温暖的故事
[2024-01-01 10:07]【我】对的，感觉作者很细腻
[2024-01-01 10:08]【对方】是啊，我喜欢他写的每一本书
[2024-01-01 10:09]【我】下次借给你
[2024-01-01 10:10]【对方】太好了！谢谢~

[2024-01-02 09:00]【对方】早上好！今天要降温了
[2024-01-02 09:01]【我】真的吗？我穿少了一点
[2024-01-02 09:02]【对方】记得多穿点，别感冒了
[2024-01-02 09:03]【我】好哒，谢谢提醒
[2024-01-02 09:04]【对方】不客气~

[2024-01-03 20:00]【对方】在干嘛呢
[2024-01-03 20:01]【我】在加班，好累
[2024-01-03 20:02]【对方】辛苦了，要注意身体啊
[2024-01-03 20:03]【我】谢谢，你真好
[2024-01-03 20:04]【对方】哈哈应该的~

[2024-01-04 15:00]【对方】我发现一个好吃的餐厅
[2024-01-04 15:01]【我】在哪里？改天一起去
[2024-01-04 15:02]【对方】在市中心，下次约个时间？
[2024-01-04 15:03]【我】好啊，这周六怎么样
[2024-01-04 15:04]【对方】可以啊，我没问题
        """

    print_chat_preview(chat_content)

    if args.stream:
        test_streaming(chat_content)
    else:
        test_non_streaming(chat_content)


if __name__ == "__main__":
    main()
