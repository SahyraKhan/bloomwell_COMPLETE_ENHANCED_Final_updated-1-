from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import ChatMessage, User, Notification

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/inbox')
@login_required
def inbox():
    sent_ids = {r[0] for r in db.session.query(ChatMessage.receiver_id).filter_by(sender_id=current_user.id)}
    recv_ids = {r[0] for r in db.session.query(ChatMessage.sender_id).filter_by(receiver_id=current_user.id)}
    partner_ids = sent_ids | recv_ids
    if partner_ids:
        partners = User.query.filter(User.id.in_(partner_ids)).all()
        return redirect(url_for('chat.conversation', other_id=partners[0].id))
    return render_template('chat/inbox.html', title='Messages')


@chat_bp.route('/<int:other_id>')
@login_required
def conversation(other_id):
    other = User.query.get_or_404(other_id)
    ChatMessage.query.filter_by(sender_id=other_id, receiver_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    messages = ChatMessage.query.filter(
        db.or_(
            db.and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id == other_id),
            db.and_(ChatMessage.sender_id == other_id, ChatMessage.receiver_id == current_user.id)
        )
    ).order_by(ChatMessage.created_at.asc()).all()
    sent_ids = {r[0] for r in db.session.query(ChatMessage.receiver_id).filter_by(sender_id=current_user.id)}
    recv_ids = {r[0] for r in db.session.query(ChatMessage.sender_id).filter_by(receiver_id=current_user.id)}
    partner_ids = (sent_ids | recv_ids) | {other_id}
    partners = User.query.filter(User.id.in_(partner_ids)).all()
    unread_counts = {p.id: ChatMessage.query.filter_by(sender_id=p.id, receiver_id=current_user.id, is_read=False).count() for p in partners}
    return render_template('chat/conversation.html', other=other, messages=messages,
                           partners=partners, unread_counts=unread_counts,
                           title=f'Chat – {other.full_name or other.username}')


@chat_bp.route('/<int:other_id>/send', methods=['POST'])
@login_required
def send_message(other_id):
    User.query.get_or_404(other_id)
    body = (request.form.get('message') or '').strip()
    if not body:
        return redirect(url_for('chat.conversation', other_id=other_id))
    msg = ChatMessage(sender_id=current_user.id, receiver_id=other_id, message=body)
    notif = Notification(user_id=other_id,
                         title=f'New message from {current_user.full_name or current_user.username}',
                         message=body[:100],
                         link=f'/chat/{current_user.id}',
                         notif_type='system')
    db.session.add_all([msg, notif])
    db.session.commit()
    return redirect(url_for('chat.conversation', other_id=other_id))


@chat_bp.route('/<int:other_id>/poll')
@login_required
def poll(other_id):
    since = request.args.get('since', 0, type=int)
    msgs = ChatMessage.query.filter(
        db.or_(
            db.and_(ChatMessage.sender_id == current_user.id, ChatMessage.receiver_id == other_id),
            db.and_(ChatMessage.sender_id == other_id, ChatMessage.receiver_id == current_user.id)
        ), ChatMessage.id > since
    ).order_by(ChatMessage.created_at.asc()).all()
    for m in msgs:
        if m.receiver_id == current_user.id:
            m.is_read = True
    db.session.commit()
    return jsonify([{'id': m.id, 'mine': m.sender_id == current_user.id,
                     'message': m.message, 'time': m.created_at.strftime('%H:%M')} for m in msgs])
