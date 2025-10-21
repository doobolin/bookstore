# 线上图书系统 - 系统架构文档

## 📋 项目概述

**项目名称**：线上图书系统 (Online Bookstore System)  
**技术栈**：Vue 3 + TypeScript + Flask + MySQL  
**设计风格**：赛博朋克 / 翠绿色主题  
**开发时间**：2024年  

---

## 🏗️ 系统架构

### 三层架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 Frontend Layer                 │
│  Vue 3 + TypeScript + Element Plus + Vite               │
│  - 页面组件 (Home, Login, Register, etc.)               │
│  - 业务组件 (CardContainer, Header, Footer)             │
│  - 特效系统 (Particle, Emoji, Animation)                │
│  - API层 (userApi, bookApi, orderApi)                   │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTP/HTTPS
┌─────────────────────────────────────────────────────────┐
│                    后端层 Backend Layer                  │
│  Flask + SQLAlchemy + Python                            │
│  - 路由处理 (Route Handlers)                            │
│  - 业务逻辑 (Business Logic)                            │
│  - 数据验证 (Data Validation)                           │
│  - API端点 (/api/login, /api/books, etc.)               │
└─────────────────────────────────────────────────────────┘
                            ↓ SQL
┌─────────────────────────────────────────────────────────┐
│                    数据层 Data Layer                     │
│  MySQL Database                                         │
│  - 用户表 (users)                                        │
│  - 图书表 (books)                                        │
│  - 分类表 (categories)                                   │
│  - 订单表 (orders)                                       │
│  - 评论表 (reviews)                                      │
│  - 销售记录 (sales_records)                             │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

### 前端项目结构 (线上图书系统)

```
线上图书系统/
├── src/
│   ├── components/          # 组件目录
│   │   ├── Home.vue         # 主页 (含粒子背景)
│   │   ├── Login.vue        # 登录页 (含粒子背景)
│   │   ├── Register.vue     # 注册页 (含粒子背景)
│   │   ├── BookDetail.vue   # 图书详情
│   │   ├── ShoppingCart.vue # 购物车
│   │   ├── OrderList.vue    # 订单列表
│   │   ├── OrderDetail.vue  # 订单详情
│   │   └── CardContainer.vue # 图书卡片容器
│   ├── api/                 # API接口层
│   │   ├── userApi.ts       # 用户相关API
│   │   ├── bookApi.ts       # 图书相关API
│   │   ├── orderApi.ts      # 订单相关API
│   │   └── axiosInstance.ts # Axios实例配置
│   ├── router/              # 路由配置
│   │   └── index.ts         # 路由定义
│   ├── style/               # 样式文件
│   │   └── reset.scss       # 样式重置
│   ├── App.vue              # 根组件
│   └── main.ts              # 入口文件 (含Emoji特效)
├── public/                  # 静态资源
├── vite.config.ts           # Vite配置
├── package.json             # 依赖配置
└── tsconfig.json            # TypeScript配置
```

### 后端项目结构 (backend)

```
backend/
├── app.py                   # Flask主应用
├── requirements.txt         # Python依赖
├── .env                     # 环境变量 (数据库配置)
└── venv/                    # Python虚拟环境
```

### 数据库结构

```
mysql_database.sql           # 完整数据库脚本
├── 表结构 (Tables)
│   ├── users               # 用户表
│   ├── books               # 图书表
│   ├── categories          # 分类表
│   ├── orders              # 订单表
│   ├── reviews             # 评论表
│   ├── sales_records       # 销售记录
│   ├── permissions         # 权限表
│   ├── role_permissions    # 角色权限映射
│   └── operation_logs      # 操作日志
├── 视图 (Views)
│   ├── v_active_users      # 活跃用户视图
│   ├── v_book_with_category # 图书分类视图
│   └── v_popular_books     # 热门图书视图
└── 索引 (Indexes)
    ├── idx_username        # 用户名索引
    ├── idx_email           # 邮箱索引
    ├── idx_title           # 图书标题索引
    └── idx_category_id     # 分类ID索引
```

---

## 🎨 核心功能模块

### 1. 用户认证模块

**功能**：
- 用户登录 (Login)
- 用户注册 (Register)
- 用户状态检查 (Active/Inactive)
- 角色验证 (User/Admin)

