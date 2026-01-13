# MySoulLinker - 社交关系分析与联系人画像系统

在信息洪流中，我们常常遗忘那些闪光的细节。**MySoulLinker** 不仅仅是一个工具，它是你的社交记忆宫殿。通过 AI 深度解析聊天记录，我们将碎片化的对话重塑为立体的**人格画像**与**情感图谱**。

## 💡 项目背景

我们都有不同的特点——性格、喜好、与相处时的注意事项，以及星座、MBTI 等性格信息。但在信息爆炸的时代，难免会遗忘这些重要的细节。

**MySoulLinker** 的诞生源于一个简单的想法：能不能有一个系统，帮助我们记录、整理和分析这些社交关系？

这个项目的灵感来自于一次与 **小杨梅** 的聊天。在交谈中，我意识到我们往往会忽略身边人的独特之处，也很难记住与每个人相处的最佳方式。

于是第二天，我决定动手实现这个想法——一个可以帮助人们更好地理解和管理社交关系的系统。

### 核心功能

1. **记录** - 手动整理聊天记录，添加日期和标注
2. **分析** - 利用 AI 深度分析联系人性格特征
3. **存储** - 将分析结果结构化保存
4. **展示** - 可视化展示分析结论
5. **导出** - 支持多种格式导出，包括可视化海报

这不是一个自动抓取数据的工具，而是一个**个人社交关系管理工具**——帮助你用心经营每一段值得珍惜的关系。

## 📌 项目概述

MySoulLinker 是一款专为个人社交管理设计的工具，它能够：

- **联系人管理** - 添加、编辑、删除联系人，设置头像、标签和备注
- **聊天记录分析** - 导入聊天记录，系统自动分析联系人性格特征
- **AI 智能画像** - 利用大语言模型深度分析核心特质、行为偏好、社交模式和思维方式
- **可视化统计** - 展示联系人活跃度、消息分布、关系趋势等数据
- **多格式导出** - 支持导出聊天记录和分析报告为 Excel、CSV、JSON、PDF 等格式

## 🏗️ 技术架构

| 层级 | 技术选型 |
|------|----------|
| 后端框架 | Flask 3.0.0 |
| 数据库 | SQLite + Flask-SQLAlchemy 3.1.1 |
| 数据处理 | Pandas 2.1.3 |
| Excel 处理 | openpyxl 3.1.2 |
| HTTP 请求 | requests 2.31.0 |
| AI 服务 | 火山引擎 API (Doubao 模型) |
| 前端模板 | Jinja2 |

## 📁 项目结构

```
MySoulLinker_v1.0/
├── app.py                    # Flask 主应用入口
├── config.py                 # 配置文件（数据库、AI API 等）
├── requirements.txt          # Python 依赖列表
├── migrate_fields.py         # 数据库迁移脚本
├── check_db.py               # 数据库检查工具
├── test_ai.py                # AI 功能测试脚本
├── seed_data.py              # 测试数据填充脚本
├── README.md                 # 项目说明文档
├── .gitignore                # Git 忽略配置
│
├── database/
│   ├── __init__.py           # 数据库模块初始化
│   └── models.py             # 数据模型定义
│       ├── Contact           # 联系人模型
│       ├── ChatLog           # 聊天记录模型
│       └── AnalysisResult    # 分析结果模型
│
├── utils/
│   ├── __init__.py           # 工具模块初始化
│   ├── ai.py                 # AI 分析模块
│   │   ├── get_ai_analysis()           # 同步 AI 分析
│   │   ├── stream_ai_analysis()        # 流式 AI 分析
│   │   └── parse_ai_response()         # 解析 AI 响应
│   │
│   └── exporter.py           # 数据导出模块
│       ├── export_chat_logs_to_csv()   # 导出聊天记录为 CSV
│       ├── export_chat_logs_to_excel() # 导出聊天记录为 Excel
│       ├── export_analysis_to_excel()  # 导出分析报告为 Excel
│       ├── export_analysis_to_json()   # 导出分析报告为 JSON
│       ├── export_analysis_to_pdf()    # 导出分析报告为 PDF
│       └── generate_summary_report()   # 生成汇总报告
│
└── templates/                # HTML 模板文件
    ├── base.html             # 基础模板
    ├── index.html            # 联系人列表页
    ├── home.html             # 数据统计首页
    ├── labeling.html         # 聊天记录标注页
    ├── profile.html          # 联系人详情页
    ├── export.html           # 数据导出页
    ├── landing.html          # 登录页
    └── redirect.html         # 重定向页
```

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows / macOS / Linux

