-- ============================================
-- 购物车和订单系统数据库表
-- 执行方式: mysql -u root -p bookstore_management_system < add_cart_order_tables.sql
-- ============================================

USE bookstore_management_system;

-- 1. 购物车表
CREATE TABLE IF NOT EXISTS shopping_cart (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '购物车项ID',
  user_id INT NOT NULL COMMENT '用户ID',
  book_id INT NOT NULL COMMENT '图书ID',
  quantity INT NOT NULL DEFAULT 1 COMMENT '数量',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '添加时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
  UNIQUE KEY unique_user_book (user_id, book_id) COMMENT '同一用户同一本书只能有一条记录'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='购物车表';

-- 2. 订单主表
CREATE TABLE IF NOT EXISTS orders (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
  order_number VARCHAR(50) UNIQUE NOT NULL COMMENT '订单编号',
  user_id INT NOT NULL COMMENT '用户ID',
  total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '订单总金额',
  status ENUM('pending', 'paid', 'shipped', 'completed', 'cancelled')
    NOT NULL DEFAULT 'pending' COMMENT '订单状态：待支付/已支付/已发货/已完成/已取消',
  receiver_name VARCHAR(100) COMMENT '收货人姓名',
  receiver_phone VARCHAR(20) COMMENT '收货人电话',
  receiver_address TEXT COMMENT '收货地址',
  payment_method VARCHAR(50) COMMENT '支付方式',
  payment_time TIMESTAMP NULL COMMENT '支付时间',
  ship_time TIMESTAMP NULL COMMENT '发货时间',
  complete_time TIMESTAMP NULL COMMENT '完成时间',
  cancel_time TIMESTAMP NULL COMMENT '取消时间',
  cancel_reason TEXT COMMENT '取消原因',
  remark TEXT COMMENT '订单备注',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
  INDEX idx_order_number (order_number),
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单主表';

-- 3. 订单明细表
CREATE TABLE IF NOT EXISTS order_items (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单项ID',
  order_id INT NOT NULL COMMENT '订单ID',
  book_id INT NOT NULL COMMENT '图书ID',
  book_title VARCHAR(200) NOT NULL COMMENT '图书标题（冗余，防止图书删除后无法查看）',
  book_author VARCHAR(100) COMMENT '图书作者（冗余）',
  book_isbn VARCHAR(20) COMMENT '图书ISBN（冗余）',
  book_image VARCHAR(255) COMMENT '图书封面（冗余）',
  quantity INT NOT NULL DEFAULT 1 COMMENT '购买数量',
  unit_price DECIMAL(10,2) NOT NULL COMMENT '单价',
  subtotal DECIMAL(10,2) NOT NULL COMMENT '小计',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
  INDEX idx_order_id (order_id),
  INDEX idx_book_id (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单明细表';

-- 插入示例数据（可选）
-- 为admin用户添加一些购物车示例数据
INSERT INTO shopping_cart (user_id, book_id, quantity) VALUES
(1, 1, 1),
(1, 3, 2)
ON DUPLICATE KEY UPDATE quantity=quantity;

-- 显示创建结果
SELECT 'shopping_cart表创建成功' AS result;
SELECT 'orders表创建成功' AS result;
SELECT 'order_items表创建成功' AS result;
SELECT '所有表创建完成！' AS result;

-- 查看表结构
DESCRIBE shopping_cart;
DESCRIBE orders;
DESCRIBE order_items;
