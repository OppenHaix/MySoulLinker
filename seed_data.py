from flask import Flask
from datetime import datetime, timedelta
from database.models import db, Contact, ChatLog, AnalysisResult
import json

def create_sample_data():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)

    with app.app_context():
        db.create_all()

        contacts_data = [
            {
                "name": "张明",
                "avatar": "",
                "notes": "大学室友，现在在互联网公司做产品经理",
                "tags": "朋友,大学同学",
                "chat_logs": [
                    {"speaker": "张明", "content": "周末有空吗？一起出来吃个饭啊", "days_ago": 3},
                    {"speaker": "我", "content": "好啊，去哪儿吃？", "days_ago": 3},
                    {"speaker": "张明", "content": "我知道一家新开的火锅店，味道超棒", "days_ago": 3},
                    {"speaker": "我", "content": "行啊，那就周六晚上吧", "days_ago": 3},
                    {"speaker": "张明", "content": "对了，你最近工作怎么样？", "days_ago": 5},
                    {"speaker": "我", "content": "还行吧，就是项目赶得比较紧", "days_ago": 5},
                    {"speaker": "张明", "content": "保重身体啊，别太拼了", "days_ago": 5},
                    {"speaker": "我", "content": "知道啦，你也是", "days_ago": 5},
                    {"speaker": "张明", "content": "上周看的那部电影怎么样？", "days_ago": 7},
                    {"speaker": "我", "content": "挺好看的，剧情很紧凑", "days_ago": 7},
                    {"speaker": "张明", "content": "我也想去看，等有空约一个", "days_ago": 7},
                ],
                "analysis": {
                    "core_traits": json.dumps({
                        "rationality": "做事有计划，但也不失灵活性",
                        "introversion": "偏外向，喜欢社交和聚会",
                        "planning": "习惯提前规划，但也能随性应对变化",
                        "responsibility": "对朋友真诚，答应的事会做到",
                        "stress_resistance": "心态较好，能合理调节压力",
                        "decision_style": "偏向民主协商，会听取他人意见"
                    }, ensure_ascii=False),
                    "behavior_preferences": json.dumps({
                        "high_frequency_topics": ["电影", "美食", "工作", "聚会"],
                        "interests": ["美食探店", "电影", "运动"],
                        "hobbies": ["篮球", "看剧"],
                        "preferences": "喜欢新鲜事物，热衷于探索新店",
                        "avoidances": "不太喜欢太正式的场合",
                        "lifestyle": "工作之余注重生活品质，周末喜欢放松"
                    }, ensure_ascii=False),
                    "social_interaction": json.dumps({
                        "initiative": "经常主动发起邀约，维护朋友关系",
                        "expression_style": "说话直接热情，善于表达",
                        "response_pattern": "回复及时，互动积极",
                        "empathy": "能理解朋友的处境和感受",
                        "sharing_willingness": "乐于分享生活和经历",
                        "boundary_awareness": "尊重他人边界，不过度干涉",
                        "collaboration_style": "配合度高，善于协调"
                    }, ensure_ascii=False),
                    "cognitive_thinking": json.dumps({
                        "knowledge_depth": "知识面广但不精",
                        "knowledge_breadth": "对生活娱乐类信息关注较多",
                        "values": "重视友情和生活平衡",
                        "principles": "为人正直，重承诺"
                    }, ensure_ascii=False),
                    "summary": "热情开朗的生活家，善于维护社交关系",
                    "interests": json.dumps(["美食", "电影", "篮球", "旅行", "音乐"], ensure_ascii=False),
                    "dos_and_donts": json.dumps({
                        "dos": ["约他尝试新餐厅", "周末一起看电影", "聊生活话题"],
                        "donts": ["让他做太正式的决定", "忽视他的邀约"]
                    }, ensure_ascii=False),
                    "topic_suggestions": json.dumps([
                        "最近上映的电影",
                        "新开的餐厅或美食",
                        "周末活动安排",
                        "工作近况",
                        "篮球或运动相关"
                    ], ensure_ascii=False),
                    "gift_suggestions": json.dumps([
                        "电影票或演出票",
                        "运动装备",
                        "美食礼券",
                        "高品质蓝牙耳机"
                    ], ensure_ascii=False)
                }
            },
            {
                "name": "李雪",
                "avatar": "",
                "notes": "公司同事，负责设计工作，非常有艺术气质",
                "tags": "同事,设计",
                "chat_logs": [
                    {"speaker": "我", "content": "那个项目的设计稿什么时候能给我？", "days_ago": 2},
                    {"speaker": "李雪", "content": "大概周四能完成，这两天在赶另一个需求", "days_ago": 2},
                    {"speaker": "我", "content": "好的，不急，质量第一", "days_ago": 2},
                    {"speaker": "李雪", "content": "谢谢理解！对了，我最近在学水彩画", "days_ago": 4},
                    {"speaker": "我", "content": "哇，好厉害！能看看你的作品吗", "days_ago": 4},
                    {"speaker": "李雪", "content": "还在练习阶段，等有成品了分享给你", "days_ago": 4},
                    {"speaker": "我", "content": "太期待了，感觉你做什么都很认真", "days_ago": 4},
                    {"speaker": "李雪", "content": "哈哈谢谢，主要是很喜欢嘛", "days_ago": 4},
                    {"speaker": "李雪", "content": "今天看到一款超美的配色，分享给你看看", "days_ago": 6},
                    {"speaker": "我", "content": "这个颜色搭配太舒服了，什么项目用的？", "days_ago": 6},
                    {"speaker": "李雪", "content": "是一个个人练习作品，想做一个极简风格的app界面", "days_ago": 6},
                ],
                "analysis": {
                    "core_traits": json.dumps({
                        "rationality": "设计决策凭直觉，但有扎实理论基础",
                        "introversion": "内心丰富但表面安静",
                        "planning": "工作有规划，但创作随性",
                        "responsibility": "对作品质量要求高，有完美主义倾向",
                        "stress_resistance": "对认可有较强需求，抗压能力中等",
                        "decision_style": "追求美感，决策时注重细节"
                    }, ensure_ascii=False),
                    "behavior_preferences": json.dumps({
                        "high_frequency_topics": ["设计", "艺术", "生活美学"],
                        "interests": ["绘画", "摄影", "设计美学", "看展"],
                        "hobbies": ["水彩画", "看设计类书籍"],
                        "preferences": "追求生活品质，注重细节美感",
                        "avoidances": "不喜欢嘈杂环境和低级趣味",
                        "lifestyle": "生活简约但有格调，注重精神世界"
                    }, ensure_ascii=False),
                    "social_interaction": json.dumps({
                        "initiative": "分享欲强，但较少主动发起社交邀约",
                        "expression_style": "委婉含蓄，善于用作品表达",
                        "response_pattern": "思考后回复，回复质量高",
                        "empathy": "对美有敏锐感知，对人也有一定共情",
                        "sharing_willingness": "乐于分享美好的事物",
                        "boundary_awareness": "有清晰的个人空间需求",
                        "collaboration风格": "配合度高，但需要一定自主权"
                    }, ensure_ascii=False),
                    "cognitive_thinking": json.dumps({
                        "knowledge_depth": "设计领域专业素养高",
                        "knowledge_breadth": "艺术人文类知识丰富",
                        "values": "追求美和真诚",
                        "principles": "对作品负责，不敷衍"
                    }, ensure_ascii=False),
                    "summary": "追求美感的安静创作者，有自己的精神世界",
                    "interests": json.dumps(["设计", "绘画", "摄影", "艺术展", "美学"], ensure_ascii=False),
                    "dos_and_donts": json.dumps({
                        "dos": ["欣赏她的作品", "聊设计艺术话题", "给她足够创作空间"],
                        "donts": ["催太急", "对她的作品敷衍评价"]
                    }, ensure_ascii=False),
                    "topic_suggestions": json.dumps([
                        "设计趋势和灵感",
                        "艺术展览",
                        "水彩画或绘画技巧",
                        "生活美学",
                        "摄影作品分享"
                    ], ensure_ascii=False),
                    "gift_suggestions": json.dumps([
                        "高品质画材",
                        "设计类书籍",
                        "艺术展览门票",
                        "简约风格的家居装饰"
                    ], ensure_ascii=False)
                }
            },
            {
                "name": "王强",
                "avatar": "",
                "notes": "发小，现在在老家发展，偶尔联系",
                "tags": "发小,家人朋友",
                "chat_logs": [
                    {"speaker": "王强", "content": "过年回家吗？", "days_ago": 10},
                    {"speaker": "我", "content": "回的，你呢？", "days_ago": 10},
                    {"speaker": "王强", "content": "我也回，到时候聚聚", "days_ago": 10},
                    {"speaker": "我", "content": "必须的，好久没见了", "days_ago": 10},
                    {"speaker": "王强", "content": "对了，你还记得小时候一起玩的那个谁吗", "days_ago": 15},
                    {"speaker": "我", "content": "记得啊，怎么了？", "days_ago": 15},
                    {"speaker": "王强", "content": "听说他也回老家工作了", "days_ago": 15},
                    {"speaker": "我", "content": "这么巧，有机会一起聚聚", "days_ago": 15},
                    {"speaker": "王强", "content": "最近工作怎么样？", "days_ago": 20},
                    {"speaker": "我", "content": "还行吧，你呢？", "days_ago": 20},
                    {"speaker": "王强", "content": "我这边稳定，就是工资一般", "days_ago": 20},
                    {"speaker": "我", "content": "稳定就好，有机会来我这边玩", "days_ago": 20},
                ],
                "analysis": {
                    "core_traits": json.dumps({
                        "rationality": "务实稳重，不追求华而不实",
                        "introversion": "内外向平衡，不张扬",
                        "planning": "追求稳定，计划性强",
                        "responsibility": "对家庭有责任感，踏实可靠",
                        "stress_resistance": "适应力强，能安于现状",
                        "decision_style": "稳健保守，倾向于风险小的选择"
                    }, ensure_ascii=False),
                    "behavior_preferences": json.dumps({
                        "high_frequency_topics": ["家庭", "工作", "老家"],
                        "interests": ["稳定的生活", "家乡"],
                        "hobbies": ["家乡美食", "老友聚会"],
                        "preferences": "喜欢简单稳定的生活",
                        "avoidances": "不喜欢大城市的快节奏",
                        "lifestyle": "注重家庭和生活平衡"
                    }, ensure_ascii=False),
                    "social_interaction": json.dumps({
                        "initiative": "维系老关系，但不热衷拓展新社交",
                        "expression_style": "朴实直接，不拐弯抹角",
                        "response_pattern": "稳定但不算及时",
                        "empathy": "对老朋友很重情义",
                        "sharing_willingness": "分享生活琐事",
                        "boundary_awareness": "边界感不强，比较随意",
                        "collaboration_style": "可靠踏实"
                    }, ensure_ascii=False),
                    "cognitive_thinking": json.dumps({
                        "knowledge_depth": "实用型知识为主",
                        "knowledge_breadth": "对老家和熟悉领域了解深",
                        "values": "重视家庭、友情、稳定",
                        "principles": "踏实本分，不做违规的事"
                    }, ensure_ascii=False),
                    "summary": "务实稳重的顾家型人格，重视老友情谊",
                    "interests": json.dumps(["家乡", "家庭", "老友", "稳定"], ensure_ascii=False),
                    "dos_and_donts": json.dumps({
                        "dos": ["回老家时聚聚", "聊聊家乡和旧事", "保持联系"],
                        "donts": ["对他judge太多", "长时间失联"]
                    }, ensure_ascii=False),
                    "topic_suggestions": json.dumps([
                        "家乡的变化",
                        "小时候的回忆",
                        "家庭近况",
                        "工作发展",
                        "过年聚会安排"
                    ], ensure_ascii=False),
                    "gift_suggestions": json.dumps([
                        "家乡特产",
                        "给家人的礼物",
                        "家乡风味的食品",
                        "体检套餐"
                    ], ensure_ascii=False)
                }
            },
            {
                "name": "陈思",
                "avatar": "",
                "notes": "健身房认识的健身教练，很专业",
                "tags": "健身,朋友",
                "chat_logs": [
                    {"speaker": "陈思", "content": "今天训练感觉怎么样？", "days_ago": 1},
                    {"speaker": "我", "content": "比上次好多了，教练教的动作很有用", "days_ago": 1},
                    {"speaker": "陈思", "content": "那就好，注意休息和饮食", "days_ago": 1},
                    {"speaker": "我", "content": "好的，下次训练什么时候？", "days_ago": 1},
                    {"speaker": "陈思", "content": "周三周六都可以，看你时间", "days_ago": 1},
                    {"speaker": "我", "content": "那就周三吧", "days_ago": 1},
                    {"speaker": "陈思", "content": "对了，最近饮食要注意少油少盐", "days_ago": 3},
                    {"speaker": "我", "content": "收到，是不是也能适当吃点放纵餐？", "days_ago": 3},
                    {"speaker": "陈思", "content": "可以，一周一次没问题", "days_ago": 3},
                    {"speaker": "我", "content": "好的，谢谢教练！", "days_ago": 3},
                    {"speaker": "陈思", "content": "加油，坚持就是胜利", "days_ago": 3},
                    {"speaker": "我", "content": "最近感觉体重没什么变化", "days_ago": 5},
                    {"speaker": "陈思", "content": "正常，体型在变化就好，不要只看体重", "days_ago": 5},
                    {"speaker": "我", "content": "好的，明白了", "days_ago": 5},
                ],
                "analysis": {
                    "core_traits": json.dumps({
                        "rationality": "科学派，相信数据和专业",
                        "introversion": "工作外向，私下偏安静",
                        "planning": "训练计划清晰有条理",
                        "responsibility": "对学员认真负责",
                        "stress_resistance": "能应对各种学员的需求",
                        "decision_style": "专业导向，用数据说话"
                    }, ensure_ascii=False),
                    "behavior_preferences": json.dumps({
                        "high_frequency_topics": ["健身", "饮食", "健康"],
                        "interests": ["健身", "营养学", "运动康复"],
                        "hobbies": ["训练", "研究营养", "自我提升"],
                        "preferences": "追求专业和科学",
                        "avoidances": "不科学的方法和急功近利",
                        "lifestyle": "极度自律，注重健康"
                    }, ensure_ascii=False),
                    "social_interaction": json.dumps({
                        "initiative": "对学员主动关心",
                        "expression风格": "专业简洁，鼓励为主",
                        "response_pattern": "及时专业",
                        "empathy": "理解学员的困难和惰性",
                        "sharing_willingness": "分享健身知识",
                        "boundary_awareness": "专业边界清晰",
                        "collaboration风格": "引导型，帮助学员达成目标"
                    }, ensure_ascii=False),
                    "cognitive_thinking": json.dumps({
                        "knowledge_depth": "健身和营养领域专业",
                        "knowledge_breadth": "了解相关健康知识",
                        "values": "健康第一，科学健身",
                        "原则": "不夸大效果，对学员负责"
                    }, ensure_ascii=False),
                    "summary": "专业负责的健身指导者，自律且追求科学",
                    "interests": json.dumps(["健身", "营养", "健康", "运动", "自律"], ensure_ascii=False),
                    "dos_and_donts": json.dumps({
                        "dos": ["认真执行他的训练计划", "饮食上配合", "有问题及时沟通"],
                        "donts": ["偷懒不训练", "随便吃垃圾食品", "不尊重专业建议"]
                    }, ensure_ascii=False),
                    "topic_suggestions": json.dumps([
                        "健身计划和目标",
                        "饮食营养搭配",
                        "最新的健身趋势",
                        "运动装备推荐",
                        "健康生活方式"
                    ], ensure_ascii=False),
                    "gift_suggestions": json.dumps([
                        "蛋白粉或营养补剂",
                        "高品质运动装备",
                        "运动手表或手环",
                        "健身课程体验券"
                    ], ensure_ascii=False)
                }
            },
            {
                "name": "刘芳",
                "avatar": "",
                "notes": "读书会认识的朋友，很爱看书",
                "tags": "读书,朋友",
                "chat_logs": [
                    {"speaker": "刘芳", "content": "最近在读什么书？", "days_ago": 2},
                    {"speaker": "我", "content": "在读《人类简史》，你呢？", "days_ago": 2},
                    {"speaker": "刘芳", "content": "我在读《百年孤独》，马尔克斯的魔幻现实主义太绝了", "days_ago": 2},
                    {"speaker": "我", "content": "这本我也想看很久了", "days_ago": 2},
                    {"speaker": "刘芳", "content": "读完可以交流一下感想", "days_ago": 2},
                    {"speaker": "我", "content": "好呀，下周读书会讨论什么书？", "days_ago": 4},
                    {"speaker": "刘芳", "content": "讨论《思考，快与慢》，心理学相关的", "days_ago": 4},
                    {"speaker": "我", "content": "这本有点难懂啊", "days_ago": 4},
                    {"speaker": "刘芳", "content": "没关系，大家一起讨论就懂了", "days_ago": 4},
                    {"speaker": "我", "content": "你推荐的那本诗集我买了", "days_ago": 6},
                    {"speaker": "刘芳", "content": "怎么样，喜欢吗？", "days_ago": 6},
                    {"speaker": "我", "content": "很有意境，很喜欢", "days_ago": 6},
                    {"speaker": "刘芳", "content": "我就知道你也会喜欢", "days_ago": 6},
                ],
                "analysis": {
                    "core_traits": json.dumps({
                        "rationality": "理性思考，但也有感性一面",
                        "introversion": "偏内向，享受独处阅读时光",
                        "planning": "阅读有规划，涉猎广泛",
                        "responsibility": "对承诺认真负责",
                        "stress_resistance": "内心平静，抗压能力强",
                        "decision_style": "深思熟虑，有自己的判断"
                    }, ensure_ascii=False),
                    "behavior_preferences": json.dumps({
                        "high_frequency_topics": ["书籍", "阅读", "思考", "文学"],
                        "interests": ["文学", "哲学", "心理学", "诗歌"],
                        "hobbies": ["阅读", "写读书笔记", "参加读书会"],
                        "preferences": "追求精神充实和思想深度",
                        "avoidances": "浅薄无聊的内容",
                        "lifestyle": "简单宁静，注重精神生活"
                    }, ensure_ascii=False),
                    "social_interaction": json.dumps({
                        "initiative": "组织读书会，主动分享",
                        "expression_style": "文雅有深度，善于表达观点",
                        "response_pattern": "认真思考后回复",
                        "empathy": "对人有耐心，能理解不同观点",
                        "sharing_willingness": "乐于推荐书籍和分享读书心得",
                        "boundary_awareness": "尊重他人观点",
                        "collaboration风格": "温和协调，营造良好讨论氛围"
                    }, ensure_ascii=False),
                    "cognitive_thinking": json.dumps({
                        "knowledge_depth": "阅读量大，理解深入",
                        "knowledge_breadth": "涉猎广泛，跨学科阅读",
                        "values": "追求真理和智慧",
                        "原则": "认真对待知识和思考"
                    }, ensure_ascii=False),
                    "summary": "热爱阅读的思考者，精神世界丰富",
                    "interests": json.dumps(["读书", "文学", "哲学", "思考", "诗歌"], ensure_ascii=False),
                    "dos_and_donts": json.dumps({
                        "dos": ["和她讨论书籍和思想", "参加读书会", "认真听她推荐"],
                        "donts": ["敷衍对待阅读话题", "发表浅薄的评论"]
                    }, ensure_ascii=False),
                    "topic_suggestions": json.dumps([
                        "最近读的书",
                        "读书会讨论的话题",
                        "哲学思考",
                        "文学经典",
                        "心理学书籍"
                    ], ensure_ascii=False),
                    "gift_suggestions": json.dumps([
                        "优质书籍",
                        "读书配件（书签、书衣）",
                        "安静的咖啡馆礼券",
                        "手写明信片"
                    ], ensure_ascii=False)
                }
            }
        ]

        for contact_data in contacts_data:
            contact = Contact(
                name=contact_data["name"],
                avatar=contact_data["avatar"],
                notes=contact_data["notes"],
                tags=contact_data["tags"],
                created_at=datetime.utcnow() - timedelta(days=30),
                updated_at=datetime.utcnow()
            )
            db.session.add(contact)
            db.session.flush()

            for log_data in contact_data["chat_logs"]:
                chat_log = ChatLog(
                    contact_id=contact.id,
                    speaker=log_data["speaker"],
                    content=log_data["content"],
                    chat_date=datetime.utcnow().date() - timedelta(days=log_data["days_ago"]),
                    created_at=datetime.utcnow() - timedelta(days=log_data["days_ago"])
                )
                db.session.add(chat_log)

            analysis_data = contact_data["analysis"]
            analysis = AnalysisResult(
                contact_id=contact.id,
                core_traits=analysis_data["core_traits"],
                behavior_preferences=analysis_data["behavior_preferences"],
                social_interaction=analysis_data["social_interaction"],
                cognitive_thinking=analysis_data["cognitive_thinking"],
                summary=analysis_data["summary"],
                interests=analysis_data["interests"],
                dos_and_donts=analysis_data["dos_and_donts"],
                created_at=datetime.utcnow() - timedelta(days=7),
                updated_at=datetime.utcnow()
            )
            db.session.add(analysis)

        db.session.commit()
        print("示例数据创建成功！共创建了 5 个联系人及其相关数据。")

if __name__ == "__main__":
    create_sample_data()
