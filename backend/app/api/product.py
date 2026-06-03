# app/api/product.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Product, ProductImage

# 创建商品蓝图
product_bp = Blueprint('product', __name__)

# 合法分类集合
VALID_CATEGORIES = {'textbook', 'electronics', 'daily', 'clothing', 'sports', 'other'}

# 分类中文映射
CATEGORY_LABELS = {
    'textbook': '教材教辅', 'electronics': '电子数码', 'daily': '生活日用',
    'clothing': '服饰鞋包', 'sports': '运动户外', 'other': '其他'
}


def allowed_file(filename):
    """检查文件后缀是否合法"""
    ALLOWED_EXTENSIONS = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image_file(file):
    """保存单个图片文件，返回生成的 URL"""
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)
    return f"{request.host_url}static/uploads/{filename}"


def collect_image_files(request):
    """从请求中收集所有图片文件（支持多图 image_0..image_4 和单图 image 兼容）"""
    files = []
    # 优先按 image_0..image_4 收集
    for i in range(5):
        key = f'image_{i}'
        if key in request.files:
            f = request.files[key]
            if f and f.filename != '' and allowed_file(f.filename):
                files.append(f)
    # 兼容旧的单图字段
    if not files and 'image' in request.files:
        f = request.files['image']
        if f and f.filename != '' and allowed_file(f.filename):
            files.append(f)
    # 也支持 images 数组
    if not files and 'images' in request.files:
        file_list = request.files.getlist('images')
        for f in file_list[:5]:
            if f and f.filename != '' and allowed_file(f.filename):
                files.append(f)
    return files


def remove_old_image_file(image_url):
    """删除旧图片文件"""
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
    """
    发布商品接口 (包含图片上传)
    注意：前端须使用 FormData 发送请求，包含 title, description, price, category, image(文件)
    """
    current_user_id = int(get_jwt_identity())

    # 1. 获取表单文本数据
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '')
    price = request.form.get('price')
    category = request.form.get('category', 'other').strip()

    if not title or not price:
        return jsonify({"msg": "商品标题和价格不能为空"}), 400

    # 2. 校验分类
    if category not in VALID_CATEGORIES:
        return jsonify({"msg": "无效的商品分类"}), 400

    try:
        price_val = float(price)
        if price_val <= 0:
            return jsonify({"msg": "价格必须大于0"}), 400
    except ValueError:
        return jsonify({"msg": "价格格式不正确"}), 400

    # 3. 处理图片上传
    image_files = collect_image_files(request)

    # 4. 开启数据库事务，插入商品记录
    try:
        # 向后兼容：保留第一张图片 URL 到 products.image_url
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
        db.session.flush()  # 获取 new_product.id

        # 保存多图
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

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "服务器异常，发布失败"}), 500


@product_bp.route('', methods=['GET'])
def get_products():
    """
    获取商品列表 (支持模糊查询、分类筛选、分页)
    公开接口，无需 JWT 鉴权
    Query Params:
      keyword  - 标题模糊搜索
      category - 分类筛选 (textbook/electronics/daily/clothing/sports/other)
      page     - 页码 (默认 1)
      per_page - 每页数量 (默认 12, 最大 48)
    """
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()

    # 参数范围限制
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 1
    elif per_page > 48:
        per_page = 48

    # 基础查询：仅查询状态为 'active'（在售）的商品
    query = Product.query.filter(Product.status == 'active')

    # 如果有关键字，执行标题的模糊搜索 (LIKE %keyword%)
    if keyword:
        query = query.filter(Product.title.ilike(f'%{keyword}%'))

    # 如果指定了有效分类，添加分类过滤
    if category and category in VALID_CATEGORIES:
        query = query.filter(Product.category == category)

    # 价格区间过滤
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

    # 按最新发布时间倒序排列 + 分页
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
    """
    获取单个商品详情
    """
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"msg": "商品不存在或已被删除"}), 404

    # 如果商品已被逻辑删除，不再向普通用户展示
    if product.status == 'deleted':
        return jsonify({"msg": "该商品已下架"}), 404

    return jsonify({
        "msg": "获取成功",
        "data": product.to_dict()
    }), 200


@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """
    编辑商品接口
    仅卖家可编辑自己的商品（已下架商品不可编辑）
    支持部分字段更新 + 更换图片
    """
    current_user_id = int(get_jwt_identity())
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"msg": "商品不存在"}), 404
    if product.status == 'deleted':
        return jsonify({"msg": "已下架的商品无法编辑"}), 400
    if product.seller_id != current_user_id:
        return jsonify({"msg": "无权操作他人的商品"}), 403

    # 提取可编辑字段
    title = request.form.get('title')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')

    # 逐个更新非空字段
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

    # 处理图片更换
    image_files = collect_image_files(request)
    if image_files:
        # 删除所有旧图片（数据库记录 + 文件）
        for old_img in product.images:
            remove_old_image_file(old_img.image_url)
        # 清除旧的多图记录
        ProductImage.query.filter_by(product_id=product.id).delete()
        # 删除旧的单图文件
        if product.image_url and product.image_url not in [img.image_url for img in product.images]:
            remove_old_image_file(product.image_url)

        # 保存新图片
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
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "更新失败"}), 500


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """
    删除商品接口
    规范要求：必须校验越权，仅能删除自己的商品。采取软删除（状态机更改）
    """
    current_user_id = int(get_jwt_identity())

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"msg": "商品不存在"}), 404

    # 【核心安全校验】：防止越权删除他人商品
    if product.seller_id != current_user_id:
        return jsonify({"msg": "无权操作他人的商品"}), 403

    try:
        # 使用逻辑删除(软删除)，避免破坏 Order 订单表的关联历史
        product.status = 'deleted'
        db.session.commit()
        return jsonify({"msg": "商品删除成功"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "删除失败"}), 500