**技术实现**：
- 前端：Vue 3 + Element Plus表单验证
- 后端：Flask路由 + MySQL查询
- 认证：Mock Token (localStorage存储)

**API端点**：
- `POST /api/login` - 用户登录
- `POST /api/register` - 用户注册
- `POST /api/check-user-status` - 检查用户状态

### 2. 图书展示模块

**功能**：
- 图书列表展示 (瀑布流布局)
- 分类筛选
- 搜索功能
- 图书详情查看

**技术实现**：
- 前端：CSS Column布局 (瀑布流)
- 数据：动态获取图书列表
- 样式：纯黑色封面 + 翠绿色主题

**API端点**：
- `GET /api/books` - 获取图书列表
- `GET /api/books/:id` - 获取图书详情
- `GET /api/books/count` - 获取图书统计

### 3. 购物车模块

**功能**：
- 添加商品到购物车
- 数量调整
- 删除商品
- 结算功能

**技术实现**：
- 前端：Vue 3响应式状态管理
- 数据：localStorage + 后端API
- 样式：翠绿色渐变背景

**API端点**：
- `POST /api/cart` - 添加到购物车
- `PUT /api/cart/:id` - 更新购物车
- `DELETE /api/cart/:id` - 删除购物车项

### 4. 订单模块

**功能**：
- 订单创建
- 订单列表查看
- 订单详情查看
- 订单状态管理

**技术实现**：
- 前端：Vue 3 + Element Plus表格
- 后端：Flask + MySQL事务
- 数据：订单表 + 销售记录表

**API端点**：
- `POST /api/orders` - 创建订单
- `GET /api/orders` - 获取订单列表
- `GET /api/orders/:id` - 获取订单详情

### 5. 视觉特效模块 ⭐

**功能**：
- 动态粒子背景 (3个页面)
- 鼠标点击Emoji特效 (全局)
- 欢迎动画 (主页)
- 卡片悬停效果

**技术实现**：

#### 动态粒子背景
- **技术**：Canvas API + requestAnimationFrame
- **粒子数量**：根据屏幕大小动态计算 (面积/5000)
- **颜色系统**：4种翠绿色渐变
- **鼠标交互**：150px影响范围，排斥+放大+变亮
- **网格连接**：自动连接150px内的粒子
- **性能**：60fps流畅动画

#### 鼠标点击Emoji特效
- **技术**：DOM操作 + CSS动画
- **表情列表**：12个精选Emoji (💚✨🌟💎🎯🚀⚡🔥💫🌈🎨📚)
- **动画效果**：向上飞出 + 旋转 + 缩小 + 淡出
- **持续时间**：2秒
- **自动清理**：动画结束后移除DOM

---

## 🔄 数据流设计

### 用户登录流程

```
用户输入 → 前端验证 → API请求 → 后端验证 → 数据库查询 
→ 返回结果 → 保存Token → 跳转主页
```

### 图书浏览流程

```
访问主页 → 初始化粒子背景 → API请求图书列表 → 数据库查询 
→ 返回图书数据 → 渲染图书卡片 → 显示给用户
```

### 购物车流程

```
点击加入购物车 → 更新前端状态 → API请求 → 数据库更新 
→ 返回结果 → 更新购物车显示
```

### 订单流程

```
提交订单 → API请求 → 创建订单记录 → 更新库存 
→ 创建销售记录 → 返回订单信息 → 显示订单详情
```

---

## 🎯 技术特点

### 前端技术特点

1. **Vue 3 Composition API** - 现代化的组件开发方式
2. **TypeScript** - 类型安全，提升代码质量
3. **Element Plus** - 丰富的UI组件库
4. **Vite** - 快速的开发服务器和构建工具
5. **Canvas粒子系统** - 高性能的动画渲染
6. **CSS Column布局** - 瀑布流图书展示
7. **响应式设计** - 适配不同屏幕尺寸

### 后端技术特点

1. **Flask** - 轻量级Python Web框架
2. **SQLAlchemy** - ORM数据库操作
3. **Raw SQL** - 直接SQL查询，性能优化
4. **RESTful API** - 标准化的API设计
5. **CORS支持** - 跨域资源共享

### 数据库技术特点

1. **MySQL** - 成熟稳定的关系型数据库
2. **视图** - 简化复杂查询
3. **索引** - 提升查询性能
4. **事务** - 保证数据一致性

