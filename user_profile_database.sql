-- ============================================
-- 用户资料扩展数据库脚本
-- 执行方式: mysql -u root -p bookstore_management_system < user_profile_database.sql
-- ============================================

USE bookstore_management_system;

-- 1. 扩展用户表 - 添加个人资料字段
ALTER TABLE users ADD COLUMN nickname VARCHAR(50) COMMENT '昵称' AFTER username;
ALTER TABLE users ADD COLUMN phone VARCHAR(20) COMMENT '手机号' AFTER email;
ALTER TABLE users ADD COLUMN avatar VARCHAR(255) COMMENT '头像URL' AFTER phone;
ALTER TABLE users ADD COLUMN gender ENUM('male', 'female', 'other') DEFAULT 'other' COMMENT '性别' AFTER avatar;
ALTER TABLE users ADD COLUMN birthday DATE COMMENT '生日' AFTER gender;

-- 2. 创建收货地址表
CREATE TABLE IF NOT EXISTS shipping_addresses (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '地址ID',
  user_id INT NOT NULL COMMENT '用户ID',
  receiver_name VARCHAR(50) NOT NULL COMMENT '收货人姓名',
  receiver_phone VARCHAR(20) NOT NULL COMMENT '收货人手机号',
  province VARCHAR(50) NOT NULL COMMENT '省份',
  city VARCHAR(50) NOT NULL COMMENT '城市',
  district VARCHAR(50) NOT NULL COMMENT '区/县',
  detail_address VARCHAR(255) NOT NULL COMMENT '详细地址',
  postal_code VARCHAR(10) COMMENT '邮政编码',
  is_default TINYINT(1) DEFAULT 0 COMMENT '是否默认地址(0-否, 1-是)',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_is_default (is_default)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收货地址表';

-- 3. 为订单表添加收货地址字段
ALTER TABLE orders ADD COLUMN shipping_address_id INT COMMENT '收货地址ID' AFTER user_id;
ALTER TABLE orders ADD COLUMN receiver_name VARCHAR(50) COMMENT '收货人姓名' AFTER shipping_address_id;
ALTER TABLE orders ADD COLUMN receiver_phone VARCHAR(20) COMMENT '收货人手机号' AFTER receiver_name;
ALTER TABLE orders ADD COLUMN shipping_address TEXT COMMENT '收货地址详情' AFTER receiver_phone;
ALTER TABLE orders ADD COLUMN order_status ENUM('pending', 'paid', 'shipped', 'completed', 'cancelled') DEFAULT 'pending' COMMENT '订单状态' AFTER total_amount;
ALTER TABLE orders ADD COLUMN payment_method VARCHAR(50) COMMENT '支付方式' AFTER order_status;
ALTER TABLE orders ADD COLUMN remark TEXT COMMENT '订单备注' AFTER payment_method;

-- 4. 更新现有用户数据 - 为admin用户添加默认资料
UPDATE users
SET nickname = '系统管理员',
    phone = '13800138000',
    gender = 'other'
WHERE username = 'admin' AND nickname IS NULL;

-- 5. 插入示例收货地址（可选）
INSERT INTO shipping_addresses (user_id, receiver_name, receiver_phone, province, city, district, detail_address, postal_code, is_default) VALUES
(1, '张三', '13800138000', '北京市', '北京市', '朝阳区', '三里屯街道10号楼101室', '100020', 1);

-- 显示创建结果
SELECT '用户资料扩展表已创建！' AS result;

-- 查看新表结构
DESCRIBE shipping_addresses;

-- 查看用户表更新后的结构
DESCRIBE users;
DESCRIBE orders;

SELECT '数据库扩展完成！包含以下新功能：' AS message;
SELECT '1. 用户表扩展（昵称、手机、头像、性别、生日）' AS feature
UNION ALL SELECT '2. 收货地址表'
UNION ALL SELECT '3. 订单表扩展（收货信息、订单状态）';
