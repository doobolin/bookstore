# Flask应用主文件
# 用于连接MySQL数据库并提供基本的API服务

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 创建Flask应用实例
app = Flask(__name__)

# 从环境变量中配置MySQL数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'bookstore_management_system')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# 初始化数据库
db = SQLAlchemy(app)

# 定义基础响应格式
def make_response(data=None, message='Success', status=200):
    response = {
        'code': status,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status

# 测试数据库连接的路由
@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    try:
        # 执行一个简单的查询来测试连接
        with app.app_context():
            result = db.session.execute(text('SELECT 1'))
            return make_response({'connected': True}, '数据库连接成功')
    except Exception as e:
        return make_response(None, f'数据库连接失败: {str(e)}', 500)

# 获取数据库版本信息
@app.route('/api/db-version', methods=['GET'])
def get_db_version():
    try:
        with app.app_context():
            result = db.session.execute(text('SELECT VERSION()'))
            version = result.scalar()
            return make_response({'version': version}, '获取数据库版本成功')
    except Exception as e:
        return make_response(None, f'获取数据库版本失败: {str(e)}', 500)

# 检查users表是否存在
@app.route('/api/check-users-table', methods=['GET'])
def check_users_table():
    try:
        with app.app_context():
            result = db.session.execute(
                text("SHOW TABLES LIKE 'users'"))
            exists = result.fetchone() is not None
            
            if exists:
                # 获取表结构
                desc_result = db.session.execute(text('DESCRIBE users'))
                columns = []
                for row in desc_result:
                    columns.append({
                        'Field': row[0],
                        'Type': row[1],
                        'Null': row[2],
                        'Key': row[3],
                        'Default': row[4],
                        'Extra': row[5]
                    })
                return make_response({'exists': True, 'columns': columns}, 'users表存在')
            else:
                return make_response({'exists': False}, 'users表不存在')
    except Exception as e:
        return make_response(None, f'检查users表失败: {str(e)}', 500)

# 获取所有活跃用户
@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        with app.app_context():
            result = db.session.execute(
                text('SELECT id, username, email, role, status, created_at FROM users'))
            users = []
            for row in result:
                users.append({
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'role': row[3],
                    'status': row[4],
                    'created_at': row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None
                })
            return make_response({'users': users}, '获取用户列表成功')
    except Exception as e:
        return make_response(None, f'获取用户列表失败: {str(e)}', 500)

# 获取用户总数API
@app.route('/api/users/count', methods=['GET'])
def get_users_count():
    try:
        with app.app_context():
            # 查询总用户数
            total_count_query = text("SELECT COUNT(*) FROM users")
            total_count_result = db.session.execute(total_count_query).fetchone()
            total_count = total_count_result[0] if total_count_result[0] is not None else 0
            
            # 查询活跃用户数
            active_count_query = text("SELECT COUNT(*) FROM users WHERE status = 'active'")
            active_count_result = db.session.execute(active_count_query).fetchone()
            active_count = active_count_result[0] if active_count_result[0] is not None else 0
            
            # 查询禁用用户数
            inactive_count_query = text("SELECT COUNT(*) FROM users WHERE status = 'inactive'")
            inactive_count_result = db.session.execute(inactive_count_query).fetchone()
            inactive_count = inactive_count_result[0] if inactive_count_result[0] is not None else 0
            
            return make_response({
                'total': total_count,
                'active': active_count,
                'inactive': inactive_count
            }, '获取用户总数成功')
    except Exception as e:
        return make_response(None, f'获取用户总数失败: {str(e)}', 500)

# 健康检查路由
@app.route('/api/health', methods=['GET'])
def health_check():
    return make_response({
        'status': 'healthy',
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }, '服务运行正常')

# 应用信息路由
@app.route('/api/info', methods=['GET'])
def app_info():
    return make_response({
        'name': 'Flask MySQL Backend',
        'version': '1.0.0',
        'description': '用于连接MySQL数据库的Flask后端服务'
    }, '获取应用信息成功')

# 添加用户API
@app.route('/api/users', methods=['POST'])
def add_user():
    try:
        from flask import request
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return make_response(None, f'缺少必填字段: {field}', 400)
        
        with app.app_context():
            # 检查用户是否已存在
            check_query = text("SELECT id FROM users WHERE username = :username OR email = :email")
            check_result = db.session.execute(check_query, {
                'username': data['username'],
                'email': data['email']
            }).fetchone()
            
            if check_result:
                return make_response(None, '用户名或邮箱已存在', 400)
            
            # 检查当前最大ID，确保ID连续性
            max_id_query = text("SELECT MAX(id) FROM users")
            max_id_result = db.session.execute(max_id_query).fetchone()
            max_id = max_id_result[0] if max_id_result[0] is not None else 0
            
            # 检查记录总数
            count_query = text("SELECT COUNT(*) FROM users")
            count_result = db.session.execute(count_query).fetchone()
            user_count = count_result[0] if count_result[0] is not None else 0
            
            # 如果ID不连续，重置自增计数器
            if max_id != user_count:
                next_id = user_count + 1
                reset_autoinc_query = text(f"ALTER TABLE users AUTO_INCREMENT = {next_id}")
                db.session.execute(reset_autoinc_query)
                db.session.commit()
            
            # 插入新用户
            insert_query = text("""
                INSERT INTO users (username, email, password, role, status, created_at)
                VALUES (:username, :email, :password, :role, :status, NOW())
            """)
            db.session.execute(insert_query, {
                'username': data['username'],
                'email': data['email'],
                'password': data['password'],  # 注意：实际应用中应该加密存储密码
                'role': data['role'],
                'status': data.get('status', 'active')
            })
            db.session.commit()
            
            # 获取新创建的用户信息
            new_user_query = text("SELECT id, username, email, role, status, created_at FROM users WHERE email = :email")
            new_user = db.session.execute(new_user_query, {'email': data['email']}).fetchone()
            
            user_data = {
                'id': new_user[0],
                'username': new_user[1],
                'email': new_user[2],
                'role': new_user[3],
                'status': new_user[4],
                'created_at': new_user[5].strftime('%Y-%m-%d %H:%M:%S') if new_user[5] else None
            }
            
            return make_response(user_data, '添加用户成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'添加用户失败: {str(e)}', 500)

# 更新用户API
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        from flask import request
        data = request.get_json()
        
        with app.app_context():
            # 检查用户是否存在
            check_query = text("SELECT id FROM users WHERE id = :user_id")
            check_result = db.session.execute(check_query, {'user_id': user_id}).fetchone()
            
            if not check_result:
                return make_response(None, '用户不存在', 404)
            
            # 构建更新查询
            update_fields = []
            update_params = {'user_id': user_id}
            
            if 'username' in data:
                update_fields.append("username = :username")
                update_params['username'] = data['username']
            
            if 'email' in data:
                update_fields.append("email = :email")
                update_params['email'] = data['email']
            
            if 'password' in data:
                update_fields.append("password = :password")
                update_params['password'] = data['password']  # 注意：实际应用中应该加密存储密码
            
            if 'role' in data:
                update_fields.append("role = :role")
                update_params['role'] = data['role']
            
            if 'status' in data:
                update_fields.append("status = :status")
                update_params['status'] = data['status']
            
            if not update_fields:
                return make_response(None, '没有需要更新的字段', 400)
            
            update_query = text(f"UPDATE users SET {', '.join(update_fields)} WHERE id = :user_id")
            db.session.execute(update_query, update_params)
            db.session.commit()
            
            # 获取更新后的用户信息
            updated_user_query = text("SELECT id, username, email, role, status, created_at FROM users WHERE id = :user_id")
            updated_user = db.session.execute(updated_user_query, {'user_id': user_id}).fetchone()
            
            user_data = {
                'id': updated_user[0],
                'username': updated_user[1],
                'email': updated_user[2],
                'role': updated_user[3],
                'status': updated_user[4],
                'created_at': updated_user[5].strftime('%Y-%m-%d %H:%M:%S') if updated_user[5] else None
            }
            
            return make_response(user_data, '更新用户成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'更新用户失败: {str(e)}', 500)

# 删除用户API
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        with app.app_context():
            # 检查用户是否存在
            check_query = text("SELECT id FROM users WHERE id = :user_id")
            check_result = db.session.execute(check_query, {'user_id': user_id}).fetchone()

            if not check_result:
                return make_response(None, '用户不存在', 404)

            # 检查要删除的用户是否有关联的订单
            orders_check_query = text("SELECT COUNT(*) FROM orders WHERE user_id = :user_id")
            orders_count = db.session.execute(orders_check_query, {'user_id': user_id}).scalar()

            if orders_count > 0:
                return make_response(None, f'无法删除用户：该用户有{orders_count}个关联订单，请先处理这些订单', 400)

            # 删除用户
            delete_query = text("DELETE FROM users WHERE id = :user_id")
            db.session.execute(delete_query, {'user_id': user_id})

            # 检查剩余的所有用户是否都没有订单（以便安全地重新排列ID）
            remaining_users_query = text("SELECT id FROM users ORDER BY id ASC")
            remaining_users = db.session.execute(remaining_users_query).fetchall()

            can_reorder = True
            for user in remaining_users:
                user_orders = db.session.execute(
                    text("SELECT COUNT(*) FROM orders WHERE user_id = :user_id"),
                    {'user_id': user[0]}
                ).scalar()
                if user_orders > 0:
                    can_reorder = False
                    break

            # 如果所有用户都没有订单，重新排列ID
            if can_reorder and remaining_users:
                # 第一步：将所有用户ID更新为临时值
                temp_ids = []
                for index, user in enumerate(remaining_users, start=1):
                    temp_id = 20000 + index
                    db.session.execute(
                        text("UPDATE users SET id = :temp_id WHERE id = :old_id"),
                        {'temp_id': temp_id, 'old_id': user[0]}
                    )
                    temp_ids.append(temp_id)

                # 第二步：将临时ID更新为正确的连续ID
                for index, temp_id in enumerate(temp_ids, start=1):
                    db.session.execute(
                        text("UPDATE users SET id = :correct_id WHERE id = :temp_id"),
                        {'correct_id': index, 'temp_id': temp_id}
                    )

                # 重置AUTO_INCREMENT
                next_id = len(remaining_users) + 1
                db.session.execute(text(f"ALTER TABLE users AUTO_INCREMENT = {next_id}"))
            else:
                # 不能重排ID，只重置AUTO_INCREMENT到下一个可用值
                if remaining_users:
                    max_id = max(user[0] for user in remaining_users)
                    next_id = max_id + 1
                else:
                    next_id = 1
                db.session.execute(text(f"ALTER TABLE users AUTO_INCREMENT = {next_id}"))

            db.session.commit()

            message = '删除用户成功'
            if can_reorder and remaining_users:
                message += '，ID已重新排列'

            return make_response(None, message)
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'删除用户失败: {str(e)}', 500)

# 修复用户ID（临时维护端点）
@app.route('/api/users/fix-ids', methods=['POST'])
def fix_user_ids():
    """修复用户ID，使其连续并重置AUTO_INCREMENT"""
    try:
        with app.app_context():
            # 获取所有用户，按ID排序
            users_query = text("SELECT id, username, email, password, role, status, created_at FROM users ORDER BY id ASC")
            users = db.session.execute(users_query).fetchall()

            if not users:
                return make_response(None, '没有用户需要修复', 200)

            # 检查是否有订单关联
            for user in users:
                orders_check = text("SELECT COUNT(*) FROM orders WHERE user_id = :user_id")
                order_count = db.session.execute(orders_check, {'user_id': user[0]}).scalar()
                if order_count > 0:
                    return make_response(None, f'用户ID {user[0]}({user[1]}) 有{order_count}个关联订单，无法重新分配ID', 400)

            # 先将所有用户ID改为临时值
            temp_mapping = {}
            for idx, user in enumerate(users, start=1):
                temp_id = 20000 + idx
                temp_mapping[temp_id] = (idx, user)
                db.session.execute(
                    text("UPDATE users SET id = :temp_id WHERE id = :old_id"),
                    {'temp_id': temp_id, 'old_id': user[0]}
                )

            # 然后将临时ID改为正确的连续ID
            for temp_id, (new_id, user) in temp_mapping.items():
                db.session.execute(
                    text("UPDATE users SET id = :new_id WHERE id = :temp_id"),
                    {'new_id': new_id, 'temp_id': temp_id}
                )

            # 重置AUTO_INCREMENT
            next_id = len(users) + 1
            db.session.execute(text(f"ALTER TABLE users AUTO_INCREMENT = {next_id}"))

            db.session.commit()

            return make_response({
                'fixed_count': len(users),
                'next_id': next_id
            }, f'成功修复{len(users)}个用户的ID')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'修复用户ID失败: {str(e)}', 500)

# 切换用户状态API
@app.route('/api/users/<int:user_id>/status', methods=['PATCH'])
def toggle_user_status(user_id):
    try:
        from flask import request
        data = request.get_json()
        
        if 'status' not in data:
            return make_response(None, '缺少状态字段', 400)
        
        if data['status'] not in ['active', 'inactive']:
            return make_response(None, '无效的状态值，只能是active或inactive', 400)
        
        with app.app_context():
            # 检查用户是否存在
            check_query = text("SELECT id FROM users WHERE id = :user_id")
            check_result = db.session.execute(check_query, {'user_id': user_id}).fetchone()
            
            if not check_result:
                return make_response(None, '用户不存在', 404)
            
            # 更新用户状态
            update_query = text("UPDATE users SET status = :status WHERE id = :user_id")
            db.session.execute(update_query, {
                'status': data['status'],
                'user_id': user_id
            })
            db.session.commit()
            
            # 获取更新后的用户信息
            updated_user_query = text("SELECT id, username, email, role, status, created_at FROM users WHERE id = :user_id")
            updated_user = db.session.execute(updated_user_query, {'user_id': user_id}).fetchone()
            
            user_data = {
                'id': updated_user[0],
                'username': updated_user[1],
                'email': updated_user[2],
                'role': updated_user[3],
                'status': updated_user[4],
                'created_at': updated_user[5].strftime('%Y-%m-%d %H:%M:%S') if updated_user[5] else None
            }
            
            return make_response(user_data, '更新用户状态成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'更新用户状态失败: {str(e)}', 500)

# 查询用户状态API - 用于检查用户是否被禁用
@app.route('/api/check-user-status', methods=['POST'])
def check_user_status():
    try:
        from flask import request
        data = request.get_json()
        
        # 验证必填字段
        if not data or 'username' not in data:
            return make_response(None, '缺少用户名', 400)
        
        username = data['username']
        
        with app.app_context():
            # 查询数据库中的用户状态
            user_query = text("""
                SELECT status 
                FROM users 
                WHERE username = :username
            """)
            user = db.session.execute(user_query, { 'username': username }).fetchone()
            
            if not user:
                return make_response({ 'exists': False, 'status': None }, '用户不存在')
            
            user_status = user[0]
            return make_response({ 'exists': True, 'status': user_status }, '查询用户状态成功')
    except Exception as e:
        return make_response(None, f'查询用户状态失败: {str(e)}', 500)

# 登录API
@app.route('/api/login', methods=['POST'])
def login():
    try:
        from flask import request
        data = request.get_json()
        
        # 验证必填字段
        if not data or 'username' not in data or 'password' not in data:
            return make_response(None, '缺少用户名或密码', 400)
        
        username = data['username']
        password = data['password']
        
        with app.app_context():
            # 查询数据库中的用户
            user_query = text("""
                SELECT id, username, role, status 
                FROM users 
                WHERE username = :username AND password = :password
            """)
            user = db.session.execute(user_query, {
                'username': username,
                'password': password
            }).fetchone()
            
            # 验证用户是否存在且状态为活跃
            if not user:
                return make_response(None, '用户名或密码错误', 401)
            
            user_id, username, role, status = user
            
            if status != 'active':
                return make_response(None, '用户已被禁用', 403)
            
            # 生成模拟token（实际项目中应该使用JWT等安全机制）
            token = f'mock-jwt-token-{username}-{user_id}'

            return make_response({
                'token': token,
                'user_id': user_id,
                'username': username,
                'role': role
            }, '登录成功')
    except Exception as e:
        return make_response(None, f'登录失败: {str(e)}', 500)

# 注册API
@app.route('/api/register', methods=['POST'])
def register():
    try:
        from flask import request
        data = request.get_json()

        # 验证必填字段
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return make_response(None, f'缺少必填字段: {field}', 400)

        username = data['username']
        email = data['email']
        password = data['password']

        with app.app_context():
            # 检查用户名是否已存在
            check_username_query = text("SELECT id FROM users WHERE username = :username")
            existing_username = db.session.execute(check_username_query, {'username': username}).fetchone()

            if existing_username:
                return make_response(None, '用户名已存在', 400)

            # 检查邮箱是否已存在
            check_email_query = text("SELECT id FROM users WHERE email = :email")
            existing_email = db.session.execute(check_email_query, {'email': email}).fetchone()

            if existing_email:
                return make_response(None, '邮箱已被注册', 400)

            # 插入新用户（默认角色为user）
            insert_query = text("""
                INSERT INTO users (username, email, password, role, status, created_at)
                VALUES (:username, :email, :password, 'user', 'active', NOW())
            """)
            db.session.execute(insert_query, {
                'username': username,
                'email': email,
                'password': password  # 注意：实际应用中应该加密存储密码
            })
            db.session.commit()

            # 获取新创建的用户信息
            new_user_query = text("""
                SELECT id, username, email, role, status, created_at
                FROM users
                WHERE username = :username
            """)
            new_user = db.session.execute(new_user_query, {'username': username}).fetchone()

            user_data = {
                'id': new_user[0],
                'username': new_user[1],
                'email': new_user[2],
                'role': new_user[3],
                'status': new_user[4],
                'created_at': new_user[5].strftime('%Y-%m-%d %H:%M:%S') if new_user[5] else None
            }

            return make_response(user_data, '注册成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'注册失败: {str(e)}', 500)

# 获取所有图书API
@app.route('/api/books', methods=['GET'])
def get_all_books():
    try:
        with app.app_context():
            # 直接使用表连接查询，避免依赖视图
            result = db.session.execute(text("""
                SELECT
                    b.id,
                    b.title,
                    b.author,
                    c.name AS category,
                    b.category_id,
                    b.description,
                    b.price,
                    b.stock,
                    b.rating,
                    b.image,
                    b.status
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
            """))
            books = []
            for row in result:
                books.append({
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'category': row[3],
                    'category_id': row[4],
                    'description': row[5],
                    'price': float(row[6]),
                    'stock': row[7],
                    'rating': float(row[8]) if row[8] else 0.0,
                    'image': row[9],
                    'status': row[10]
                })
            return make_response({'books': books}, '获取图书列表成功')
    except Exception as e:
        return make_response(None, f'获取图书列表失败: {str(e)}', 500)

# 获取单个图书详情API
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    try:
        with app.app_context():
            # 查询指定ID的图书，关联分类表获取分类名称
            result = db.session.execute(text("""
                SELECT
                    b.id,
                    b.isbn,
                    b.title,
                    b.author,
                    c.name AS category,
                    b.category_id,
                    b.description,
                    b.price,
                    b.stock,
                    b.rating,
                    b.image,
                    b.status,
                    b.created_at,
                    b.updated_at
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                WHERE b.id = :book_id
            """), {'book_id': book_id})

            book_row = result.fetchone()

            # 如果图书不存在，返回404
            if not book_row:
                return make_response(None, '图书不存在', 404)

            # 构建图书详情数据
            book_data = {
                'id': book_row[0],
                'isbn': book_row[1],
                'title': book_row[2],
                'author': book_row[3],
                'category': book_row[4],
                'category_id': book_row[5],
                'description': book_row[6],
                'price': float(book_row[7]),
                'stock': book_row[8],
                'rating': float(book_row[9]) if book_row[9] else 0.0,
                'image': book_row[10],
                'status': book_row[11],
                'created_at': book_row[12].strftime('%Y-%m-%d %H:%M:%S') if book_row[12] else None,
                'updated_at': book_row[13].strftime('%Y-%m-%d %H:%M:%S') if book_row[13] else None
            }

            return make_response(book_data, '获取图书详情成功')
    except Exception as e:
        return make_response(None, f'获取图书详情失败: {str(e)}', 500)

# 获取所有分类API
@app.route('/api/categories', methods=['GET'])
def get_all_categories():
    try:
        with app.app_context():
            result = db.session.execute(text("""
                SELECT id, name, description
                FROM categories
                ORDER BY id ASC
            """))
            categories = []
            for row in result:
                categories.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2]
                })
            return make_response({'categories': categories}, '获取分类列表成功')
    except Exception as e:
        return make_response(None, f'获取分类列表失败: {str(e)}', 500)