---

## 🚀 性能优化

### 前端性能优化

1. **粒子数量动态计算** - 根据屏幕大小调整粒子数量
2. **requestAnimationFrame** - 使用浏览器优化的动画API
3. **Canvas硬件加速** - GPU加速渲染
4. **DOM自动清理** - Emoji特效2秒后自动移除
5. **响应式窗口适配** - 窗口大小变化时重新初始化
6. **懒加载** - 图片和组件按需加载

### 后端性能优化

1. **数据库索引** - 关键字段建立索引
2. **SQL优化** - 使用JOIN减少查询次数
3. **数据库视图** - 预计算常用查询
4. **连接池** - 复用数据库连接

---

## 📊 数据库设计

### 核心表结构

#### users (用户表)
```sql
- id: INT (主键)
- username: VARCHAR(50) (唯一)
- email: VARCHAR(100) (唯一)
- password: VARCHAR(255)
- role: ENUM('user', 'admin')
- status: ENUM('active', 'inactive')
- created_at: TIMESTAMP
```

#### books (图书表)
```sql
- id: INT (主键)
- title: VARCHAR(200)
- author: VARCHAR(100)
- category_id: INT (外键)
- price: DECIMAL(10,2)
- stock: INT
- rating: DECIMAL(3,2)
- description: TEXT
- created_at: TIMESTAMP
```

#### orders (订单表)
```sql
- id: INT (主键)
- user_id: INT (外键)
- total_amount: DECIMAL(10,2)
- status: ENUM('pending', 'completed', 'cancelled')
- created_at: TIMESTAMP
```

---

## 🎨 设计系统

### 颜色系统

**主题色**：翠绿色系
- Primary: `#10b981`
- Light: `#34d399`, `#6ee7b7`
- Dark: `#059669`, `#047857`, `#065f46`

**背景色**：
- 纯黑: `#000000`

**强调色**：
- 金色: `#fbbf24` (星级评分)

### 字体系统

- 主字体：系统默认字体
- 代码字体：Monospace

### 间距系统

- 小间距：8px, 12px, 16px
- 中间距：20px, 24px, 32px
- 大间距：40px, 48px, 64px

---

## 📝 开发规范

### 代码规范

1. **命名规范**：驼峰命名法 (camelCase)
2. **组件命名**：大驼峰命名法 (PascalCase)
3. **文件命名**：小写 + 连字符 (kebab-case)
4. **注释规范**：关键逻辑必须注释

### Git提交规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 样式调整
refactor: 代码重构
perf: 性能优化
test: 测试相关
chore: 构建/工具相关
```

---

## 🔒 安全考虑

### 当前安全问题 ⚠️

1. **密码存储**：明文存储 (应使用bcrypt加密)
2. **Token验证**：Mock Token (应使用JWT)
3. **SQL注入**：已使用参数化查询 ✅
4. **XSS攻击**：Vue自动转义 ✅
5. **CORS配置**：需要配置CORS策略

### 安全改进建议

1. 使用bcrypt加密密码
2. 实现JWT认证
3. 添加HTTPS支持
4. 配置CORS白名单
5. 添加请求频率限制

---

## 📈 未来优化方向

### 功能扩展

1. **支付系统** - 集成第三方支付
2. **评论系统** - 完善图书评论功能
3. **推荐系统** - 基于用户行为的图书推荐
4. **搜索优化** - 全文搜索 + 模糊匹配
5. **用户中心** - 个人信息管理

### 技术优化

1. **状态管理** - 引入Pinia
2. **服务端渲染** - SSR提升SEO
3. **PWA支持** - 离线访问
4. **国际化** - i18n多语言支持
5. **单元测试** - Jest + Vue Test Utils

---

## 📚 相关文档

- [系统用例分析](./USE_CASE_ANALYSIS.md) - 完整的用例分析文档
- [背景特效总结](./BACKGROUND_AND_EFFECTS_SUMMARY.md)
- [UI重新设计总结](./UI_REDESIGN_SUMMARY.md)
- [CLAUDE.md](../CLAUDE.md) - 项目开发指南

---

**文档版本**：v1.1
**最后更新**：2024年
**维护者**：开发团队

喵~系统架构文档完成啦！🐾✨