### 安装步骤

1. **克隆项目**

   ```bash
   git clone <your-repo-url>
   cd MySoulLinker_v1.0
   ```

2. **创建虚拟环境**（可选但推荐）

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**（可选）

   ```bash
   # 设置密钥
   export SECRET_KEY="your-secret-key"
   
   # 火山引擎 API Key（用于 AI 分析功能）
   export VOLCANO_ARK_API_KEY="your-api-key"
   ```

5. **启动应用**

   ```bash
   python app.py
   ```

6. **访问应用**

   打开浏览器访问 http://localhost:5000

## 📖 使用指南

### 1. 添加联系人

首次访问需要输入用户名，然后可以开始添加联系人：

- 点击"添加联系人"按钮
- 填写联系人姓名
- 可选：设置头像、标签、备注信息

### 2. 导入聊天记录

1. 进入联系人详情页
2. 点击"添加聊天记录"
3. 输入聊天日期
4. 逐条添加聊天内容，区分"我"和"对方"
5. 保存记录

### 3. AI 性格分析

1. 确保联系人有足够的聊天记录（建议 30 条以上）
2. 进入联系人详情页
3. 点击"开始分析"按钮
4. 等待 AI 完成分析（支持流式输出，实时显示进度）

**分析维度包括：**

| 维度 | 内容 |
|------|------|
| 核心特质 | 理性/感性、内向/外向、计划性、责任态度、抗压能力、决策风格 |
| 行为偏好 | 高频话题、兴趣爱好、生活习惯、消费观念 |
| 社交互动 | 主动性、表达风格、共情能力、分享欲、边界感 |
| 认知思维 | 知识深度、知识广度、价值观、底线原则 |

**AI 还将提供：**
- 📝 一句话性格总结
- 🎯 话题推荐（基于聊天内容）
- 🎁 礼物建议
- ✅ 相处指南（应该做/不应该做）

### 4. 数据导出

支持批量导出多个格式：

**聊天记录导出：**
- CSV 格式
- Excel 格式 (.xlsx)
- ZIP 压缩包（包含多种格式）

**分析报告导出：**
- Excel 格式（包含摘要、兴趣关键词、性格特质、相处指南）
- JSON 格式（结构化数据）
- PDF/TXT 格式（可打印的文档）

### 5. 数据统计

首页展示整体数据概览：

- 📊 总联系人数量
- 💬 总消息数量
- 📈 本月新增联系人
- 🔥 活跃关系（30天内有互动的联系人）
- 📉 分析覆盖率

**活跃度图表：** 展示最近 30 天的消息分布趋势

## ⚙️ 配置说明

### API Key 配置（必须）

⚠️ **重要：** 本项目使用火山引擎的 AI 服务进行分析功能，**必须配置 API Key 才能使用 AI 分析功能**。

