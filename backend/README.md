# Flask MySQL 后端服务

一个使用Flask框架连接MySQL数据库的后端服务示例。

## 技术栈
- Python 3.8+
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- PyMySQL 1.1.0
- python-dotenv 1.0.0
- MySQL 5.7+

## 项目结构
```
backend/
├── app.py           # Flask应用主文件
├── requirements.txt # 项目依赖包
├── .env             # 环境变量配置（请勿提交到版本控制）
├── venv/            # Python虚拟环境
└── README.md        # 项目说明文档
```

## 环境要求
- Python 3.8或更高版本
- MySQL 5.7或更高版本
- 已创建名为`bookstore_management_system`的数据库

## 安装步骤

### 1. 激活虚拟环境

Windows系统：
```powershell
cd d:\AAA\backend
venv\Scripts\activate
```

Linux/Mac系统：
```bash
cd d:\AAA\backend
source venv/bin/activate
```

### 2. 安装依赖包

```powershell
pip install -r requirements.txt
```

### 3. 配置环境变量

编辑`.env`文件，设置您的MySQL数据库连接信息：
```
# MySQL数据库连接配置
DB_USERNAME=root        # 您的MySQL用户名
DB_PASSWORD=password    # 您的MySQL密码
DB_HOST=localhost       # 数据库主机地址
DB_PORT=3306            # 数据库端口
DB_NAME=bookstore_management_system # 数据库名称

# Flask配置
SECRET_KEY=your-secret-key-here # 随机密钥，用于会话加密
DEBUG=True              # 调试模式（生产环境应设为False）

# 服务器配置
HOST=0.0.0.0            # 主机地址
PORT=5000               # 端口号
```

## 运行应用

在激活的虚拟环境中执行：

```powershell
python app.py
```

应用将在 http://localhost:5000 启动。

## API端点

应用提供以下API端点用于测试和管理：

- **健康检查**：`GET /api/health`
  - 检查服务是否正常运行

- **应用信息**：`GET /api/info`
  - 获取应用基本信息

- **数据库连接测试**：`GET /api/test-connection`
  - 测试与MySQL数据库的连接是否正常

- **数据库版本**：`GET /api/db-version`
  - 获取MySQL数据库版本信息

- **检查users表**：`GET /api/check-users-table`
  - 检查users表是否存在并获取表结构

- **获取所有用户**：`GET /api/users`
  - 获取数据库中所有用户的列表

## 注意事项

1. **安全提示**
   - 请勿将`.env`文件提交到版本控制系统
   - 生产环境中应禁用`DEBUG`模式
   - 生产环境应使用HTTPS
   - 应设置强密码和适当的权限控制

2. **生产部署**
   - 生产环境应使用WSGI服务器（如Gunicorn或uWSGI）
   - 建议使用Docker容器化部署
   - 考虑使用反向代理（如Nginx）

3. **扩展建议**
   - 添加用户认证和授权功能
   - 实现API限流
   - 添加日志记录和监控
   - 实现请求验证和错误处理

## 常见问题解决

**问题：无法连接到MySQL数据库**
- 确认MySQL服务已启动
- 检查`.env`文件中的连接信息是否正确
- 确保数据库用户有足够的权限
- 确认防火墙设置允许连接

**问题：依赖安装失败**
- 确保Python版本符合要求
- 尝试更新pip：`pip install --upgrade pip`
- 检查网络连接是否正常

**问题：API请求返回500错误**
- 查看控制台输出获取详细错误信息
- 检查数据库连接是否正常
- 确认相关表已创建