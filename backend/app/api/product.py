# app/api/product.py
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Product

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
    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            if not allowed_file(file.filename):
                return jsonify({"msg": "不支持的图片格式，仅支持 png, jpg, jpeg, gif"}), 400

            # 安全处理文件名并生成唯一UUID前缀，防止文件名冲突或路径穿越攻击
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"

            # 保存到本地配置的 static/uploads 目录
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)

            # 生成前端可访问的 URL
            image_url = f"{request.host_url}static/uploads/{filename}"

    # 4. 开启数据库事务，插入商品记录
    try:
        new_product = Product(
            seller_id=current_user_id,
            title=title,
            description=description,
            category=category,
            price=price_val,
            image_url=image_url,
            status='active'
        )
        db.session.add(new_product)
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
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            if not allowed_file(file.filename):
                return jsonify({"msg": "不支持的图片格式，仅支持 png, jpg, jpeg, gif"}), 400

            # 删除旧图片文件
            if product.image_url:
                old_filename = product.image_url.rsplit('/', 1)[-1]
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_filename)
                try:
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except OSError:
                    pass  # 旧文件删除失败不阻塞更新

            # 保存新图片
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{ext}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            product.image_url = f"{request.host_url}static/uploads/{filename}"

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
