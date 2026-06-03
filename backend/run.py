# run.py
import os
from dotenv import load_dotenv

load_dotenv()  # 确保 run.py 同级目录的 .env 被加载

from gevent import monkey
monkey.patch_all()

from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    # 采用 socketio 启动，gevent 将接管服务器运行
    socketio.run(app, host=host, port=port, debug=debug)
