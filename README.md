# MySoulLinker - 社交关系分析与联系人画像系统

在信息洪流中，我们常常遗忘那些闪光的细节。**MySoulLinker** 不仅仅是一个工具，它是你的社交记忆宫殿。通过 AI 深度解析聊天记录，我们将碎片化的对话重塑为立体的**人格画像**与**情感图谱**。

## 💡 关于这个项目

我们都有不同的特点——性格、喜好、相处时的注意事项。但在信息爆炸的时代，这些细节容易遗忘。

这个想法源于一次与 **小杨梅** 的聊天。我意识到我们常常忽略身边人的独特之处，也很难记住与每个人相处的最佳方式。于是第二天，我决定动手实现这个系统。

### 核心功能

| 功能 | 说明 |
|------|------|
| � 联系人管理 | 添加、编辑、删除联系人，设置头像、标签和备注 |
| 💬 聊天记录整理 | 手动整理聊天记录，添加日期和标注 |
| 🤖 AI 性格分析 | 利用大语言模型深度分析核心特质、行为偏好、社交模式 |
| 📊 数据统计 | 展示联系人活跃度、消息分布、关系趋势 |
| 📤 多格式导出 | 支持 Excel、CSV、JSON、PDF、海报等多种格式 |

> ⚠️ 这是一个**个人社交关系管理工具**，不是自动抓取数据的工具。

---

## � 快速开始

### 1. 环境准备

- Python 3.8+
- Git

### 2. 克隆并安装

```bash
# 克隆项目
git clone https://github.com/OppenHaix/MySoulLinker.git
cd MySoulLinker

# 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制模板
cp .env.example .env

# 编辑配置（必须填入 VOLCANO_ARK_API_KEY）
# 用任意编辑器打开 .env 文件
```

**.env 文件内容：**
```env
# AI 分析必须（注册火山引擎获取）
VOLCANO_ARK_API_KEY=your-api-key-here

# Flask 密钥（可选，有默认值）
SECRET_KEY=dev-secret-key
```

> 📁 `.env` 已被 `.gitignore` 忽略，不会提交到 GitHub

### 4. 启动应用

```bash
python app.py
```

打开浏览器访问 http://localhost:5000

---

## 📖 使用流程

### 第一步：添加联系人

1. 首次访问输入用户名
2. 点击"添加联系人"
3. 填写姓名、头像、标签、备注

### 第二步：整理聊天记录

1. 进入联系人详情页
2. 点击"添加聊天记录"
3. 输入聊天日期
4. 逐条添加消息（区分"我"和"对方"）
5. 保存

### 第三步：AI 性格分析

1. 确保有足够聊天记录（建议 30+ 条）
2. 点击"开始分析"
3. 等待 AI 完成分析（流式输出，实时显示）

**AI 分析内容：**
- 核心特质（理性/感性、内向/外向、抗压能力等）
- 行为偏好（高频话题、兴趣爱好、消费观念）
- 社交互动（主动性、共情能力、边界感）
- 认知思维（价值观、知识深度、底线原则）
- 一句话性格总结
- 话题推荐、礼物建议、相处指南

### 第四步：导出与统计

- **导出**：支持 Excel、CSV、JSON、PDF、海报格式
- **统计**：首页展示总联系人、消息数、活跃关系、分析覆盖率

---

## ⚙️ 配置说明

### 获取 API Key

