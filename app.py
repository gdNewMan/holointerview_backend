from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, User, Education, JobExperience, ProjectExp
import os


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://test_user:test_user@119.67.85.26/PROJECT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)

model_name = 'ft:gpt-3.5-turbo-0125:personal::9SqEUNiZ'
api_key = os.getenv('OPENAI_API_KEY')

user_info = {}

questionCount = 0

@app.route('/api/register', methods=['POST'])
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

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('userId')
    password = data.get('passwd')

    app.logger.info(f'Received login data: userId={user_id}, passwd={password}')

    user = User.query.filter_by(userId=user_id).first()

    if user is None or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    session['user_id'] = user_id
    return jsonify({"message": "Login successful", "userID": user_id}), 200

@app.route('/api/submit_info', methods=['POST'])
def submit_info():
    data = request.json
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    # Education 추가
    new_education = Education(
        userId=user_id,
        schoolName=data.get('schoolName'),
        major=data.get('major')
    )
    db.session.add(new_education)

    # JobExperience 추가
    new_job_experience = JobExperience(
        userId=user_id,
        companyName=data.get('companyName'),
        position=data.get('position'),
        jobDetail=data.get('jobDetail'),
        years_of_service=data.get('years_of_service')
    )
    db.session.add(new_job_experience)

    # ProjectExp 추가
    new_project_exp = ProjectExp(
        userId=user_id,
        devLanguage=data.get('devLanguage'),
        tech=data.get('tech'),
        detail=data.get('detail')
    )
    db.session.add(new_project_exp)

    db.session.commit()

    return jsonify({"message": "Information submitted successfully"}), 200

questionCount = 0

@app.route('/api/users',methods = ['POST'])
def set_user():
    global questionCount
    questionCount=0
    data = {
        "message":"hi"
    }
    return jsonify(data)

@app.route('/api/data', methods=['GET'])
def get_data():
    global questionCount
    if questionCount < len(sendingData):
        data = {
            "message": sendingData[questionCount]
        }
    elif questionCount==len(sendingData):
        data = {
            "message": "수고하셨습니다"
        }
    else:
        data = {
            "message": ""
        }
    questionCount = questionCount+1
    return jsonify(data)

@app.route('/api/data', methods=['POST'])
def post_data():
    received_data = request.get_json()
    response = {
        "receivedMessage": received_data,
    }
    #send Data to GPT and server
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)