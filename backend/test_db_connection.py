# 测试数据库连接脚本
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 创建Flask应用实例
app = Flask(__name__)

# 从环境变量中配置MySQL数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'bookstore_management_system')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 测试数据库连接
def test_db():
    try:
        with app.app_context():
            print(f"尝试连接到数据库: {app.config['SQLALCHEMY_DATABASE_URI']}")
            result = db.session.execute(text('SELECT 1'))
            print("数据库连接成功!")
            print(f"查询结果: {result.scalar()}")
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")

if __name__ == '__main__':
    test_db()