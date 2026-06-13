import re
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

def validate_password_strength(password):
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
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({"msg": "用户名、邮箱和密码不能为空"}), 400

    if len(username) < 2 or len(username) > 50:
        return jsonify({"msg": "用户名长度应在2-50个字符之间"}), 400

    if not validate_email_format(email):
        return jsonify({"msg": "请输入有效的邮箱地址"}), 400

    is_valid, password_error = validate_password_strength(password)
    if not is_valid:
        return jsonify({"msg": password_error}), 400

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({"msg": "该邮箱或用户名已被注册"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "注册成功"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"msg": "服务器内部错误，请稍后重试"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"msg": "邮箱和密码不能为空"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "邮箱或密码错误"}), 401

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
