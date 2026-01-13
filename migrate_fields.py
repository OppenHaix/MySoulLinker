import os
import sqlite3
from flask import Flask
from database.models import db, Contact, AnalysisResult, ChatLog
from config import Config
import sys

app = Flask(__name__)
app.config.from_object(Config)
db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
print(f"Database path: {db_path}")

def migrate_add_fields():
    with app.app_context():
        if not os.path.exists(db_path):
            print("数据库文件不存在，将创建新数据库...")
            db.create_all()
            print("✅ 数据库和表已创建!")
        else:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Database tables: {[t[0] for t in tables]}")
            
            if 'analysis_result' in [t[0] for t in tables]:
                cursor.execute("PRAGMA table_info(analysis_result)")
                columns = [row[1] for row in cursor.fetchall()]
                print(f"Current columns: {columns}")
                
                if 'topic_suggestions' not in columns:
                    cursor.execute("ALTER TABLE analysis_result ADD COLUMN topic_suggestions TEXT DEFAULT ''")
                    print("✅ 已添加 topic_suggestions 字段")
                else:
                    print("ℹ️ topic_suggestions 字段已存在")
                
                if 'gift_suggestions' not in columns:
                    cursor.execute("ALTER TABLE analysis_result ADD COLUMN gift_suggestions TEXT DEFAULT ''")
                    print("✅ 已添加 gift_suggestions 字段")
                else:
                    print("ℹ️ gift_suggestions 字段已存在")
                
                conn.commit()
            else:
                print("analysis_result 表不存在，将创建...")
                db.create_all()
                print("✅ 表已创建!")
            
            conn.close()
        
        print("✅ 数据库迁移完成！")

if __name__ == '__main__':
    migrate_add_fields()
