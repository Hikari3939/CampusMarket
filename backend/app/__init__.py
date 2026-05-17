# app/__init__.py
from flask import Flask
from config import Config

import app.socket_events  # 导入该文件以激活 Socket 监听装饰器

from app.extensions import db, jwt, cors, socketio
from app.api.auth import auth_bp
from app.api.product import product_bp
from app.api.order import order_bp
from app.api.user import user_bp
from app.api.message import message_bp

def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='/static')
    
    # 加载配置
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    # 允许所有跨域请求
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app)
    
    # 注册蓝图 (路由前缀为 /api/auth)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(message_bp, url_prefix='/api/messages') 
    
    return app