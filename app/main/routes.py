from flask import Blueprint, request, jsonify, session, current_app as app
from ..models import db, Education, JobExperience, ProjectExp

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/submit_info', methods=['POST'])
def submit_info():
    data = request.json
    user_id = session.get('user_id')

    app.logger.info(f'Session user_id: {user_id}')
    app.logger.info(f'Received data: {data}')

    if not data.get('userId'):
        return jsonify({"message": "Unauthorized"}), 401

    new_education = Education(
        userId=user_id,
        schoolName=data.get('schoolName'),
        major=data.get('major')
    )
    db.session.add(new_education)

    new_job_experience = JobExperience(
        userId=user_id,
        companyName=data.get('companyName'),
        position=data.get('position'),
        jobDetail=data.get('jobDetail'),
        years_of_service=data.get('years_of_service')
    )
    db.session.add(new_job_experience)

    new_project_exp = ProjectExp(
        userId=user_id,
        devLanguage=data.get('devLanguage'),
        tech=data.get('tech'),
        detail=data.get('detail')
    )
    db.session.add(new_project_exp)

    db.session.commit()

    return jsonify({"message": "Information submitted successfully"}), 200

@main_bp.route('/api/users',methods = ['POST'])
def set_user():
    global questionCount
    questionCount=0
    data = {
        "message":"hi"
    }
    return jsonify(data)

@main_bp.route('/api/data', methods=['GET'])
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

@main_bp.route('/api/data', methods=['POST'])
def post_data():
    received_data = request.get_json()
    response = {
        "receivedMessage": received_data,
    }
    return jsonify(response)
