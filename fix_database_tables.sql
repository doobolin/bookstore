-- ============================================
-- 修复和补充数据库表结构
-- 执行方式: mysql -u root -p bookstore_management_system < fix_database_tables.sql
-- ============================================

USE bookstore_management_system;

-- 删除现有的不完整表（如果存在）
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS shopping_cart;

-- 1. 重新创建购物车表（完整版）
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

-- 2. 重新创建订单主表（简化版）
CREATE TABLE IF NOT EXISTS orders (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
  order_number VARCHAR(50) UNIQUE NOT NULL COMMENT '订单编号',
  user_id INT NOT NULL COMMENT '用户ID',
  total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '订单总金额',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
  INDEX idx_order_number (order_number),
  INDEX idx_user_id (user_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单主表';

-- 3. 重新创建订单明细表（简化版）
CREATE TABLE IF NOT EXISTS order_items (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单项ID',
  order_id INT NOT NULL COMMENT '订单ID',
  book_id INT NOT NULL COMMENT '图书ID',
  quantity INT NOT NULL DEFAULT 1 COMMENT '购买数量',
  subtotal DECIMAL(10,2) NOT NULL COMMENT '小计金额',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
  INDEX idx_order_id (order_id),
  INDEX idx_book_id (book_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单明细表';

-- 显示创建结果
SELECT '购物车和订单表已重新创建！' AS result;

-- 查看表结构
DESCRIBE shopping_cart;
DESCRIBE orders;
DESCRIBE order_items;
