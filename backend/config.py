# config.py
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 数据库配置
    # 格式：mysql+pymysql://用户名:密码@主机地址:端口/数据库名
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:3939@127.0.0.1:3306/campus_market?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret-campus-key' # 生产环境应使用环境变量
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1) # Token 1天后过期
    
    # 图片上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 限制最大上传大小为 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}