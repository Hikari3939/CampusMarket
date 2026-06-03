# run.py
from gevent import monkey
monkey.patch_all()

from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True)
    # 采用 socketio 启动，此时 gevent 将接管服务器运行
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
