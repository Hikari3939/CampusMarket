# app/api/review.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Review, Order, User

review_bp = Blueprint('review', __name__)


@review_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    """
    创建交易评价
    路径: POST /api/reviews
    Body: { "order_id": 1, "rating": 5, "comment": "卖家态度很好！" }
    规则: 只有订单的买家和卖家可以互评，每人对同一订单只能评价一次
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    order_id = data.get('order_id')
    rating = data.get('rating')
    comment = data.get('comment', '').strip()

    if not order_id:
        return jsonify({"msg": "缺少订单ID"}), 400
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"msg": "评分必须为 1-5 的整数"}), 400

    # 查找订单
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"msg": "订单不存在"}), 404
    if order.status != 'completed':
        return jsonify({"msg": "只能评价已完成的订单"}), 400

    # 确定评价者和被评价者
    if current_user_id == order.buyer_id:
        reviewee_id = order.seller_id
    elif current_user_id == order.seller_id:
        reviewee_id = order.buyer_id
    else:
        return jsonify({"msg": "无权评价该订单"}), 403

    # 检查是否已评价
    existing = Review.query.filter_by(order_id=order_id, reviewer_id=current_user_id).first()
    if existing:
        return jsonify({"msg": "您已经评价过该订单了"}), 400

    try:
        new_review = Review(
            order_id=order_id,
            reviewer_id=current_user_id,
            reviewee_id=reviewee_id,
            rating=rating,
            comment=comment
        )
        db.session.add(new_review)
        db.session.commit()

        return jsonify({
            "msg": "评价成功",
            "data": {
                "id": new_review.id,
                "rating": new_review.rating,
                "comment": new_review.comment,
                "created_at": new_review.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "评价失败"}), 500


@review_bp.route('/check/<int:order_id>', methods=['GET'])
@jwt_required()
def check_reviewed(order_id):
    """
    检查当前用户是否已评价某订单
    路径: GET /api/reviews/check/<order_id>
    返回: { "data": { "reviewed": true } }
    """
    current_user_id = int(get_jwt_identity())
    existing = Review.query.filter_by(order_id=order_id, reviewer_id=current_user_id).first()
    return jsonify({
        "data": {"reviewed": existing is not None}
    }), 200
