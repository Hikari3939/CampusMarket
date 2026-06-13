from flask import Flask
from config import Config

import app.socket_events

from app.extensions import db, jwt, cors, socketio
from app.api.auth import auth_bp
from app.api.product import product_bp
from app.api.order import order_bp
from app.api.user import user_bp
from app.api.message import message_bp
from app.api.favorite import favorite_bp
from app.api.review import review_bp

def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='/static')
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    socketio.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(message_bp, url_prefix='/api/messages')
    app.register_blueprint(favorite_bp, url_prefix='/api/favorites')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')

    return app