# 添加图书API
@app.route('/api/books', methods=['POST'])
def add_book():
    try:
        from flask import request
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['title', 'author', 'price', 'stock']
        for field in required_fields:
            if field not in data:
                return make_response(None, f'缺少必填字段: {field}', 400)
        
        with app.app_context():
            # 查找最小的可用ID（填补删除后留下的空缺）
            find_min_available_id_query = text("""
                SELECT MIN(t1.id + 1)
                FROM books t1
                LEFT JOIN books t2 ON t1.id + 1 = t2.id
                WHERE t2.id IS NULL AND t1.id + 1 > 0
            """)
            min_available_id = db.session.execute(find_min_available_id_query).scalar()
            
            # 如果没有空缺的ID，则获取当前最大ID加1
            if not min_available_id:
                max_id_query = text("SELECT MAX(id) FROM books")
                max_id = db.session.execute(max_id_query).scalar()
                min_available_id = 1 if max_id is None else max_id + 1
            
            # 插入新图书（指定ID）
            insert_query = text("""
                INSERT INTO books (id, title, author, category_id, description, price, stock, rating, image, status)
                VALUES (:id, :title, :author, :category_id, :description, :price, :stock, :rating, :image, :status)
            """)
            db.session.execute(insert_query, {
                'id': min_available_id,
                'title': data['title'],
                'author': data['author'],
                'category_id': data.get('category_id'),
                'description': data.get('description'),
                'price': data['price'],
                'stock': data['stock'],
                'rating': data.get('rating', 0.0),
                'image': data.get('image'),
                'status': data.get('status', 'available')
            })
            db.session.commit()
            
            # 获取新创建的图书信息
            new_book_query = text("SELECT id, title, author, price, stock FROM books WHERE id = :id")
            new_book = db.session.execute(new_book_query, {'id': min_available_id}).fetchone()
            
            if not new_book:
                return make_response(None, '添加图书成功，但无法获取新图书信息', 201)
            
            book_data = {
                'id': new_book[0],
                'title': new_book[1],
                'author': new_book[2],
                'price': float(new_book[3]),
                'stock': new_book[4]
            }
            
            return make_response(book_data, '添加图书成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'添加图书失败: {str(e)}', 500)

# 更新图书API
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    try:
        from flask import request
        data = request.get_json()
        
        with app.app_context():
            # 检查图书是否存在
            check_query = text("SELECT id FROM books WHERE id = :book_id")
            check_result = db.session.execute(check_query, {'book_id': book_id}).fetchone()
            
            if not check_result:
                return make_response(None, '图书不存在', 404)
            
            # 构建更新查询
            update_fields = []
            update_params = {'book_id': book_id}
            
            if 'title' in data:
                update_fields.append("title = :title")
                update_params['title'] = data['title']
            
            if 'author' in data:
                update_fields.append("author = :author")
                update_params['author'] = data['author']
            
            if 'category_id' in data:
                update_fields.append("category_id = :category_id")
                update_params['category_id'] = data['category_id']
            
            if 'description' in data:
                update_fields.append("description = :description")
                update_params['description'] = data['description']
            
            if 'price' in data:
                update_fields.append("price = :price")
                update_params['price'] = data['price']
            
            if 'stock' in data:
                update_fields.append("stock = :stock")
                update_params['stock'] = data['stock']
            
            if 'rating' in data:
                update_fields.append("rating = :rating")
                update_params['rating'] = data['rating']
            
            if 'image' in data:
                update_fields.append("image = :image")
                update_params['image'] = data['image']
            
            if 'status' in data:
                update_fields.append("status = :status")
                update_params['status'] = data['status']
            
            if not update_fields:
                return make_response(None, '没有需要更新的字段', 400)
            
            update_query = text(f"UPDATE books SET {', '.join(update_fields)} WHERE id = :book_id")
            db.session.execute(update_query, update_params)
            db.session.commit()
            
            # 获取更新后的图书信息
            updated_book_query = text("SELECT id, title, author, price, stock FROM books WHERE id = :book_id")
            updated_book = db.session.execute(updated_book_query, {'book_id': book_id}).fetchone()
            
            book_data = {
                'id': updated_book[0],
                'title': updated_book[1],
                'author': updated_book[2],
                'price': float(updated_book[3]),
                'stock': updated_book[4]
            }
            
            return make_response(book_data, '更新图书成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'更新图书失败: {str(e)}', 500)

# 删除图书API
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        with app.app_context():
            # 检查图书是否存在
            check_query = text("SELECT id FROM books WHERE id = :book_id")
            check_result = db.session.execute(check_query, {'book_id': book_id}).fetchone()
            
            if not check_result:
                return make_response(None, '图书不存在', 404)
            
            # 删除图书
            delete_query = text("DELETE FROM books WHERE id = :book_id")
            db.session.execute(delete_query, {'book_id': book_id})
            db.session.commit()
            
            return make_response(None, '删除图书成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'删除图书失败: {str(e)}', 500)

# 获取图书总数API
@app.route('/api/books/count', methods=['GET'])
def get_books_count():
    try:
        with app.app_context():
            # 查询图书总数和总库存（仅计算可用状态的图书）
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    SUM(stock) as total_stock
                FROM books
                WHERE status = 'available'
            """))
            count_data = result.fetchone()
            
            return make_response({
                'total': count_data[0],
                'totalStock': count_data[1] if count_data[1] else 0
            }, '获取图书统计数据成功')
    except Exception as e:
        return make_response(None, f'获取图书统计数据失败: {str(e)}', 500)

# 实时库存预警API
@app.route('/api/books/low-stock', methods=['GET'])
def get_low_stock_books():
    try:
        with app.app_context():
            # 查询库存低于10本且状态为available的图书
            result = db.session.execute(text("""
                SELECT
                    b.id,
                    b.title,
                    b.author,
                    c.name AS category,
                    b.stock
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                WHERE b.status = 'available' AND b.stock < 20
                ORDER BY b.stock ASC
            """))
            low_stock_books = []
            for row in result:
                low_stock_books.append({
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'category': row[3],
                    'stock': row[4]
                })

            return make_response({
                'books': low_stock_books,
                'total': len(low_stock_books)
            }, '获取低库存图书成功')
    except Exception as e:
        return make_response(None, f'获取低库存图书失败: {str(e)}', 500)

# 搜索图书API
@app.route('/api/books/search', methods=['GET'])
def search_books():
    try:
        from flask import request

        # 获取搜索参数
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()

        if not query and not category:
            return make_response(None, '请提供搜索关键词或分类', 400)

        with app.app_context():
            # 构建基础查询
            sql_query = """
                SELECT
                    b.id,
                    b.title,
                    b.author,
                    c.name AS category,
                    b.description,
                    b.price,
                    b.stock,
                    b.rating,
                    b.image,
                    b.status
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                WHERE 1=1
            """
            params = {}

            # 如果有搜索关键词,进行多字段模糊搜索
            if query:
                sql_query += """
                    AND (
                        b.title LIKE :query
                        OR b.author LIKE :query
                        OR b.description LIKE :query
                        OR c.name LIKE :query
                    )
                """
                params['query'] = f'%{query}%'

            # 如果指定了分类且不是"全部"
            if category and category != '全部':
                sql_query += " AND c.name = :category"
                params['category'] = category

            # 按评分和标题排序
            sql_query += " ORDER BY b.rating DESC, b.title ASC"

            # 执行查询
            result = db.session.execute(text(sql_query), params)
            books = []
            for row in result:
                books.append({
                    'id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'category': row[3],
                    'description': row[4],
                    'price': float(row[5]),
                    'stock': row[6],
                    'rating': float(row[7]) if row[7] else 0.0,
                    'image': row[8],
                    'status': row[9]
                })

            return make_response({
                'books': books,
                'total': len(books),
                'query': query,
                'category': category
            }, f'搜索成功，找到{len(books)}本图书')
    except Exception as e:
        return make_response(None, f'搜索图书失败: {str(e)}', 500)

# ============================================
# 购物车API
# ============================================

# 获取用户购物车
@app.route('/api/cart', methods=['GET'])
def get_cart():
    try:
        from flask import request
        # 从请求头获取用户ID（实际应用中应从token解析）
        user_id = request.args.get('user_id')
        if not user_id:
            return make_response(None, '缺少用户ID', 400)

        with app.app_context():
            # 查询用户购物车
            result = db.session.execute(text("""
                SELECT
                    sc.id,
                    sc.book_id,
                    b.title,
                    b.author,
                    b.price,
                    b.image,
                    sc.quantity,
                    b.stock
                FROM shopping_cart sc
                JOIN books b ON sc.book_id = b.id
                WHERE sc.user_id = :user_id
                ORDER BY sc.created_at DESC
            """), {'user_id': user_id})

            cart_items = []
            for row in result:
                cart_items.append({
                    'id': row[0],
                    'book_id': row[1],
                    'title': row[2],
                    'author': row[3],
                    'price': float(row[4]),
                    'image': row[5],
                    'quantity': row[6],
                    'stock': row[7]
                })

            return make_response({
                'items': cart_items,
                'total': len(cart_items)
            }, '获取购物车成功')
    except Exception as e:
        return make_response(None, f'获取购物车失败: {str(e)}', 500)

# 添加商品到购物车
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    try:
        from flask import request
        data = request.get_json()

        # 验证必填字段
        if not data or 'user_id' not in data or 'book_id' not in data:
            return make_response(None, '缺少必填字段', 400)

        user_id = data['user_id']
        book_id = data['book_id']
        quantity = data.get('quantity', 1)

        with app.app_context():
            # 检查图书是否存在且有库存
            book_check = db.session.execute(text("""
                SELECT stock FROM books WHERE id = :book_id
            """), {'book_id': book_id}).fetchone()

            if not book_check:
                return make_response(None, '图书不存在', 404)

            if book_check[0] < quantity:
                return make_response(None, f'库存不足，当前库存：{book_check[0]}', 400)

            # 检查购物车中是否已有该商品
            existing = db.session.execute(text("""
                SELECT id, quantity FROM shopping_cart
                WHERE user_id = :user_id AND book_id = :book_id
            """), {'user_id': user_id, 'book_id': book_id}).fetchone()

            if existing:
                # 更新数量
                new_quantity = existing[1] + quantity
                db.session.execute(text("""
                    UPDATE shopping_cart
                    SET quantity = :quantity, updated_at = NOW()
                    WHERE id = :id
                """), {'quantity': new_quantity, 'id': existing[0]})
            else:
                # 添加新记录
                db.session.execute(text("""
                    INSERT INTO shopping_cart (user_id, book_id, quantity)
                    VALUES (:user_id, :book_id, :quantity)
                """), {'user_id': user_id, 'book_id': book_id, 'quantity': quantity})

            db.session.commit()
            return make_response(None, '添加到购物车成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'添加到购物车失败: {str(e)}', 500)

# 更新购物车商品数量
@app.route('/api/cart/update', methods=['PUT'])
def update_cart():
    try:
        from flask import request
        data = request.get_json()

        if not data or 'cart_id' not in data or 'quantity' not in data:
            return make_response(None, '缺少必填字段', 400)

        cart_id = data['cart_id']
        quantity = data['quantity']

        if quantity < 1:
            return make_response(None, '数量必须大于0', 400)

        with app.app_context():
            # 检查库存
            stock_check = db.session.execute(text("""
                SELECT b.stock FROM shopping_cart sc
                JOIN books b ON sc.book_id = b.id
                WHERE sc.id = :cart_id
            """), {'cart_id': cart_id}).fetchone()

            if not stock_check:
                return make_response(None, '购物车项不存在', 404)

            if stock_check[0] < quantity:
                return make_response(None, f'库存不足，当前库存：{stock_check[0]}', 400)

            # 更新数量
            db.session.execute(text("""
                UPDATE shopping_cart
                SET quantity = :quantity, updated_at = NOW()
                WHERE id = :cart_id
            """), {'quantity': quantity, 'cart_id': cart_id})
            db.session.commit()

            return make_response(None, '更新购物车成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'更新购物车失败: {str(e)}', 500)

# 从购物车删除商品
@app.route('/api/cart/remove', methods=['DELETE'])
def remove_from_cart():
    try:
        from flask import request
        cart_id = request.args.get('cart_id')

        if not cart_id:
            return make_response(None, '缺少购物车项ID', 400)

        with app.app_context():
            db.session.execute(text("""
                DELETE FROM shopping_cart WHERE id = :cart_id
            """), {'cart_id': cart_id})
            db.session.commit()

            return make_response(None, '删除成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'删除失败: {str(e)}', 500)

# 清空购物车
@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    try:
        from flask import request
        user_id = request.args.get('user_id')

        if not user_id:
            return make_response(None, '缺少用户ID', 400)

        with app.app_context():
            db.session.execute(text("""
                DELETE FROM shopping_cart WHERE user_id = :user_id
            """), {'user_id': user_id})
            db.session.commit()

            return make_response(None, '购物车已清空')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'清空购物车失败: {str(e)}', 500)

# ============================================
# 订单API
# ============================================

# 创建订单
@app.route('/api/orders/create', methods=['POST'])
def create_order():
    try:
        from flask import request
        import datetime
        data = request.get_json()

        # 验证必填字段（简化版）
        required_fields = ['user_id', 'items']
        for field in required_fields:
            if field not in data:
                return make_response(None, f'缺少必填字段: {field}', 400)

        user_id = data['user_id']
        items = data['items']  # [{'book_id': 1, 'quantity': 2}, ...]

        if not items or len(items) == 0:
            return make_response(None, '订单商品不能为空', 400)

        with app.app_context():
            # 生成订单号（格式：ORD + 时间戳 + 用户ID）
            order_number = f"ORD{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"

            # 计算订单总金额并验证库存
            total_amount = 0
            order_items_data = []

            for item in items:
                book_id = item['book_id']
                quantity = item['quantity']

                # 查询图书信息
                book = db.session.execute(text("""
                    SELECT id, title, author, isbn, price, stock, image
                    FROM books WHERE id = :book_id
                """), {'book_id': book_id}).fetchone()

                if not book:
                    return make_response(None, f'图书ID {book_id} 不存在', 404)

                if book[5] < quantity:
                    return make_response(None, f'《{book[1]}》库存不足', 400)

                unit_price = float(book[4])
                subtotal = unit_price * quantity
                total_amount += subtotal

                order_items_data.append({
                    'book_id': book[0],
                    'book_title': book[1],
                    'book_author': book[2],
                    'book_isbn': book[3],
                    'book_image': book[6],
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': subtotal
                })

            # 创建订单
            db.session.execute(text("""
                INSERT INTO orders (order_number, user_id, total_amount)
                VALUES (:order_number, :user_id, :total_amount)
            """), {
                'order_number': order_number,
                'user_id': user_id,
                'total_amount': total_amount
            })

            # 获取订单ID
            order_id = db.session.execute(text("""
                SELECT id FROM orders WHERE order_number = :order_number
            """), {'order_number': order_number}).fetchone()[0]

            # 插入订单明细
            for item_data in order_items_data:
                db.session.execute(text("""
                    INSERT INTO order_items (order_id, book_id, quantity, subtotal)
                    VALUES (:order_id, :book_id, :quantity, :subtotal)
                """), {
                    'order_id': order_id,
                    'book_id': item_data['book_id'],
                    'quantity': item_data['quantity'],
                    'subtotal': item_data['subtotal']
                })

                # 减少库存
                db.session.execute(text("""
                    UPDATE books SET stock = stock - :quantity
                    WHERE id = :book_id
                """), {
                    'quantity': item_data['quantity'],
                    'book_id': item_data['book_id']
                })

            # 清空购物车
            db.session.execute(text("""
                DELETE FROM shopping_cart WHERE user_id = :user_id
            """), {'user_id': user_id})

            db.session.commit()

            return make_response({
                'order_id': order_id,
                'order_number': order_number,
                'total_amount': total_amount
            }, '订单创建成功')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'创建订单失败: {str(e)}', 500)

# 获取用户订单列表
@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        from flask import request
        user_id = request.args.get('user_id')

        with app.app_context():
            # 如果提供了user_id，查询该用户的订单；否则查询所有订单（管理员）
            if user_id:
                # 用户订单
                result = db.session.execute(text("""
                    SELECT id, order_number, total_amount, created_at
                    FROM orders
                    WHERE user_id = :user_id
                    ORDER BY created_at DESC
                """), {'user_id': user_id})
            else:
                # 所有订单（管理员用）- 关联users表获取用户名
                result = db.session.execute(text("""
                    SELECT o.id, o.order_number, o.user_id, u.username,
                           o.total_amount, o.created_at
                    FROM orders o
                    LEFT JOIN users u ON o.user_id = u.id
                    ORDER BY o.created_at DESC
                """))

            orders = []
            for row in result:
                if user_id:
                    # 用户订单格式
                    orders.append({
                        'id': row[0],
                        'order_number': row[1],
                        'total_amount': float(row[2]),
                        'created_at': row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None
                    })
                else:
                    # 管理员订单格式
                    orders.append({
                        'id': row[0],
                        'order_number': row[1],
                        'user_id': row[2],
                        'username': row[3],
                        'total_amount': float(row[4]),
                        'created_at': row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else None
                    })

            return make_response({
                'orders': orders,
                'total': len(orders)
            }, '获取订单列表成功')
    except Exception as e:
        return make_response(None, f'获取订单列表失败: {str(e)}', 500)

# 获取订单详情
@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    try:
        with app.app_context():
            # 获取订单基本信息（关联users表获取用户名）
            order = db.session.execute(text("""
                SELECT o.id, o.order_number, o.user_id, o.total_amount, o.created_at, u.username
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                WHERE o.id = :order_id
            """), {'order_id': order_id}).fetchone()

            if not order:
                return make_response(None, '订单不存在', 404)

            # 获取订单明细（关联books表获取图书信息）
            items = db.session.execute(text("""
                SELECT
                    oi.book_id, b.title, b.author, b.isbn, b.image,
                    oi.quantity, b.price, oi.subtotal
                FROM order_items oi
                JOIN books b ON oi.book_id = b.id
                WHERE oi.order_id = :order_id
            """), {'order_id': order_id})

            order_items = []
            for item in items:
                order_items.append({
                    'book_id': item[0],
                    'book_title': item[1],
                    'book_author': item[2],
                    'book_isbn': item[3],
                    'book_image': item[4],
                    'quantity': item[5],
                    'unit_price': float(item[6]),
                    'subtotal': float(item[7])
                })

            order_data = {
                'id': order[0],
                'order_number': order[1],
                'user_id': order[2],
                'username': order[5],  # 添加用户名
                'total_amount': float(order[3]),
                'created_at': order[4].strftime('%Y-%m-%d %H:%M:%S') if order[4] else None,
                'items': order_items
            }

            return make_response(order_data, '获取订单详情成功')
    except Exception as e:
        return make_response(None, f'获取订单详情失败: {str(e)}', 500)

# 取消订单（恢复库存并删除订单）
@app.route('/api/orders/<int:order_id>/cancel', methods=['DELETE'])
def cancel_order(order_id):
    try:
        with app.app_context():
            # 检查订单是否存在
            order = db.session.execute(text("""
                SELECT id FROM orders WHERE id = :order_id
            """), {'order_id': order_id}).fetchone()

            if not order:
                return make_response(None, '订单不存在', 404)

            # 恢复库存
            db.session.execute(text("""
                UPDATE books b
                JOIN order_items oi ON b.id = oi.book_id
                SET b.stock = b.stock + oi.quantity
                WHERE oi.order_id = :order_id
            """), {'order_id': order_id})

            # 删除订单（会级联删除order_items）
            db.session.execute(text("""
                DELETE FROM orders WHERE id = :order_id
            """), {'order_id': order_id})

            db.session.commit()
            return make_response(None, '订单已取消并删除')
    except Exception as e:
        db.session.rollback()
        return make_response(None, f'取消订单失败: {str(e)}', 500)


# 运行应用
if __name__ == '__main__':
    # 注意：生产环境应使用WSGI服务器，如Gunicorn或uWSGI
    app.run(debug=True, host='0.0.0.0', port=5000)

# 注意事项：
# 1. 实际部署时应禁用debug模式
# 2. 数据库连接信息应通过环境变量或.env文件设置
# 3. 生产环境应使用HTTPS
# 4. 应添加适当的认证和授权机制