1. 注册登录 [火山引擎控制台](https://www.volcengine.com/)
2. 开通 AI 服务
3. 复制 API Key 到 `.env` 文件

### 配置文件 (config.py)

```python
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # 密钥（从环境变量读取）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-mysoullinker'
    VOLCANO_ARK_API_KEY = os.environ.get('VOLCANO_ARK_API_KEY')

    # 数据库
    DATABASE_DIR = os.path.join(BASE_DIR, 'database')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(DATABASE_DIR, 'social.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 火山引擎 AI
    VOLCANO_ARK_ENDPOINT = 'https://ark.cn-beijing.volces.com/api/v3'
    AI_MODEL_ID = 'doubao-seed-1-6-251015'

    # 文件上传
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
```

### 环境变量表

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `VOLCANO_ARK_API_KEY` | 火山引擎 API Key | **必填** |
| `SECRET_KEY` | Flask 密钥 | dev-key-for-mysoullinker |
| `DATABASE_URI` | 数据库连接字符串 | SQLite 本地文件 |

---

## 🏗️ 技术架构

| 层级 | 技术 |
|------|------|
| 后端 | Flask 3.0.0 |
| 数据库 | SQLite + Flask-SQLAlchemy |
| 数据处理 | Pandas + openpyxl |
| AI 服务 | 火山引擎 API (Doubao) |
| 前端 | Jinja2 + 原生 JS/CSS |

---

## 📁 项目结构

```
MySoulLinker/
├── app.py                  # Flask 主入口
├── config.py               # 配置文件
├── requirements.txt        # 依赖列表
├── reset_dev.py            # 开发环境重置脚本
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略配置
│
├── database/
│   ├── models.py           # Contact, ChatLog, AnalysisResult
│   └── __init__.py
│
├── utils/
│   ├── ai.py               # AI 分析模块
│   ├── exporter.py         # 数据导出模块
│   └── __init__.py
│
├── static/
│   ├── css/                # 样式文件
│   └── js/                 # 脚本文件
│
└── templates/              # HTML 模板
    ├── base.html
    ├── index.html          # 联系人列表
    ├── home.html           # 数据统计
    ├── labeling.html       # 聊天记录标注
    ├── profile.html        # 联系人详情
    ├── export.html         # 数据导出
    └── landing.html        # 登录页
```

---

## 🔌 API 接口

### 联系人

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/contacts` | 获取列表 |
| POST | `/api/contacts` | 创建联系人 |
| GET | `/api/contacts/<id>` | 获取详情 |
| PUT | `/api/contacts/<id>` | 更新信息 |
| DELETE | `/api/contacts/<id>` | 删除联系人 |

### 聊天记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/contacts/<id>/chat-logs` | 获取聊天记录 |
| POST | `/api/contacts/<id>/chat-logs` | 添加聊天记录 |

### AI 分析

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/contacts/<id>/analyze` | 同步分析 |
| POST | `/api/contacts/<id>/analyze/stream` | 流式分析（推荐） |
| GET | `/api/contacts/<id>/analysis` | 获取分析结果 |

---

## 📊 数据模型

### Contact (联系人)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(100) | 姓名 |
| avatar | String(255) | 头像 URL |
| notes | Text | 备注 |
| tags | String(500) | 标签 |
| created_at | DateTime | 创建时间 |

### ChatLog (聊天记录)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| contact_id | Integer | 关联联系人 |
| speaker | String(20) | 发言者（我/对方） |
| content | Text | 消息内容 |
| chat_date | Date | 聊天日期 |

### AnalysisResult (分析结果)
| 字段 | 类型 | 说明 |
|------|------|------|
| contact_id | Integer | 关联联系人（唯一） |
| core_traits | Text | 核心特质 |
| behavior_preferences | Text | 行为偏好 |
| social_interaction | Text | 社交互动 |
| cognitive_thinking | Text | 认知思维 |
| summary | Text | 性格总结 |
| dos_and_donts | Text | 相处指南 |

---

## 🛠️ 开发工具

```bash
# 重置开发环境（清理测试数据）
python reset_dev.py

# 检查数据库
python check_db.py

# 填充测试数据
python seed_data.py

# 测试 AI 功能
python test_ai.py
```

---

## 📦 依赖

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
pandas==2.1.3
openpyxl==3.1.2
requests==2.31.0
python-dotenv==1.0.0
```

---

## 📝 更新日志

### v1.0 (2025-01)
- 初始版本发布
- 联系人管理、聊天记录整理
- AI 性格分析（流式输出）
- 数据统计与可视化
- 多格式数据导出

---

## 📄 许可证

MIT License

## 👨‍💻 作者

[OppenHaix](https://github.com/OppenHaix)

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [火山引擎](https://www.volcengine.com/) - AI 能力支持
