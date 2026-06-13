from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Favorite, Product

favorite_bp = Blueprint('favorite', __name__)

@favorite_bp.route('', methods=['POST'])
@jwt_required()
def toggle_favorite():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data.get('product_id')

    if not product_id:
        return jsonify({"msg": "缺少商品ID"}), 400

    product = Product.query.get(product_id)
    if not product or product.status == 'deleted':
        return jsonify({"msg": "商品不存在或已下架"}), 404

    existing = Favorite.query.filter_by(user_id=current_user_id, product_id=product_id).first()

    if existing:
        try:
            db.session.delete(existing)
            db.session.commit()
            return jsonify({
                "msg": "已取消收藏",
                "data": {"is_favorited": False}
            }), 200
        except Exception:
            db.session.rollback()
            return jsonify({"msg": "操作失败"}), 500
    else:
        try:
            fav = Favorite(user_id=current_user_id, product_id=product_id)
            db.session.add(fav)
            db.session.commit()
            return jsonify({
                "msg": "收藏成功",
                "data": {"is_favorited": True}
            }), 201
        except Exception:
            db.session.rollback()
            return jsonify({"msg": "操作失败"}), 500

@favorite_bp.route('', methods=['GET'])
@jwt_required()
def get_favorites():
    current_user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 1
    elif per_page > 48:
        per_page = 48

    query = Favorite.query \
        .filter_by(user_id=current_user_id) \
        .join(Product) \
        .filter(Product.status == 'active') \
        .order_by(Favorite.created_at.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for fav in paginated.items:
        item = fav.product.to_dict()
        item['favorited_at'] = fav.created_at.strftime('%Y-%m-%d %H:%M:%S')
        data.append(item)

    return jsonify({
        "msg": "获取成功",
        "data": data,
        "pagination": {
            "total": paginated.total,
            "page": page,
            "per_page": per_page,
            "pages": paginated.pages
        }
    }), 200

@favorite_bp.route('/check', methods=['GET'])
@jwt_required()
def check_favorites():
    current_user_id = int(get_jwt_identity())
    ids_str = request.args.get('ids', '')
    if not ids_str:
        return jsonify({"data": []}), 200

    try:
        product_ids = [int(pid.strip()) for pid in ids_str.split(',') if pid.strip()]
    except ValueError:
        return jsonify({"data": []}), 200

    favorites = Favorite.query.filter(
        Favorite.user_id == current_user_id,
        Favorite.product_id.in_(product_ids)
    ).all()

    return jsonify({
        "data": [f.product_id for f in favorites]
    }), 200
