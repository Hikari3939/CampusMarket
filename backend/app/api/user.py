# app/api/user.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import Product, Order, User, Review
from app.extensions import db
from app.api.auth import validate_password_strength

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
            "category": p.category,
            "status": p.status,
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
                "seller_name": order.seller.username
            }
        })

    return jsonify({
        "msg": "获取购买历史成功",
        "data": data
    }), 200


@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    修改个人资料（支持用户名和头像）
    路径: PUT /api/users/me
    支持 JSON: { "username": "新用户名" }
    支持 FormData: username + avatar(文件)
    """
    current_user_id = int(get_jwt_identity())

    # 判断请求类型：JSON 还是 FormData
    if request.is_json:
        data = request.get_json()
        username = data.get('username', '').strip()
        avatar_file = None
    else:
        username = request.form.get('username', '').strip()
        avatar_file = request.files.get('avatar')

    if not username:
        return jsonify({"msg": "用户名不能为空"}), 400
    if len(username) < 2 or len(username) > 50:
        return jsonify({"msg": "用户名长度应在2-50个字符之间"}), 400

    # 检查用户名是否被其他用户占用
    existing = User.query.filter(User.username == username, User.id != current_user_id).first()
    if existing:
        return jsonify({"msg": "该用户名已被使用"}), 400

    user = User.query.get(current_user_id)
    user.username = username

    # 处理头像上传
    if avatar_file and avatar_file.filename != '':
        allowed_exts = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
        ext = avatar_file.filename.rsplit('.', 1)[-1].lower() if '.' in avatar_file.filename else ''
        if ext not in allowed_exts:
            return jsonify({"msg": "不支持的图片格式，仅支持 png, jpg, jpeg, gif"}), 400

        # 删除旧头像文件
        if user.avatar_url:
            old_filename = user.avatar_url.rsplit('/', 1)[-1]
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars', old_filename)
            try:
                if os.path.exists(old_path):
                    os.remove(old_path)
            except OSError:
                pass

        # 保存新头像
        avatars_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.{ext}"
        avatar_file.save(os.path.join(avatars_dir, filename))
        user.avatar_url = f"{request.host_url}static/uploads/avatars/{filename}"

    try:
        db.session.commit()
        return jsonify({
            "msg": "资料更新成功",
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "更新失败"}), 500


@user_bp.route('/me/password', methods=['PUT'])
@jwt_required()
def update_password():
    """
    修改密码（需验证旧密码）
    路径: PUT /api/users/me/password
    Body: { "old_password": "...", "new_password": "..." }
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({"msg": "旧密码和新密码不能为空"}), 400

    user = User.query.get(current_user_id)

    # 验证旧密码
    if not check_password_hash(user.password_hash, old_password):
        return jsonify({"msg": "旧密码不正确"}), 400

    # 新密码强度校验
    is_valid, error_msg = validate_password_strength(new_password)
    if not is_valid:
        return jsonify({"msg": error_msg}), 400

    user.password_hash = generate_password_hash(new_password)

    try:
        db.session.commit()
        return jsonify({"msg": "密码修改成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "修改失败"}), 500


@user_bp.route('/<int:user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    """
    获取用户公开主页（无需登录）
    路径: GET /api/users/<id>/profile
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "用户不存在"}), 404

    # 仅展示在售商品
    products = Product.query.filter_by(
        seller_id=user_id, status='active'
    ).order_by(Product.created_at.desc()).all()

    # 获取评价统计
    avg_rating_result = db.session.query(db.func.avg(Review.rating)).filter(
        Review.reviewee_id == user_id
    ).scalar()
    avg_rating = round(float(avg_rating_result), 1) if avg_rating_result else 0
    review_count = Review.query.filter_by(reviewee_id=user_id).count()

    return jsonify({
        "msg": "获取成功",
        "data": {
            "user": {
                "id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "avg_rating": avg_rating,
                "review_count": review_count
            },
            "products": [p.to_dict() for p in products]
        }
    }), 200


@user_bp.route('/<int:user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):
    """
    获取用户收到的评价列表
    路径: GET /api/users/<id>/reviews
    公开接口，无需登录
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "用户不存在"}), 404

    reviews = Review.query.filter_by(reviewee_id=user_id).order_by(Review.created_at.desc()).all()

    data = []
    for r in reviews:
        data.append({
            "id": r.id,
            "order_id": r.order_id,
            "reviewer": {
                "id": r.reviewer.id,
                "username": r.reviewer.username,
                "avatar_url": r.reviewer.avatar_url
            },
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    avg_rating_result = db.session.query(db.func.avg(Review.rating)).filter(
        Review.reviewee_id == user_id
    ).scalar()
    avg_rating = round(float(avg_rating_result), 1) if avg_rating_result else 0

    return jsonify({
        "msg": "获取成功",
        "data": {
            "reviews": data,
            "avg_rating": avg_rating,
            "review_count": len(data)
        }
    }), 200
