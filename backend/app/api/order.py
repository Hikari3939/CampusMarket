from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Product, Order
from datetime import datetime
import uuid

order_bp = Blueprint('order', __name__)

@order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    product_id = data.get('product_id')
    if not product_id:
        return jsonify({"msg": "缺少商品ID"}), 400

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

        order_no = datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex[:8].upper()

        new_order = Order(
            order_no=order_no,
            buyer_id=current_user_id,
            seller_id=product.seller_id,
            product_id=product.id,
            deal_price=product.price,
            status='completed'
        )
        db.session.add(new_order)

        product.status = 'sold'
        db.session.commit()

        return jsonify({
            "msg": "购买成功",
            "data": {
                "order_id": new_order.id,
                "order_no": new_order.order_no,
                "deal_price": float(new_order.deal_price)
            }
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({"msg": "服务器内部错误，交易失败"}), 500

@order_bp.route('/<int:order_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_order(order_id):
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

    product = Product.query.get(order.product_id)
    if not product or product.status != 'sold':
        return jsonify({"msg": "商品状态异常，无法取消"}), 400

    try:
        order.status = 'cancelled'
        product.status = 'active'
        db.session.commit()
        return jsonify({"msg": "订单已取消，商品已重新上架"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"msg": "取消失败"}), 500
