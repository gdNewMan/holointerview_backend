from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 외부 MySQL 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://test_user:test_user@119.67.85.26/PROJECT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# User 테이블과 매핑되는 데이터베이스 모델 정의
class User(db.Model):
    __tablename__ = 'User'  # 기존 User 테이블 이름
    userId = db.Column(db.String(12), primary_key=True)
    passwd = db.Column(db.String(128), nullable=False)
    userName = db.Column(db.String(128), nullable=False)

@app.route('/')
def home():
    return "Hello, Flask with MySQL!"


# 사용자 추가 엔드포인트
@app.route('/api/users', methods=['POST'])
def add_user():
    try:
        data = request.json
        app.logger.info(f'Received data: {data}')
        new_user = User(
            userId=data.get('userId'),
            passwd=data.get('passwd'),
            userName=data.get('userName')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User added successfully'})
    except Exception as e:
        app.logger.error(f'Error: {e}')
        return jsonify({'message': 'Failed to add user', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
