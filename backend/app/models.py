# app/models.py
from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(255), comment='用户头像URL')
    created_at = db.Column(db.DateTime, default=datetime.now)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='商品主键ID')
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='卖家ID')
    title = db.Column(db.String(100), nullable=False, comment='商品标题')
    description = db.Column(db.Text, comment='商品详细描述')
    category = db.Column(
        db.Enum('textbook', 'electronics', 'daily', 'clothing', 'sports', 'other'),
        default='other',
        comment='商品分类'
    )
    price = db.Column(db.Numeric(10, 2), nullable=False, comment='商品价格')
    image_url = db.Column(db.String(255), comment='商品图片本地存储路径')
    status = db.Column(db.Enum('active', 'sold', 'deleted'), default='active', comment='状态')
    
    created_at = db.Column(db.DateTime, default=datetime.now, comment='发布时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='最后更新时间')

    # 定义关系，方便连表查询获取卖家信息
    seller = db.relationship('User', backref=db.backref('products', lazy=True))
    images = db.relationship('ProductImage', backref='product', lazy=True, order_by='ProductImage.sort_order',
                             cascade='all, delete-orphan')

    def to_dict(self):
        """将对象转化为字典，方便 JSON 序列化返回给前端"""
        # 获取多图列表（按 sort_order 排序）
        image_list = [img.image_url for img in self.images] if self.images else []
        # 向后兼容：如果有多图，image_url 取第一张；否则保留旧字段
        primary_image = image_list[0] if image_list else self.image_url

        return {
            "id": self.id,
            "seller_id": self.seller_id,
            "seller_name": self.seller.username, # 连表获取卖家名称
            "seller_avatar_url": self.seller.avatar_url,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "price": float(self.price), # Decimal 类型需要转 float 才能 JSON 序列化
            "image_url": primary_image,
            "image_urls": image_list,  # 多图列表
            "status": self.status,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_no = db.Column(db.String(50), unique=True, nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    deal_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum('completed', 'cancelled'), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 定义关系映射，方便联合查询
    product = db.relationship('Product', backref='orders')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='bought_orders')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='sold_orders')

class ProductImage(db.Model):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    sort_order = db.Column(db.SmallInteger, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    product = db.relationship('Product', backref='favorited_by')


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='评价主键ID')
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, comment='关联订单ID')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='评价者ID')
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='被评价者ID')
    rating = db.Column(db.SmallInteger, nullable=False, comment='评分(1-5星)')
    comment = db.Column(db.Text, comment='评价内容')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='评价时间')

    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='given_reviews')
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], backref='received_reviews')
    order = db.relationship('Order', backref='reviews')


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='消息主键ID')
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='发送方ID')
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='接收方ID')
    content = db.Column(db.Text, nullable=False, comment='消息内容')
    is_read = db.Column(db.Boolean, default=False, comment='是否已读: 0未读, 1已读')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='发送时间')

    # 定义双向关系便于关联查询
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')