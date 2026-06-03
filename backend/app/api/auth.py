# app/api/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.models import User
from app.extensions import db

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 1. 参数校验
    if not username or not email or not password:
        return jsonify({"msg": "用户名、邮箱和密码不能为空"}), 400

    # 2. 检查用户是否已存在
    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({"msg": "该邮箱或用户名已被注册"}), 400

    # 3. 密码加密并存入数据库 (防脱库泄露)
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "注册成功"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "数据库错误", "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 1. 查找用户
    user = User.query.filter_by(email=email).first()

    # 2. 校验账号和密码
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"msg": "邮箱或密码错误"}), 401

    # 3. 签发 JWT Token (把用户 ID 作为身份载荷 payload)
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "msg": "登录成功",
        "token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200