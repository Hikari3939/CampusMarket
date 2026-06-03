# app/api/order.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Product, Order
from datetime import datetime
import uuid

# 创建订单蓝图
order_bp = Blueprint('order', __name__)

@order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """
    创建订单（购买商品）
    路径: POST /api/orders
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    # 1. 参数校验
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({"msg": "缺少商品ID"}), 400

    # 2. 获取商品并加行级悲观锁 (with_for_update) 防止超卖/并发购买
    try:
        product = db.session.query(Product).with_for_update().filter_by(id=product_id).first()
        
        if not product:
            return jsonify({"msg": "商品不存在"}), 404
            
        if product.status == 'deleted':
            return jsonify({"msg": "该商品已下架或删除"}), 400
            
        if product.status == 'sold':
            return jsonify({"msg": "手慢了，该商品已被抢购"}), 400
            
        if product.seller_id == current_user_id:
            return jsonify({"msg": "不能购买自己发布的商品"}), 400

        # 3. 核心业务：生成订单号
        # 格式: 年月日时分秒 + UUID前8位
        order_no = datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex[:8].upper()

        # 4. 创建订单快照
        new_order = Order(
            order_no=order_no,
            buyer_id=current_user_id,
            seller_id=product.seller_id,
            product_id=product.id,
            deal_price=product.price,  # 记录当时的成交价快照
            status='completed'
        )
        db.session.add(new_order)

        # 5. 修改商品状态为已售
        product.status = 'sold'

        # 6. 提交数据库事务
        db.session.commit()

        return jsonify({
            "msg": "购买成功",
            "data": {
                "order_id": new_order.id,
                "order_no": new_order.order_no,
                "deal_price": float(new_order.deal_price)
            }
        }), 201

    except Exception as e:
        # 严格遵守规范：异常时必须 rollback，保证数据原子性
        db.session.rollback()
        return jsonify({"msg": "服务器内部错误，交易失败"}), 500


@order_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
    """
    取消订单（仅买家可操作，恢复商品为上架状态）
    路径: PUT /api/orders/<id>/cancel
    """
    current_user_id = int(get_jwt_identity())
    order = Order.query.get(order_id)

    if not order:
        return jsonify({"msg": "订单不存在"}), 404

    if order.buyer_id != current_user_id:
        return jsonify({"msg": "无权操作他人的订单"}), 403

    if order.status == 'cancelled':
        return jsonify({"msg": "订单已经被取消"}), 400

    if order.status != 'completed':
        return jsonify({"msg": "该订单状态不允许取消"}), 400

    # 检查关联商品，仅当商品仍为 sold 状态时才恢复
    product = Product.query.get(order.product_id)
    if not product or product.status != 'sold':
        return jsonify({"msg": "商品状态异常，无法取消"}), 400

    try:
        order.status = 'cancelled'
        product.status = 'active'  # 恢复商品为在售
        db.session.commit()
        return jsonify({"msg": "订单已取消，商品已重新上架"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "取消失败"}), 500