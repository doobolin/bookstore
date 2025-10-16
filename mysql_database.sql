-- MySQL数据库设计 - 线上书店管理系统
-- 此脚本包含系统的核心表结构设计
-- 注意：根据需求，先不设计图书相关表

-- 创建数据库
CREATE DATABASE IF NOT EXISTS bookstore_management_system;
USE bookstore_management_system;

-- 1. 用户表 - 存储系统用户信息
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
  password VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
  email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
  role ENUM('admin', 'user') NOT NULL DEFAULT 'user' COMMENT '角色（管理员/普通用户）',
  status ENUM('active', 'inactive') NOT NULL DEFAULT 'active' COMMENT '状态（活跃/禁用）',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

-- 2. 权限表 - 存储系统权限信息（用于更精细的权限控制）
CREATE TABLE IF NOT EXISTS permissions (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '权限ID',
  name VARCHAR(50) NOT NULL COMMENT '权限名称',
  description VARCHAR(255) COMMENT '权限描述',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统权限表';

-- 3. 角色权限关联表 - 存储角色与权限的多对多关系
CREATE TABLE IF NOT EXISTS role_permissions (
  role_name ENUM('admin', 'user') NOT NULL COMMENT '角色名称',
  permission_id INT NOT NULL COMMENT '权限ID',
  PRIMARY KEY (role_name, permission_id),
  FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';

-- 4. 操作日志表 - 记录系统关键操作
CREATE TABLE IF NOT EXISTS operation_logs (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
  user_id INT COMMENT '操作用户ID',
  operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
  operation_desc TEXT COMMENT '操作描述',
  ip_address VARCHAR(50) COMMENT 'IP地址',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统操作日志表';


INSERT INTO users (username, password, email, role, status) 
VALUES ('admin', '$2a$10$Q4V8C3e0D1r5T6y7U8i9o7P3L2K1J0H9G8F7E6D5C4B3A2', 'admin@example.com', 'admin', 'active');

-- 插入初始权限数据
INSERT INTO permissions (name, description) VALUES
('user_manage', '用户管理权限'),
('system_config', '系统配置权限'),
('log_view', '日志查看权限');

-- 为管理员角色分配权限
INSERT INTO role_permissions (role_name, permission_id) VALUES
('admin', 1),
('admin', 2),
('admin', 3);

-- 创建索引以提高查询性能
ALTER TABLE users ADD INDEX idx_username (username);
ALTER TABLE users ADD INDEX idx_email (email);
ALTER TABLE operation_logs ADD INDEX idx_user_id (user_id);
ALTER TABLE operation_logs ADD INDEX idx_created_at (created_at);

-- 创建视图用于简化常用查询
CREATE VIEW v_active_users AS
SELECT id, username, email, role, created_at, updated_at
FROM users
WHERE status = 'active';


-- 5. 图书分类表 - 存储图书分类信息
CREATE TABLE IF NOT EXISTS categories (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID',
  name VARCHAR(50) NOT NULL UNIQUE COMMENT '分类名称',
  description VARCHAR(255) COMMENT '分类描述',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书分类表';

-- 6. 图书表 - 存储图书信息
CREATE TABLE IF NOT EXISTS books (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '图书ID',
  isbn VARCHAR(20) UNIQUE COMMENT '国际标准书号(ISBN)',
  title VARCHAR(100) NOT NULL COMMENT '书名',
  author VARCHAR(100) NOT NULL COMMENT '作者',
  category_id INT COMMENT '分类ID',
  description TEXT COMMENT '图书描述',
  price DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '价格',
  stock INT NOT NULL DEFAULT 0 COMMENT '库存数量',
  rating DECIMAL(3,2) DEFAULT 0.00 COMMENT '评分(0-5分)',
  image VARCHAR(255) COMMENT '图书封面图片路径',
  status ENUM('available', 'unavailable') NOT NULL DEFAULT 'available' COMMENT '状态（可借阅/不可借阅）',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书表';

-- 确保图书ID从1开始递增排列
ALTER TABLE books AUTO_INCREMENT = 1;

-- 7. 图书销售记录表 - 记录图书的销售情况
CREATE TABLE IF NOT EXISTS sales_records (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '销售记录ID',
  user_id INT COMMENT '购买用户ID',
  book_id INT NOT NULL COMMENT '图书ID',
  quantity INT NOT NULL DEFAULT 1 COMMENT '销售数量',
  unit_price DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '单价',
  total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '销售总金额',
  sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '销售日期',
  order_number VARCHAR(100) UNIQUE COMMENT '订单编号',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书销售记录表';

-- 8. 图书评论表 - 存储用户对图书的评论和评分
CREATE TABLE IF NOT EXISTS reviews (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '评论ID',
  user_id INT NOT NULL COMMENT '用户ID',
  book_id INT NOT NULL COMMENT '图书ID',
  rating INT NOT NULL COMMENT '评分(1-5分)',
  comment TEXT COMMENT '评论内容',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='图书评论表';

-- 插入初始图书分类数据
INSERT INTO categories (name, description) VALUES
('技术', '计算机科学、编程、软件开发等相关图书'),
('文学', '小说、诗歌、散文等文学作品'),
('历史', '历史事件、人物传记等历史类图书'),
('科学', '自然科学、社会科学等学术类图书'),
('艺术', '绘画、音乐、设计等艺术类图书'),
('哲学', '哲学思想、逻辑学等哲学类图书'),
('心理学', '心理学理论、心理辅导等心理学类图书'),
('经济', '经济学理论、金融投资等经济类图书'),
('管理', '企业管理、项目管理等管理类图书'),
('生活', '生活技巧、健康养生等生活类图书');

-- 插入示例图书数据
INSERT INTO books (isbn, title, author, category_id, description, price, stock, rating, image, status) VALUES
('978-7115531291', 'Vue.js 3 权威指南', '尤雨溪', 1, '全面掌握Vue 3的Composition API和最新特性', 89.00, 50, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7115529823', 'React 深度指南', 'Dan Abramov', 1, '深入理解React的Hook系统和性能优化', 99.00, 30, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7544291195', '百年孤独', '加西亚·马尔克斯', 2, '魔幻现实主义文学代表作，布恩迪亚家族的传奇故事', 55.00, 100, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7506394328', '活着', '余华', 2, '讲述了福贵苦难的一生，展现了生命的顽强', 39.00, 80, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7508672065', '人类简史', '尤瓦尔·赫拉利', 3, '从认知革命到科学革命，人类如何征服世界', 68.00, 60, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7535794567', '时间简史', '史蒂芬·霍金', 4, '探索宇宙的起源和命运，从大爆炸到黑洞', 49.00, 40, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7544777151', '艺术的故事', '贡布里希', 5, '西方艺术史的入门经典，图文并茂', 128.00, 20, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7544748118', '苏菲的世界', '乔斯坦·贾德', 6, '通过少女苏菲的故事讲述西方哲学史', 42.00, 70, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7115534384', 'JavaScript高级程序设计', 'Nicholas C. Zakas', 1, '全面覆盖JavaScript核心概念与高级特性', 99.00, 45, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7115528086', 'Python编程：从入门到实践', 'Eric Matthes', 1, '适合初学者的Python入门书籍，包含实际项目', 79.00, 65, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7115515142', '设计模式：可复用面向对象软件的基础', 'Erich Gamma', 1, '介绍23种设计模式的经典著作', 88.00, 35, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7111647716', '算法导论', 'Thomas H. Cormen', 1, '计算机算法领域的经典教材', 128.00, 30, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7111607950', '深入理解计算机系统', 'Randal E. Bryant', 1, '系统级编程和计算机系统的综合介绍', 118.00, 25, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7115523364', '编程珠玑', 'Jon Bentley', 1, '程序员的思考训练指南', 69.00, 40, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7020135106', '红楼梦', '曹雪芹', 2, '中国古典文学四大名著之一', 45.00, 120, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7020135342', '西游记', '吴承恩', 2, '中国古典文学四大名著之一', 42.00, 110, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7020135359', '三国演义', '罗贯中', 2, '中国古典文学四大名著之一', 48.00, 105, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7020135335', '水浒传', '施耐庵', 2, '中国古典文学四大名著之一', 46.00, 100, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7020133980', '围城', '钱钟书', 2, '现代文学经典之作，幽默而深刻', 38.00, 85, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7020133973', '平凡的世界', '路遥', 2, '讲述中国农村变革时期的普通人生活', 59.00, 95, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7101126565', '中国通史', '吕思勉', 3, '中国历史的全面介绍', 78.00, 55, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7544771425', '世界简史', '赫伯特·乔治·威尔斯', 3, '简明世界历史概述', 68.00, 60, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7506355447', '明朝那些事儿', '当年明月', 3, '通俗有趣的明朝历史解读', 88.00, 75, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7506386739', '全球通史', '斯塔夫里阿诺斯', 3, '从史前到21世纪的全球历史', 98.00, 50, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7542871496', '自然哲学的数学原理', '艾萨克·牛顿', 4, '经典物理学著作', 79.00, 40, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7542871489', '物种起源', '查尔斯·达尔文', 4, '进化论的奠基之作', 69.00, 45, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7542871472', '相对论', '阿尔伯特·爱因斯坦', 4, '相对论理论的系统阐述', 68.00, 35, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7542871465', '化学元素周期表', '德米特里·门捷列夫', 4, '化学元素分类的基础理论', 78.00, 30, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7542871458', '宇宙的奥秘', '卡尔·萨根', 4, '探索宇宙的奥秘与人类的未来', 88.00, 55, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7544777152', '艺术的故事', '贡布里希', 5, '西方艺术史的入门经典', 128.00, 25, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7544777168', '色彩理论', '约瑟夫·阿尔伯斯', 5, '现代色彩理论的基础著作', 89.00, 30, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7544777175', '设计心理学', '唐纳德·诺曼', 5, '从心理学角度解析设计原则', 78.00, 45, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7544777182', '音乐理论基础', '沃尔特·辟斯顿', 5, '音乐理论的系统学习教材', 89.00, 40, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7101123885', '论语', '孔子', 6, '儒家思想的经典著作', 35.00, 90, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7544777199', '理想国', '柏拉图', 6, '西方哲学的经典著作', 48.00, 50, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7544777205', '纯粹理性批判', '伊曼努尔·康德', 6, '德国古典哲学的代表作品', 68.00, 40, 4.6, '/images/book-placeholder.svg', 'available'),
('978-7544777212', '存在与时间', '马丁·海德格尔', 6, '存在主义哲学的重要著作', 79.00, 35, 4.5, '/images/book-placeholder.svg', 'available'),
('978-7544777229', '心理学与生活', '理查德·格里格', 7, '心理学入门的经典教材', 89.00, 60, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7544777236', '梦的解析', '西格蒙德·弗洛伊德', 7, '精神分析学的奠基之作', 59.00, 55, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7544777243', '思考，快与慢', '丹尼尔·卡尼曼', 7, '行为经济学的重要著作', 79.00, 70, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7543233782', '经济学原理', '格里高利·曼昆', 8, '经济学入门的经典教材', 98.00, 65, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7543233799', '国富论', '亚当·斯密', 8, '经济学的奠基之作', 68.00, 50, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7543233805', '资本论', '卡尔·马克思', 8, '马克思主义政治经济学的经典著作', 79.00, 45, 4.6, '/images/book-placeholder.svg', 'available'),
('978-7508686218', '原则', '雷·达里奥', 9, '生活和工作的原则指南', 89.00, 80, 4.8, '/images/book-placeholder.svg', 'available'),
('978-7544777250', '领导力21法则', '约翰·麦克斯韦尔', 9, '领导力培养的核心法则', 78.00, 65, 4.7, '/images/book-placeholder.svg', 'available'),
('978-7544777267', '高效能人士的七个习惯', '史蒂芬·柯维', 9, '个人管理和效能提升的经典', 68.00, 95, 4.9, '/images/book-placeholder.svg', 'available'),
('978-7544290754', '断舍离', '山下英子', 10, '极简生活方式的实践指南', 58.00, 85, 4.7, '/images/book-placeholder.svg', 'available');

-- 创建索引以提高查询性能
ALTER TABLE books ADD INDEX idx_title (title);
ALTER TABLE books ADD INDEX idx_author (author);
ALTER TABLE books ADD INDEX idx_category_id (category_id);
ALTER TABLE sales_records ADD INDEX idx_user_id (user_id);
ALTER TABLE sales_records ADD INDEX idx_book_id (book_id);
ALTER TABLE sales_records ADD INDEX idx_sale_date (sale_date);
ALTER TABLE reviews ADD INDEX idx_user_id (user_id);
ALTER TABLE reviews ADD INDEX idx_book_id (book_id);

-- 创建视图用于简化常用查询
CREATE VIEW v_book_with_category AS
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
  b.status, 
  b.created_at, 
  b.updated_at
FROM books b
LEFT JOIN categories c ON b.category_id = c.id;

CREATE VIEW v_popular_books AS
SELECT 
  b.id, 
  b.title, 
  b.author, 
  b.price, 
  b.rating, 
  COUNT(r.id) AS review_count
FROM books b
LEFT JOIN reviews r ON b.id = r.book_id
WHERE b.rating >= 4.5
GROUP BY b.id
ORDER BY b.rating DESC, review_count DESC
LIMIT 10;

-- 图书管理相关权限
INSERT INTO permissions (name, description) VALUES
('book_manage', '图书管理权限'),
('category_manage', '分类管理权限'),
('sales_manage', '销售记录管理权限'),
('review_manage', '评论管理权限');

-- 为管理员角色分配图书管理相关权限
INSERT INTO role_permissions (role_name, permission_id) VALUES
('admin', (SELECT id FROM permissions WHERE name = 'book_manage')),
('admin', (SELECT id FROM permissions WHERE name = 'category_manage')),
('admin', (SELECT id FROM permissions WHERE name = 'sales_manage')),
('admin', (SELECT id FROM permissions WHERE name = 'review_manage'));

-- 数据库维护建议：
-- 1. 定期更新图书评分和统计数据
-- 2. 定期清理过期的交易记录
-- 3. 定期备份数据库以防止数据丢失
-- 4. 优化查询性能，根据实际业务需求创建更多索引