**获取 API Key：**
1. 注册并登录 [火山引擎控制台](https://www.volcengine.com/)
2. 开通 AI 服务，获取 API Key

**配置步骤：**

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 API Key：
```env
VOLCANO_ARK_API_KEY=your-api-key-here
SECRET_KEY=dev-secret-key-change-in-production
```

> 📁 `.env` 文件已被 `.gitignore` 忽略，不会提交到 GitHub

### 配置文件 (config.py)

```python
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    # 密钥配置（从环境变量读取）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-mysoullinker'
    VOLCANO_ARK_API_KEY = os.environ.get('VOLCANO_ARK_API_KEY')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(DATABASE_DIR, 'social.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 火山引擎 AI 配置
    VOLCANO_ARK_ENDPOINT = 'https://ark.cn-beijing.volces.com/api/v3'
    AI_MODEL_ID = 'doubao-seed-1-6-251015'
    
    # 文件上传/导出配置
    UPLOAD_FOLDER = 'uploads'
    EXPORT_FOLDER = 'exports'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask 密钥 | dev-key-for-mysoullinker |
| `VOLCANO_ARK_API_KEY` | 火山引擎 API Key | 必填，无默认值 |
| `DATABASE_URI` | 数据库连接字符串 | SQLite 本地文件 |

## 📊 数据模型

### Contact (联系人)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 联系人姓名 |
| avatar | String(255) | 头像 URL |
| notes | Text | 备注信息 |
| tags | String(500) | 标签（逗号分隔） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**关联关系：**
- 一对多：ChatLog（聊天记录）
- 一对一：AnalysisResult（分析结果）

**计算属性：**
- `sessions`: 会话次数（不同聊天日期数）
- `active_days`: 活跃天数
- `has_analysis`: 是否已完成分析

### ChatLog (聊天记录)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| contact_id | Integer | 关联联系人 ID |
| speaker | String(20) | 发言者（"我" 或 "对方"） |
| content | Text | 消息内容 |
| chat_date | Date | 聊天日期 |
| created_at | DateTime | 创建时间 |

### AnalysisResult (分析结果)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| contact_id | Integer | 关联联系人 ID（唯一） |
| core_traits | Text | 核心特质（JSON） |
| behavior_preferences | Text | 行为偏好（JSON） |
| social_interaction | Text | 社交互动（JSON） |
| cognitive_thinking | Text | 认知思维（JSON） |
| summary | Text | 性格总结 |
| interests | Text | 兴趣关键词（JSON 数组） |
| dos_and_donts | Text | 相处指南（JSON） |
| topic_suggestions | Text | 话题推荐（JSON 数组） |
| gift_suggestions | Text | 礼物建议（JSON 数组） |
| raw_response | Text | AI 原始响应 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 🔌 API 接口

### 联系人管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/contacts` | 获取所有联系人列表 |
| POST | `/api/contacts` | 创建新联系人 |
| GET | `/api/contacts/<id>` | 获取单个联系人详情 |
| PUT | `/api/contacts/<id>` | 更新联系人信息 |
| DELETE | `/api/contacts/<id>` | 删除联系人 |

### 聊天记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/contacts/<id>/chat-logs` | 获取联系人的聊天记录 |
| POST | `/api/contacts/<id>/chat-logs` | 添加聊天记录 |

### AI 分析

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/contacts/<id>/analyze` | 同步 AI 分析 |
| POST | `/api/contacts/<id>/analyze/stream` | 流式 AI 分析（推荐） |
| POST | `/api/contacts/<id>/analyze-selected` | 分析选中的消息 |
| GET | `/api/contacts/<id>/analysis` | 获取分析结果 |

### 页面路由

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 首页/登录页 |
| GET | `/home` | 数据统计首页 |
| GET | `/contacts` | 联系人列表页 |
| GET | `/labeling/<id>` | 聊天记录标注页 |
| GET | `/profile/<id>` | 联系人详情页 |
| GET | `/export` | 数据导出页 |

## 🛠️ 开发工具

### 数据库工具

```bash
# 检查数据库状态
python check_db.py

# 字段迁移
python migrate_fields.py

# 填充测试数据
python seed_data.py

# 测试 AI 功能
python test_ai.py
```

### 项目计划

项目开发计划文档位于：`.trae/documents/plan_20260112_072009.md`

## 📦 依赖说明

```
Flask==3.0.0              # Web 框架
Flask-SQLAlchemy==3.1.1   # ORM 数据库操作
pandas==2.1.3             # 数据分析
openpyxl==3.1.2           # Excel 文件处理
requests==2.31.0          # HTTP 请求（用于调用 AI API）
```

## 📦 依赖说明

```
Flask==3.0.0              # Web 框架
Flask-SQLAlchemy==3.1.1   # ORM 数据库操作
pandas==2.1.3             # 数据分析
openpyxl==3.1.2           # Excel 文件处理
requests==2.31.0          # HTTP 请求（用于调用 AI API）
```

## 📝 更新日志

### v1.0 (2025-01)
- ✨ 初始版本发布
- 📇 联系人管理功能
- 💬 聊天记录导入
- 🤖 AI 性格分析（流式输出）
- 📊 数据统计与可视化
- 📤 多格式数据导出

## 📄 许可证

MIT License

## 👨‍💻 作者

[OppenHaix](https://github.com/OppenHaix)

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - 优秀的 Python Web 框架
- [火山引擎](https://www.volcengine.com/) - 提供 AI 能力支持
- [OpenAI](https://openai.com/) - AI Prompt 设计参考
