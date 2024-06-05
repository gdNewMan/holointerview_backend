from flask import Blueprint, request, jsonify, session, current_app as app
from ..models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    user_id = data.get('userId')
    password = data.get('passwd')
    user_name = data.get('userName')

    app.logger.info(f'Received data: userID={user_id}, password={password}, userName={user_name}')

    if not user_id or not password or not user_name:
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter_by(userId=user_id).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(userId=user_id, userName=user_name)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 200

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('userId')
    password = data.get('passwd')

    app.logger.info(f'Received login data: userId={user_id}, passwd={password}')

    user = User.query.filter_by(userId=user_id).first()

    if user is None or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    app.logger.info(f'Session set for user_id: {session.get("user_id")}')
    return jsonify({"message": "Login successful", "userId": user_id}), 200
