-- 1. 创建数据库并设置字符集为 utf8mb4
CREATE DATABASE IF NOT EXISTS campus_market DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 切换到该数据库
USE campus_market;

-- 3. 创建用户表 (users)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱(可作为登录账号)',
    password_hash VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB COMMENT='用户表';

-- 4. 创建商品表 (products)
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '商品主键ID',
    seller_id INT NOT NULL COMMENT '卖家ID',
    title VARCHAR(100) NOT NULL COMMENT '商品标题',
    description TEXT COMMENT '商品详细描述',
    price DECIMAL(10, 2) NOT NULL COMMENT '商品价格',
    image_url VARCHAR(255) COMMENT '商品图片本地存储路径',
    status ENUM('active', 'sold', 'deleted') DEFAULT 'active' COMMENT '状态: active在售, sold已售, deleted删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='商品表';

-- 5. 创建订单表 (orders)
-- 记录交易历史，关联买家、卖家和商品
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单主键ID',
    order_no VARCHAR(50) NOT NULL UNIQUE COMMENT '订单流水号',
    buyer_id INT NOT NULL COMMENT '买家ID',
    seller_id INT NOT NULL COMMENT '卖家ID',
    product_id INT NOT NULL COMMENT '商品ID',
    deal_price DECIMAL(10, 2) NOT NULL COMMENT '成交价格(快照)',
    status ENUM('completed', 'cancelled') DEFAULT 'completed' COMMENT '订单状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '交易时间',
    FOREIGN KEY (buyer_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (seller_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
) ENGINE=InnoDB COMMENT='订单流水表';

-- 6. 创建私信表 (messages)
-- 用于支持买卖双方的实时聊天历史记录
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '消息主键ID',
    sender_id INT NOT NULL COMMENT '发送方ID',
    receiver_id INT NOT NULL COMMENT '接收方ID',
    content TEXT NOT NULL COMMENT '消息内容',
    is_read TINYINT(1) DEFAULT 0 COMMENT '是否已读: 0未读, 1已读',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='私信聊天记录表';