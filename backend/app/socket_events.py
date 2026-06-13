from flask import request
from flask_socketio import emit, disconnect
from flask_jwt_extended import decode_token
from app.extensions import socketio, db
from app.models import Message

online_users = {}

@socketio.on('connect')
def handle_connect(auth):
    token = auth.get('token') if auth else None
    if not token:
        disconnect()
        return

    try:
        decoded_token = decode_token(token)
        user_id = int(decoded_token['sub'])
        online_users[user_id] = request.sid
    except Exception:
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    user_id_to_remove = None
    for user_id, sid in online_users.items():
        if sid == request.sid:
            user_id_to_remove = user_id
            break

    if user_id_to_remove:
        del online_users[user_id_to_remove]

@socketio.on('send_message')
def handle_send_message(data):
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
        new_msg = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content
        )
        db.session.add(new_msg)
        db.session.commit()

        msg_payload = {
            'id': new_msg.id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'content': content,
            'created_at': new_msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

        receiver_sid = online_users.get(receiver_id)
        if receiver_sid:
            emit('receive_message', msg_payload, room=receiver_sid)

        emit('message_sent', msg_payload)

    except Exception:
        db.session.rollback()
        emit('error', {'msg': '发送失败：服务器数据库异常'})

@socketio.on('mark_as_read')
def handle_mark_as_read(data):
    msg_id = data.get('message_id')
    if not msg_id:
        return

    try:
        msg = Message.query.get(msg_id)
        if msg and not msg.is_read:
            msg.is_read = True
            db.session.commit()
    except Exception:
        db.session.rollback()
