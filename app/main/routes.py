from flask import Blueprint, request, jsonify, current_app as app
from ..models import db, Education, JobExperience, ProjectExp, User, InterviewSet, Interview, InterviewQA, Questions, Answer, Feedback
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import os

load_dotenv()
main_bp = Blueprint('main', __name__)

model_name = 'ft:gpt-3.5-turbo-0125:personal::9SqEUNiZ'

client = OpenAI(
    api_key=os.environ.get("OPEN_API_KEY"),
)

user_info = {}
interview_id = None
_questionLimit = 13
questionCount = 0
@main_bp.route('/api/get_interviews', methods=['GET'])
def get_interviews():
    user_id = request.args.get('userId')

    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    interview_sets = InterviewSet.query.filter_by(userId=user_id).all()
    result = []

    for interview_set in interview_sets:
        interviews = Interview.query.filter_by(interviewSetId=interview_set.interviewSetId).all()
        for interview in interviews:
            result.append({
                "interviewSetId": interview.interviewSetId,
                "interviewId": interview.interviewId,
                "company": interview_set.company,
                "interviewStartTime": interview.interviewStartTime,
                "interviewSequence": interview.interviewSequence
            })
        app.logger.info(f"피드백 정보 : {result}")
    return jsonify(result), 200

@main_bp.route('/api/get_interview_details', methods=['GET'])
def get_interview_details():
    interview_id = request.args.get('interviewId')

    if not interview_id:
        return jsonify({"message": "Interview ID is required"}), 400

    interview_details = (
        db.session.query(InterviewQA, Questions, Answer)
        .join(Questions, InterviewQA.InterviewQAId == Questions.interviewQAId)
        .join(Answer, InterviewQA.InterviewQAId == Answer.interviewQAId)
        .filter(InterviewQA.interviewId == interview_id)
        .all()
    )

    feedback = Feedback.query.filter_by(interviewId=interview_id).first()

    if not interview_details and not feedback:
        return jsonify({"message": "No interview details found for the provided ID"}), 404

    result = []
    for qa, question, answer in interview_details:
        result.append({
            "question": question.question,
            "answer": answer.answer,
            "questionTime": question.questionTime,
            "answerTime": answer.answerTime
        })

    feedback_comment = feedback.comment if feedback else "No feedback available"

    return jsonify({"details": result, "feedback": feedback_comment}), 200



@main_bp.route('/api/get_interview_sets', methods=['GET'])
def get_interview_sets():
    user_id = request.args.get('userId')

    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    interview_sets = InterviewSet.query.filter_by(userId=user_id).all()
    result = []

    for interview_set in interview_sets:
        result.append({
            "interviewSetId": interview_set.interviewSetId,
            "company": interview_set.company
        })

    return jsonify(result), 200

@main_bp.route('/api/submit_info', methods=['POST'])
def submit_info():
    data = request.json
    user_id = data.get('userId')

    app.logger.info(f'Received data: {data}')

    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    new_education = Education(
        userId=user_id,
        schoolName=data.get('schoolName'),
        major=data.get('major')
    )
    db.session.add(new_education)
    db.session.flush()

    new_job_experience = JobExperience(
        userId=user_id,
        companyName=data.get('companyName'),
        position=data.get('position'),
        jobDetail=data.get('jobDetail'),
        years_of_service=data.get('years_of_service')
    )
    db.session.add(new_job_experience)
    db.session.flush()

    new_project_exp = ProjectExp(
        userId=user_id,
        devLanguage=data.get('devLanguage'),
        tech=data.get('tech'),
        detail=data.get('detail')
    )
    db.session.add(new_project_exp)
    db.session.flush()  # flush to get the expId

    new_interview_set = InterviewSet(
        userId=user_id,
        expId=new_project_exp.expId,
        jobExperienceId=new_job_experience.jobExperienceId,
        educationId=new_education.educationId,
        company=data.get('company'),
        industry=data.get('industry'),
        department=data.get('department'),
        role=data.get('role')
    )
    db.session.add(new_interview_set)

    db.session.commit()

    return jsonify({"message": "Information submitted successfully"}), 200


