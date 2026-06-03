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
    avatar_url VARCHAR(255) DEFAULT NULL COMMENT '用户头像URL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) ENGINE=InnoDB COMMENT='用户表';

-- 4. 创建商品表 (products)
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '商品主键ID',
    seller_id INT NOT NULL COMMENT '卖家ID',
    title VARCHAR(100) NOT NULL COMMENT '商品标题',
    description TEXT COMMENT '商品详细描述',
    category ENUM('textbook','electronics','daily','clothing','sports','other') DEFAULT 'other' COMMENT '商品分类',
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

-- 7. 索引：加速商品列表查询与排序
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_created_at ON products(created_at);
CREATE INDEX idx_products_price ON products(price);

-- 8. 创建商品多图表 (product_images)
CREATE TABLE product_images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '图片主键ID',
    product_id INT NOT NULL COMMENT '商品ID',
    image_url VARCHAR(255) NOT NULL COMMENT '图片路径',
    sort_order TINYINT UNSIGNED DEFAULT 0 COMMENT '排序序号(0-4)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_product_images_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品多图表';

-- 9. 创建收藏表 (favorites)
CREATE TABLE favorites (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '收藏主键ID',
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT NOT NULL COMMENT '商品ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_product (user_id, product_id),
    INDEX idx_favorites_user_id (user_id),
    INDEX idx_favorites_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏/心愿单表';

-- 10. 创建评价表 (reviews)
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评价主键ID',
    order_id INT NOT NULL COMMENT '关联订单ID',
    reviewer_id INT NOT NULL COMMENT '评价者ID',
    reviewee_id INT NOT NULL COMMENT '被评价者ID',
    rating TINYINT UNSIGNED NOT NULL COMMENT '评分(1-5星)',
    comment TEXT COMMENT '评价内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '评价时间',
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewee_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_order_reviewer (order_id, reviewer_id),
    INDEX idx_reviews_reviewee_id (reviewee_id),
    INDEX idx_reviews_reviewer_id (reviewer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='交易互评表';

-- 11. 追加索引：加速消息查询
ALTER TABLE messages ADD INDEX idx_messages_sender_receiver (sender_id, receiver_id);
ALTER TABLE messages ADD INDEX idx_messages_created_at (created_at);