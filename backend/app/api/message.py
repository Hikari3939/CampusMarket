from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from app.extensions import db
from app.models import Message, User

message_bp = Blueprint('message', __name__)

@message_bp.route('/history/<int:contact_id>', methods=['GET'])
@jwt_required()
def get_chat_history(contact_id):
    current_user_id = int(get_jwt_identity())

    contact = User.query.get(contact_id)
    if not contact:
        return jsonify({"msg": "联系人不存在"}), 404

    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user_id, Message.receiver_id == contact_id),
            and_(Message.sender_id == contact_id, Message.receiver_id == current_user_id)
        )
    ).order_by(Message.created_at.asc()).all()

    unread_msgs = [m for m in messages if m.receiver_id == current_user_id and not m.is_read]
    if unread_msgs:
        try:
            for m in unread_msgs:
                m.is_read = True
            db.session.commit()
        except Exception:
            db.session.rollback()

    data = []
    for msg in messages:
        data.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "receiver_id": msg.receiver_id,
            "content": msg.content,
            "is_read": msg.is_read,
            "created_at": msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({
        "msg": "获取历史记录成功",
        "data": {
            "contact": {"id": contact.id, "username": contact.username, "avatar_url": contact.avatar_url},
            "messages": data
        }
    }), 200

@message_bp.route('/contacts', methods=['GET'])
@jwt_required()
def get_contacts():
    current_user_id = get_jwt_identity()

    sent_to = db.session.query(Message.receiver_id).filter_by(sender_id=current_user_id).all()
    received_from = db.session.query(Message.sender_id).filter_by(receiver_id=current_user_id).all()

    contact_ids = set([r[0] for r in sent_to] + [r[0] for r in received_from])

    contacts_data = []
    for cid in contact_ids:
        user = User.query.get(cid)
        if not user:
            continue

        last_msg = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user_id, Message.receiver_id == cid),
                and_(Message.sender_id == cid, Message.receiver_id == current_user_id)
            )
        ).order_by(Message.created_at.desc()).first()

        unread_count = Message.query.filter_by(
            sender_id=cid, receiver_id=current_user_id, is_read=False
        ).count()

        contacts_data.append({
            "id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "last_message": last_msg.content if last_msg else "",
            "last_time": last_msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if last_msg else "",
            "unread_count": unread_count
        })

    contacts_data.sort(key=lambda x: x['last_time'], reverse=True)

    return jsonify({
        "msg": "获取联系人列表成功",
        "data": contacts_data
    }), 200