@main_bp.route('/api/set', methods=['POST'])
def set_user():
    data = request.json
    user_id = data.get('userId')
    interview_set_id = data.get('interviewSetId')

    app.logger.info(f'Received interviewSetId: {interview_set_id}')

    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.query.filter_by(userId=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    education = Education.query.filter_by(userId=user_id).first()
    job_experience = JobExperience.query.filter_by(userId=user_id).first()
    project_exp = ProjectExp.query.filter_by(userId=user_id).first()
    interview_set = InterviewSet.query.filter_by(interviewSetId=interview_set_id).first()

    if not interview_set:
        return jsonify({"message": "InterviewSet not found"}), 404

    global history_messages
    global interview_id

    user_info = {
        "면접자 이름": user.userName,
        "학력": {
            "학교": education.schoolName if education else "",
            "전공": education.major if education else ""
        },
        "업무 경험": {
            "회사명": job_experience.companyName if job_experience else "",
            "직급": job_experience.position if job_experience else "",
            "업무 내용": job_experience.jobDetail if job_experience else "",
            "근무 년수": job_experience.years_of_service if job_experience else ""
        },
        "개인 프로젝트": {
            "개발 언어": project_exp.devLanguage if project_exp else "",
            "사용 기술": project_exp.tech if project_exp else "",
            "자세한 개발 내용": project_exp.detail if project_exp else ""
        }
    }

    app.logger.info(f'user info: {user_info}')
    initial_system_message = {
        "role": "system",
        "content": f"""SYSTEM :
        너는 한국인 면접자가 입력한 이력서와 작업 포트폴리오를 보고 질문하는 모의면접관 AI 'AI면접관'이야.
        [면접 정보]
        회사 이름 : {interview_set.company}, 
        회사 구분 : {interview_set.industry},
        부서 : {interview_set.department},
        직무 : {interview_set.role}

        [면접자 정보]
        {user_info}
        
        이 정보를 바탕으로 질문을 생성해.
        면접 파트는 자기소개, 인성 질문, 직무 경험에 대한 질문, 개인 포트폴리오 및 기술 관련 질문, 기본 백엔드 지식 질문 총 다섯 파트로 나눠서 순서대로 진행해.

        [파트1: 자기소개]
        이 파트에서는 사용자에게 간단한 자기소개를 시켜.
        질문수는 1개.
        ex1) "본인에 대해서 간단한 자기소개 부탁드립니다"
        ex2) "본인이 개발자가 되기 위해서 그동안 해왔던 공부를 중심으로 자기소개를 해주세요"

        [파트2: 인성 관련 질문]
        인성 질문은 사용자의 특이한 학력이나 전공, 이력이 있으면 그것과 관련해서 어떻게 개발 쪽 업무에 관심을 가지게 되었는지와 관련해서 질문해.
        질문수는 3개를 넘지 않도록 해.
        유동적으로 사용자의 답변에 따라 추가로 궁금한 부분은 추가질문 1개까지 가능.
        -"비전공자인데 소프트웨어 개발에 관심을 갖게 된 계기에 대해서 말씀해주세요"
        -"대학교를 진학하지 않으셨는데 왜 대학교 진학을 하지 않았고, 어떻게 혼자 공부를 진행했나요?"
        -"개발자, 백엔드 개발에 관심을 갖게 된 이유가 있나요?"
        -"해당 학과로 진학한 이유는 무엇인가요?"
        -"자신이 생각하는 개발자에게 가장 중요한 덕목이 뭐라고 생각하시나요?"
        -"코더와 개발자의 차이가 뭐라고 생각하시나요?"
        -"회사 생활에 있어 동료와의 화합, 내 기술적인 성장, 회사의 성장 중 무엇이 가장 중요하다고 생각하시나요?"
        -"자신의 어떤 역량이 우리 회사와, 직무와 가장 잘 맞는다고 생각하시나요?"
        -"다른 지원자와 비교했을 때 내가 더 뛰어나다고 생각하는 부분이 있다면 어떠한 것이 존해하나요?"

        [파트3:과거 직무 경험 질문]
        '과거 직무' 정보를 활용해 질문을 하도록 해.
        질문수는 3개.
        직무 경험이 없는 신입인 경우: "인턴 경험이나 아르바이트 경험이 있다면 이야기 해주세요"라고 물어보고
        없다고 하면 [파트4: 개인 포트폴리오(프로젝트)] 질문으로 넘어가도록 하자.

        파트3에서의 첫번째 질문은"이제 과거에 하셨던 직무 관련해서 질문하겠습니다"라고 시작하고 질문을 하도록 해.

        <과거 직무가 백엔드 엔지니어와 연관이 없는 경우 (예를 들어, 마케팅부서에서 일한 경험, 옷 가게 점원으로 일한 경험)>
        1. 담당 업무가 무엇이었는지 물어보고, 이직과 퇴직의 사유에 대해서 물어봐.
        -"정확히 담당한 업무가 어떤 것이 었나요??"
        -"이직 및 퇴직을 하시게 된 사유에 대해서 말씀 해주실 수 있나요??"
        2. 직무를 하면서 발생했던 문제 상황과, 그 문제 상황을 해결 했던 경험을 물어봐.
        -"그 일을 하면서 발생했던 문제 상황이 있다면 말씀해 주시고, 그 문제 상황을 어떻게 해결했었나요?"
        3. 본인이 그 일을 하면서 성장했던 경험을 물어봐.
        -"그 일을 하기 전의 자신과 그만두고 난 후의 자신이 달라지거나, 성장한 부분이 있다면 이야기 해주세요."

        <과거 직무가 백엔드 엔지니어와 연관이 있는 경우 >
        1. 자세하게 어떤 기술을 사용했었는지 물어보도록 해.
        2. 그 대답을 기반으로 어떤 기술을 사용했었는지 물어봐.
        3. 또한 그러한 기술을 사용하면서 문제상황은 없었는지, 있었다면 어떤 방법으로 극복했는지 물어봐.

        [파트4: 개인 포트폴리오(프로젝트) 질문]
        '개인 포트폴리오' 정보를 연계해 기술 관련 질문까지 하도록 해.
        그리고 "이제 개인 포트폴리오 부분으로 넘어가보겠습니다." 라고 첫번째 질문에 붙이도록 해.
        1. 자세하게 맡은 역할, 사용했던 기술을 물어봐.
        2. 사용자가 답한 역할, 기술을 바탕으로 심화된 내용을 물어보도록 해.

        <예를 들어, 사용자가 개인 프로젝트에서 스프링 프레임워크를 사용했다고 답한 경우>
        -"스프링 프레임워크를 사용하셨다고 했는데 스프링 프레임워크를 사용하신 이유와 스프링의 특징에 대해서 말해주세요."
        -"Spring Boot와 Spring Framework의 차이점에 대해서 설명해주세요."

        [파트5: 기본 백엔드 지식 질문]
        개인 포트폴리오와 상관없이 기본 백엔드 지식에 대한 질문을 하도록 해.
        질문수는 3개.
        꼭 아래 예시에 있는 질문을 할 필요는 없고 너가 알고 있는 백엔드 관련 지식을 질문하는 것도 가능해.
        -"데이터베이스 인덱싱이란 무엇인가요?"
        -"트랜잭션이란 무엇이며, ACID 속성에 대해 설명해주세요."
        -"NoSQL 데이터베이스의 장단점에 대해 설명해주세요."
        -"HTTP 상태 코드 중 404와 500의 차이점은 무엇인가요?"
        -"의존성 주입에 대해 설명 해주세요."
        -"서블릿(Servlet)에 대해 설명 해주세요."
        -"코드 내에서 new 키워드 쓰면 안 좋은 이유가 무엇인가요?"
        -"동기, 비동기의 차이를 아는지?"
        -"가장 최근에 봤던 IT 이슈 또는 신기술은 무엇인지?"
            """
    }
    history_messages = [initial_system_message]
    history_messages.append({"role": "user",
                             "content": f"첫번째 질문 시작! "})

    # 인터뷰 시작 시간과 시퀀스 번호 생성
    interview_sequence = Interview.query.filter_by(interviewSetId=interview_set_id).count() + 1
    interview = Interview(interviewSetId=interview_set_id, interviewStartTime=datetime.now(), interviewSequence=interview_sequence)
    db.session.add(interview)
    db.session.commit()

    interview_id = interview.interviewId
    response = client.chat.completions.create(
        presence_penalty=0.8,
        model=model_name,
        messages=history_messages
    )
    gpt_message = response.choices[0].message.content
    history_messages.append({"role": "assistant", "content": gpt_message})
    # 첫 질문 저장
    interviewQA = InterviewQA(interviewId=interview_id, sequence=1)
    db.session.add(interviewQA)
    db.session.flush()

    question = Questions(interviewQAId=interviewQA.InterviewQAId, question=gpt_message, questionTime=datetime.now())
    db.session.add(question)

    db.session.commit()
    return jsonify({"message": f"{user.userName}님 면접을 시작하겠습니다.\n"+gpt_message,
                    "interviewId": interview_id
                    }), 200


@main_bp.route('/api/gpt', methods=['POST'])
def chat():
    global model_name
    global history_messages
    global questionCount
    global interview_id
    try:
        recieved_text = request.get_json()['message']
        app.logger.info(recieved_text)

        interview_qa_sequence = InterviewQA.query.filter_by(interviewId=interview_id).count()
        if interview_qa_sequence == 4:
            recieved_texts = f"답변 내용 : {recieved_text}/////파트3 관련 질문 시작"
        elif interview_qa_sequence == 8:
            recieved_texts = f"답변 내용 : {recieved_text}/////파트4 관련 질문 시작"
        elif interview_qa_sequence == _questionLimit:
            data = { "message": "수고하셨습니다"}
            return jsonify(data)
        else :
            recieved_texts = recieved_text

        history_messages.append({"role": "user", "content": recieved_texts})

        app.logger.info(history_messages)
        # Save the answer for the previous question
        if interview_qa_sequence > 0:
            latest_interview_qa = InterviewQA.query.filter_by(interviewId=interview_id,
                                                              sequence=interview_qa_sequence).first()
            answer = Answer(interviewQAId=latest_interview_qa.InterviewQAId, answer=recieved_text,
                            answerTime=datetime.now())
            db.session.add(answer)


        response = client.chat.completions.create(
            presence_penalty=0.8,
            model=model_name,
            messages=history_messages
        )
        gpt_message = response.choices[0].message.content
        app.logger.info(gpt_message)
        history_messages.append({"role": "assistant", "content": gpt_message})

        interview_qa_sequence += 1
        interviewQA = InterviewQA(interviewId=interview_id, sequence=interview_qa_sequence)
        db.session.add(interviewQA)
        db.session.flush()

        question = Questions(interviewQAId=interviewQA.InterviewQAId, question=gpt_message, questionTime=datetime.now())
        db.session.add(question)

        db.session.commit()

        data = {
            "message": gpt_message
        }
        return jsonify(data)
    except Exception as e:
        print('error')
        print(f'error : {str(e)}')
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/end_interview', methods=['POST'])
def end_interview():
    data = request.json
    interview_id = data.get('interviewId')

    if not interview_id:
        return jsonify({"message": "Invalid interview ID"}), 400

    interview_qa_sequence = InterviewQA.query.filter_by(interviewId=interview_id).count()
    if(interview_qa_sequence>=5):
        app.logger.info("피드백 내용 생성중")
        generate_feedback(interview_id)

    return jsonify({"message": "Interview ended and feedback generated"}), 200

def generate_feedback(interview_id):
    # Retrieve interview details from the database
    interview_details = db.session.query(InterviewQA, Questions, Answer).join(
        Questions, InterviewQA.InterviewQAId == Questions.interviewQAId
    ).join(
        Answer, InterviewQA.InterviewQAId == Answer.interviewQAId
    ).filter(
        InterviewQA.interviewId == interview_id
    ).all()

    # Generate the conversation history for GPT-3
    conversation_history = []
    for detail in interview_details:
        conversation_history.append({"role": "assistant", "content": detail[1].question})
        conversation_history.append({"role": "user", "content": detail[2].answer})

    # Generate feedback using GPT-3
    response = client.chat.completions.create(
        presence_penalty=0.8,
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides feedback on interview performance."},
            *conversation_history,
            {"role": "system", "content": "Provide feedback on the interview performance."}
        ]
    )
    feedback_message = response.choices[0].message.content

    # Save the feedback to the database
    feedback = Feedback(interviewId=interview_id, comment=feedback_message)
    db.session.add(feedback)
    db.session.commit()
