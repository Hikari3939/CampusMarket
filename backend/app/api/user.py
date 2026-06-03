# app/api/user.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Product, Order
from app.extensions import db

# 创建用户蓝图
user_bp = Blueprint('user', __name__)
    
@user_bp.route('/me/published', methods=['GET'])
@jwt_required()
def get_my_published():
    """
    获取我发布的商品历史
    路径: GET /api/users/me/published
    """
    current_user_id = int(get_jwt_identity())
    
    # 按照创建时间倒序排列
    products = Product.query.filter_by(seller_id=current_user_id).order_by(Product.created_at.desc()).all()
    
    # 序列化数据
    data = []
    for p in products:
        data.append({
            "id": p.id,
            "title": p.title,
            "price": float(p.price),
            "image_url": p.image_url,
            "status": p.status, # 前端可根据 status('active', 'sold', 'deleted') 显示不同标签
            "created_at": p.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return jsonify({
        "msg": "获取发布历史成功",
        "data": data
    }), 200


@user_bp.route('/me/bought', methods=['GET'])
@jwt_required()
def get_my_bought():
    """
    获取我购买的订单历史
    路径: GET /api/users/me/bought
    """
    current_user_id = int(get_jwt_identity())
    
    # 查询买家为当前用户的订单，并关联查询商品信息
    orders = Order.query.filter_by(buyer_id=current_user_id).order_by(Order.created_at.desc()).all()
    
    data = []
    for order in orders:
        # 因为在 models 中定义了 relationship，可以直接访问 order.product
        product = order.product
        data.append({
            "order_id": order.id,
            "order_no": order.order_no,
            "deal_price": float(order.deal_price),
            "order_status": order.status,
            "order_time": order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "product": {
                "id": product.id,
                "title": product.title,
                "image_url": product.image_url,
                "seller_name": order.seller.username # 关联获取卖家名称
            }
        })
        
    return jsonify({
        "msg": "获取购买历史成功",
        "data": data
    }), 200