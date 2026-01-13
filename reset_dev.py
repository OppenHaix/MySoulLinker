import os
import shutil

from app import create_app, db
from database.models import Contact, ChatLog, AnalysisResult
from seed_data import seed_sample_data


def reset_dev_environment():
    """重置开发环境：清理测试数据，恢复默认配置"""
    app = create_app()
    
    with app.app_context():
        print("🧹 清理测试数据...")
        
        # 删除所有分析结果
        AnalysisResult.query.delete()
        print("  ✅ 已清理分析结果")
        
        # 删除所有聊天记录
        ChatLog.query.delete()
        print("  ✅ 已清理聊天记录")
        
        # 删除所有联系人
        Contact.query.delete()
        print("  ✅ 已清理联系人")
        
        # 提交删除
        db.session.commit()
        print("  ✅ 数据库变更已提交")
        
        # 重置数据库文件（如果存在）
        db_path = os.path.join('database', 'social.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"  ✅ 已删除数据库文件: {db_path}")
        
        # 删除 uploads 和 exports 目录
        for folder in ['uploads', 'exports']:
            folder_path = folder
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"  ✅ 已删除目录: {folder_path}")
        
        print("\n🌱 填充示例数据...")
        seed_sample_data()
        
        print("\n✅ 开发环境已重置！")
        print("\n📝 下一步操作：")
        print("   1. git add .")
        print("   2. git commit -m '更新'")
        print("   3. git push")


if __name__ == '__main__':
    reset_dev_environment()
