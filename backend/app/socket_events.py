# app/socket_events.py
from flask import request
from flask_socketio import emit, disconnect
from flask_jwt_extended import decode_token
from app.extensions import socketio, db
from app.models import Message

# 在内存中维护在线用户字典映射: { user_id : socket_session_id }
online_users = {}

@socketio.on('connect')
def handle_connect(auth):
    """
    建立 WebSocket 连接时的鉴权。
    前端需在连接时传递: const socket = io(URL, { auth: { token: "JWT..." } })
    """
    token = auth.get('token') if auth else None
    if not token:
        disconnect()
        return

    try:
        # 手动校验与解析 JWT Token
        decoded_token = decode_token(token)
        user_id = int(decoded_token['sub'])
        
        # 记录用户上线
        online_users[user_id] = request.sid
        print(f"[Socket] User {user_id} connected. SID: {request.sid}")
    except Exception as e:
        print(f"[Socket] Token 验证失败拒绝连接: {e}")
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    """断开连接时，清理在线字典"""
    user_id_to_remove = None
    for user_id, sid in online_users.items():
        if sid == request.sid:
            user_id_to_remove = user_id
            break
            
    if user_id_to_remove:
        del online_users[user_id_to_remove]
        print(f"[Socket] User {user_id_to_remove} disconnected.")

@socketio.on('send_message')
def handle_send_message(data):
    """
    处理发来的聊天消息
    预期前端推送 data: { "receiver_id": 2, "content": "商品还在吗？" }
    """
    # 1. 查找当前发信人的 User ID
    sender_id = None
    for uid, sid in online_users.items():
        if sid == request.sid:
            sender_id = uid
            break
            
    if not sender_id:
        emit('error', {'msg': '发送失败：身份丢失，请刷新重连'})
        return

    receiver_id = data.get('receiver_id')
    if receiver_id:
        receiver_id = int(receiver_id)
    content = data.get('content')

    if not receiver_id or not content:
        emit('error', {'msg': '发送失败：消息格式不完整'})
        return

    try:
        # 2. 消息持久化入库，必须使用 try-except 包裹并 rollback()
        new_msg = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content
        )
        db.session.add(new_msg)
        db.session.commit()

        # 3. 构建规范的回推数据
        msg_payload = {
            'id': new_msg.id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'content': content,
            'created_at': new_msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

        # 4. 如果接收方在线，执行实时路由定向推送 (room=SID)
        receiver_sid = online_users.get(receiver_id)
        if receiver_sid:
            emit('receive_message', msg_payload, room=receiver_sid)
            
        # 5. 向发送方回传成功确认
        emit('message_sent', msg_payload)

    except Exception as e:
        db.session.rollback()
        print(f"[Socket Error] 消息保存失败: {e}")
        emit('error', {'msg': '发送失败：服务器数据库异常'})

@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    """
    处理前端发来的实时已读回执
    消除聊天框活跃状态下的幽灵未读
    """
    msg_id = data.get('message_id')
    if not msg_id:
        return
        
    try:
        msg = Message.query.get(msg_id)
        if msg and not msg.is_read:
            msg.is_read = True
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[Socket Error] 标记已读失败: {e}")