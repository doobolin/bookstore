# 📚 线上书店

一个现代化的在线图书商城系统，采用 Vue 3 + TypeScript + Flask 全栈开发，提供完整的图书浏览、购物车、订单管理等功能。界面设计采用 iOS 风格，简约优雅。

## ✨ 功能特性

### 用户端功能
- 🔐 **用户认证系统**
  - 用户注册/登录
  - 密码加密存储
  - 会话管理

- 📖 **图书浏览**
  - 图书分类展示
  - 图书详情查看
  - 搜索功能
  - 响应式卡片布局

- 🛒 **购物车管理**
  - 添加/删除商品
  - 数量调整
  - 实时价格计算
  - 持久化存储

- 📦 **订单系统**
  - 订单创建与提交
  - 订单状态跟踪
  - 订单详情查看
  - 订单历史记录
  - 多种订单状态（待发货、配送中、已取消、售后）

- 👤 **个人中心**
  - 个人资料管理
  - 收货地址管理
  - 密码修改
  - 交易统计
  - 最近订单查看

### 管理端功能
- 📊 **图书管理**
  - 图书增删改查
  - 图书信息编辑
  - 库存管理
  - 实时搜索

- 📂 **分类管理**
  - 分类数据展示
  - 分类信息管理

## 🎨 设计特色

- **iOS 风格设计**
  - 毛玻璃效果（Glassmorphism）
  - 柔和阴影层次
  - iOS 系统配色
  - 流畅的动画过渡

- **响应式布局**
  - 适配各种屏幕尺寸
  - 移动端友好

- **现代化 UI**
  - 圆角卡片设计
  - 简约清新风格
  - 统一的视觉语言

## 🛠️ 技术栈

### 前端
- **框架**: Vue 3.5 (Composition API)
- **语言**: TypeScript 5.8
- **构建工具**: Vite 7.1
- **UI 框架**: Element Plus 2.11
- **路由**: Vue Router 4.5
- **样式**: SCSS/Sass

### 后端
- **框架**: Flask 3.0
- **数据库**: MySQL (通过 SQLAlchemy)
- **跨域**: Flask-CORS
- **ORM**: Flask-SQLAlchemy 3.1

### 开发工具
- Vue TSC (TypeScript 类型检查)
- Python-dotenv (环境变量管理)

## 📁 项目结构

```
AAA/
├── 线上书店/              # 用户端前端
│   ├── src/
│   │   ├── components/       # Vue 组件
│   │   │   ├── Home.vue           # 首页
│   │   │   ├── Login.vue          # 登录
│   │   │   ├── Register.vue       # 注册
│   │   │   ├── BookDetail.vue     # 图书详情
│   │   │   ├── ShoppingCart.vue   # 购物车
│   │   │   ├── OrderCheckout.vue  # 订单结算
│   │   │   ├── OrderList.vue      # 订单列表
│   │   │   ├── OrderDetail.vue    # 订单详情
│   │   │   ├── UserProfile.vue    # 个人中心
│   │   │   ├── PageContainer.vue  # 页面容器
│   │   │   └── CardContainer.vue  # 卡片容器
│   │   ├── router/           # 路由配置
│   │   ├── assets/           # 静态资源
│   │   └── api/              # API 接口
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── 图书后台管理/              # 管理端前端
│   ├── src/
│   │   ├── components/       # 管理组件
│   │   ├── views/            # 页面视图
│   │   └── api/              # API 接口
│   ├── package.json
│   └── vite.config.ts
│
└── backend/                  # 后端服务
    ├── app.py                # Flask 主应用
    ├── models.py             # 数据模型
    ├── routes/               # API 路由
    ├── requirements.txt      # Python 依赖
    └── .env                  # 环境变量（需自行创建）
```

## 🚀 快速开始

### 环境要求

- Node.js 16+
- Python 3.8+
- MySQL 8.0+

### 1. 克隆项目

```bash
git clone <repository-url>
cd AAA
```

### 2. 配置数据库

创建 MySQL 数据库：

```sql
CREATE DATABASE bookstore_management_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 配置后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件并配置
# .env 示例:
# DB_HOST=localhost
# DB_PORT=3306
# DB_USERNAME=root
# DB_PASSWORD=your_password
# DB_NAME=bookstore_management_system
# SECRET_KEY=your-secret-key
```

### 4. 启动后端服务

```bash
python app.py
# 默认运行在 http://localhost:5000
```

### 5. 启动用户端前端

```bash
cd 线上图书系统

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 访问 http://localhost:5173
```

### 6. 启动管理端前端

```bash
cd 图书后台管理

# 安装依赖
npm install

# 启动开发服务器
npm run dev
# 访问 http://localhost:5174
```

## 📦 构建部署

### 前端构建

```bash
# 用户端
cd 线上图书系统
npm run build

# 管理端
cd 图书后台管理
npm run build
```

构建产物在 `dist/` 目录下，可部署到任何静态服务器。

### 后端部署

```bash
cd backend

# 生产环境推荐使用 gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔧 开发指南

### 代码规范

- TypeScript 严格模式
- 使用 Composition API
- 组件采用 `<script setup>` 语法
- SCSS 样式采用 BEM 命名规范

### API 接口规范

```typescript
// 统一响应格式
{
  code: number,      // 状态码
  message: string,   // 提示信息
  data?: any        // 响应数据
}
```

### 样式指南

- 采用 iOS 设计规范
- 主色调: `#007aff` (iOS Blue)
- 成功色: `#34c759` (iOS Green)
- 危险色: `#ff3b30` (iOS Red)
- 圆角: `20px` (卡片), `12px` (按钮)
- 毛玻璃效果: `backdrop-filter: blur(20px)`

<img width="1892" height="990" alt="image" src="https://github.com/user-attachments/assets/d08f7ea5-86ee-4491-accf-05fae931f1a3" />
<img width="1763" height="991" alt="image" src="https://github.com/user-attachments/assets/93dcf013-e306-44ae-a96f-01869207d27f" />
<img width="1509" height="979" alt="image" src="https://github.com/user-attachments/assets/c629856e-5d2c-4f30-9075-c3ab80bb2a07" />
<img width="1392" height="792" alt="image" src="https://github.com/user-attachments/assets/68f0f2eb-6404-4e81-ac9b-e60583bc29f4" />
<img width="1861" height="972" alt="image" src="https://github.com/user-attachments/assets/0688ab49-ed73-46f9-89af-2c95d0ff486f" />


