import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Product, ProductImage

product_bp = Blueprint('product', __name__)

VALID_CATEGORIES = {'textbook', 'electronics', 'daily', 'clothing', 'sports', 'other'}

CATEGORY_LABELS = {
    'textbook': '教材教辅', 'electronics': '电子数码', 'daily': '生活日用',
    'clothing': '服饰鞋包', 'sports': '运动户外', 'other': '其他'
}

def allowed_file(filename):
    ALLOWED_EXTENSIONS = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image_file(file):
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)
    return f"{request.host_url}static/uploads/{filename}"

def collect_image_files(request):
    files = []
    for i in range(5):
        key = f'image_{i}'
        if key in request.files:
            f = request.files[key]
            if f and f.filename != '' and allowed_file(f.filename):
                files.append(f)
    if not files and 'image' in request.files:
        f = request.files['image']
        if f and f.filename != '' and allowed_file(f.filename):
            files.append(f)
    if not files and 'images' in request.files:
        file_list = request.files.getlist('images')
        for f in file_list[:5]:
            if f and f.filename != '' and allowed_file(f.filename):
                files.append(f)
    return files

def remove_old_image_file(image_url):
    if not image_url:
        return
    old_filename = image_url.rsplit('/', 1)[-1]
    old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_filename)
    try:
        if os.path.exists(old_path):
            os.remove(old_path)
    except OSError:
        pass

@product_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    current_user_id = int(get_jwt_identity())

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '')
    price = request.form.get('price')
    category = request.form.get('category', 'other').strip()

    if not title or not price:
        return jsonify({"msg": "商品标题和价格不能为空"}), 400

    if category not in VALID_CATEGORIES:
        return jsonify({"msg": "无效的商品分类"}), 400

    try:
        price_val = float(price)
        if price_val <= 0:
            return jsonify({"msg": "价格必须大于0"}), 400
    except ValueError:
        return jsonify({"msg": "价格格式不正确"}), 400

    image_files = collect_image_files(request)

    try:
        primary_url = None
        new_product = Product(
            seller_id=current_user_id,
            title=title,
            description=description,
            category=category,
            price=price_val,
            image_url=None,
            status='active'
        )
        db.session.add(new_product)
        db.session.flush()

        for idx, img_file in enumerate(image_files):
            img_url = save_image_file(img_file)
            if idx == 0:
                primary_url = img_url
                new_product.image_url = primary_url
            db.session.add(ProductImage(
                product_id=new_product.id,
                image_url=img_url,
                sort_order=idx
            ))

        db.session.commit()
        return jsonify({
            "msg": "商品发布成功",
            "data": new_product.to_dict()
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({"msg": "服务器异常，发布失败"}), 500

@product_bp.route('', methods=['GET'])
def get_products():
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()

    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 1
    elif per_page > 48:
        per_page = 48

    query = Product.query.filter(Product.status == 'active')

    if keyword:
        query = query.filter(Product.title.ilike(f'%{keyword}%'))

    if category and category in VALID_CATEGORIES:
        query = query.filter(Product.category == category)

    if min_price:
        try:
            query = query.filter(Product.price >= float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            query = query.filter(Product.price <= float(max_price))
        except ValueError:
            pass

    paginated = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "msg": "获取成功",
        "data": [p.to_dict() for p in paginated.items],
        "pagination": {
            "total": paginated.total,
            "page": page,
            "per_page": per_page,
            "pages": paginated.pages
        }
    }), 200

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"msg": "商品不存在或已被删除"}), 404

    if product.status == 'deleted':
        return jsonify({"msg": "该商品已下架"}), 404

    return jsonify({
        "msg": "获取成功",
        "data": product.to_dict()
    }), 200

@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    current_user_id = int(get_jwt_identity())
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"msg": "商品不存在"}), 404
    if product.status == 'deleted':
        return jsonify({"msg": "已下架的商品无法编辑"}), 400
    if product.seller_id != current_user_id:
        return jsonify({"msg": "无权操作他人的商品"}), 403

    title = request.form.get('title')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')

    if title is not None:
        title = title.strip()
        if not title:
            return jsonify({"msg": "商品标题不能为空"}), 400
        product.title = title

    if description is not None:
        product.description = description

    if category is not None:
        category = category.strip()
        if category not in VALID_CATEGORIES:
            return jsonify({"msg": "无效的商品分类"}), 400
        product.category = category

    if price is not None:
        try:
            price_val = float(price)
            if price_val <= 0:
                return jsonify({"msg": "价格必须大于0"}), 400
            product.price = price_val
        except ValueError:
            return jsonify({"msg": "价格格式不正确"}), 400

    image_files = collect_image_files(request)
    if image_files:
        for old_img in product.images:
            remove_old_image_file(old_img.image_url)
        ProductImage.query.filter_by(product_id=product.id).delete()
        if product.image_url and product.image_url not in [img.image_url for img in product.images]:
            remove_old_image_file(product.image_url)

        for idx, img_file in enumerate(image_files):
            img_url = save_image_file(img_file)
            if idx == 0:
                product.image_url = img_url
            db.session.add(ProductImage(
                product_id=product.id,
                image_url=img_url,
                sort_order=idx
            ))

    try:
        db.session.commit()
        return jsonify({
            "msg": "商品更新成功",
            "data": product.to_dict()
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({"msg": "更新失败"}), 500

@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    current_user_id = int(get_jwt_identity())

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "商品不存在"}), 404

    if product.seller_id != current_user_id:
        return jsonify({"msg": "无权操作他人的商品"}), 403

    try:
        product.status = 'deleted'
        db.session.commit()
        return jsonify({"msg": "商品删除成功"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"msg": "删除失败"}), 500
