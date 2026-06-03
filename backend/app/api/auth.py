# app/api/auth.py
import re
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.models import User
from app.extensions import db

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

def validate_password_strength(password):
    """校验密码强度，返回 (is_valid, error_message)"""
    if len(password) < 6:
        return False, "密码长度不能少于6位"
    if len(password) > 128:
        return False, "密码长度不能超过128位"
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含至少一个字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含至少一个数字"
    return True, ""

def validate_email_format(email):
    """校验邮箱基本格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # 1. 参数校验 - 非空检查
    if not username or not email or not password:
        return jsonify({"msg": "用户名、邮箱和密码不能为空"}), 400

    # 2. 用户名长度校验
    if len(username) < 2 or len(username) > 50:
        return jsonify({"msg": "用户名长度应在2-50个字符之间"}), 400

    # 3. 邮箱格式校验
    if not validate_email_format(email):
        return jsonify({"msg": "请输入有效的邮箱地址"}), 400

    # 4. 密码强度校验
    is_valid, password_error = validate_password_strength(password)
    if not is_valid:
        return jsonify({"msg": password_error}), 400

    # 5. 检查用户是否已存在
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({"msg": "该邮箱或用户名已被注册"}), 400

    # 6. 密码加密并存入数据库 (防脱库泄露)
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "注册成功"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "服务器内部错误，请稍后重试"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # 1. 参数校验
    if not email or not password:
        return jsonify({"msg": "邮箱和密码不能为空"}), 400

    # 2. 查找用户
    user = User.query.filter_by(email=email).first()

    # 3. 校验账号和密码（使用统一错误信息防止用户枚举攻击）
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "邮箱或密码错误"}), 401

    # 4. 签发 JWT Token (把用户 ID 作为身份载荷 payload)
    # Flask-JWT-Extended 4.7+ 要求 identity 为字符串
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "msg": "登录成功",
        "token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.avatar_url
        }
    }), 200