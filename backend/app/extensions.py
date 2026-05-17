# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()

# 实例化 SocketIO，允许所有源跨域访问
socketio = SocketIO(cors_allowed_origins="*")
