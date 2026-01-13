import os

# ⚠️ 请设置自己的火山引擎 API Key
# 方式：export VOLCANO_ARK_API_KEY="your-api-key"
VOLCANO_ARK_API_KEY = None  # 必须通过环境变量设置

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
os.makedirs(DATABASE_DIR, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-mysoullinker'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(DATABASE_DIR, 'social.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    VOLCANO_ARK_API_KEY = os.environ.get('VOLCANO_ARK_API_KEY')
    VOLCANO_ARK_ENDPOINT = 'https://ark.cn-beijing.volces.com/api/v3'
    AI_MODEL_ID = 'doubao-seed-1-6-251015'
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
