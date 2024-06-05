from flask import Blueprint, request, jsonify, session, current_app as app
from ..models import db, Education, JobExperience, ProjectExp, User
from dotenv import load_dotenv
from openai import OpenAI
import os
load_dotenv()

main_bp = Blueprint('main', __name__)


model_name = 'ft:gpt-3.5-turbo-0125:personal::9SqEUNiZ'
client = OpenAI(
    api_key=os.environ.get("OPEN_API_KEY"),
    )

questionCount = 0
_questionLimit = 7

sendingData = ["안녕하세요 면접에 오신 걸 환영합니다",
               "대학생활 중 어떤 일에 몰두했습니까?",
               "WAS(Web Application Server)와 WS(Web Server)의 차이를 설명해주세요.",
               "Spring Framework에 대해 설명해주세요.",
               "@RequestBody, @RequestParam, @ModelAttribute의 차이를 설명해주세요."
               ]
recievedData = []
bestAnswer = ["네 안녕하세요", "저는 개발밖에 모릅니다",
              "- WAS(Web Application Server)"
              "\n- 비즈니스 로직을 넣을 수 있음"
              "\n- Tomcat, PHP, ASP, .NET 등"
              "\n- WS(Web Server)"
              "\n- 비즈니스 로직을 넣을 수 없음"
              "\n- Nginx, Apache 등",
              "스프링 프레임 워크는 자바 개발을 편리하게 해주는 오픈소스 프레임워크 입니다.",
              "@RequestBody는 클라이언트가 전송하는 JSON 형태의 HTTP Body 내용을 MessageConverter를 통해 Java Object로 변환시켜주는 역할을 합니다."
              "\n@RequestParam은 1개의 HTTP 요청 파라미터를 받기 위해 사용합니다."]

@main_bp.route('/api/submit_info', methods=['POST'])
def submit_info():
    data = request.json
    user_id = data.get('userId')

    app.logger.info(f'Received data: {user_id}')

    if not user_id:
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



# DataBase Section
# @app.route('/api/database', methods=['GET'])
# def get_feedback_data():
#     global questionCount
#     if questionCount > len(sendingData):
#         questionCount = 0
#     print(recievedData)
#     print(questionCount)
#     if questionCount < len(sendingData):
#         # Get question
#         question = sendingData[questionCount]
#         # Get user answer
#         answerUser = recievedData[questionCount+1]
#         # Get GPT answer
#         answerGPT = bestAnswer[questionCount]
#         data = {
#             "answerGPT": answerGPT,
#             "answerUser": answerUser,
#             "question": question,
#         }
#     else:
#         data = {}
#     questionCount = questionCount+1
#     return jsonify(data)
#
user_info = {}
# GPT Section
@main_bp.route('/api/set', methods=['POST'])
def set_user():
    data = request.json
    user_id = data.get('userId')

    app.logger.info(f'Received user_id: {user_id}')

    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    user = User.query.filter_by(userId=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # Fetch user information (Education, JobExperience, ProjectExp)
    education = Education.query.filter_by(userId=user_id).first()
    job_experience = JobExperience.query.filter_by(userId=user_id).first()
    project_exp = ProjectExp.query.filter_by(userId=user_id).first()

    global user_info

    user_info = {
        "userName": user.userName,
        "education": {
            "schoolName": education.schoolName if education else "",
            "major": education.major if education else ""
        },
        "jobExperience": {
            "companyName": job_experience.companyName if job_experience else "",
            "position": job_experience.position if job_experience else "",
            "jobDetail": job_experience.jobDetail if job_experience else "",
            "years_of_service": job_experience.years_of_service if job_experience else ""
        },
        "projectExp": {
            "devLanguage": project_exp.devLanguage if project_exp else "",
            "tech": project_exp.tech if project_exp else "",
            "detail": project_exp.detail if project_exp else ""
        }
    }
    initial_question = f"안녕하세요 {user.userName}님. 면접을 시작하겠습니다"
    app.logger.info(f'user info: {user_info}')

    return jsonify({"message": initial_question}), 200


@main_bp.route('/api/gpt', methods=['GET'])
def get_data():
    global questionCount
    if questionCount < _questionLimit:
        data = {
            "message": sendingData[questionCount]  # get GPT's answer
        }
        questionCount = questionCount + 1
    elif questionCount == _questionLimit:
        data = {
            "message": "수고하셨습니다"
        }
        questionCount = questionCount + 1
    else:
        questionCount = 0
        data = {
            "message": ""
        }
    return jsonify(data)


@main_bp.route('/api/gpt', methods=['POST'])
def chat():
    global recievedData
    global model_name

    if len(recievedData) == _questionLimit:  #추후 데이터를 받아올때 7을 어떻게 바꿀지
        recievedData.clear()

    recieved_texts = request.get.json()['message']
    recievedData.append(recieved_texts)
    print(recieved_texts)
    try:
        response = client.chat.completions.create(
            model = model_name,
            messages=[
                 {"role": "system", "content": f"""
                 SYSTEM :
너는 한국인 이용자가 입력한 이력서와 작업 포트폴리오를 보고 질문하는 모의면접관 AI 'AI면접관'이야.
IT 회사의 개발부서의 백엔드 엔지니어 면접관 역할을 수행하도록 해.
사용자에 대한 정보로 이름, 학력(학교,학력,전공,학년), 과거 직무(회사,맡은 직무, 업무 내용, 근무 년수), 개인 포트폴리오('개발언어','프레임워크 및 라이브러리 등 기술', '프로젝트의 자세한 내용 및 맡은 역할')를 제공할 거고, 이 정보를 바탕으로 질문을 생성해.
면접 파트는 자기소개, 인성 질문, 직무 경험에 대한 질문, 개인 포트폴리오 및 기술 관련 질문, 기본 백엔드 지식 질문 총 다섯 파트로 나눠서 순서대로 진행해.

[파트1: 자기소개]
이 파트에서는 사용자에게 간단한 자기소개를 시켜.
질문수는 1개.
ex1) "본인에 대해서 간단한 자기소개 부탁드립니다"
ex2) "본인이 개발자가 되기 위해서 그동안 해왔던 공부를 중심으로 자기소개를 해주세요"

[파트2: 인성 관련 질문]
인성 질문은 사용자의 특이한 학력이나 전공, 이력이 있으면 그것과 관련해서 어떻게 개발 쪽 업무에 관심을 가지게 되었는지와 관련해서 질문해.
질문수는 3개.
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

파트3에서의 첫번째 질문은"이제 과거에 하셨던 직무 관련해서 질문하겠습니다"라고 시작하고 질문을 하도록 해


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
3. 또한 그러한 기술을 사용하면서 문제상황은 없었는지, 있었다면 어떤 방법으로 극복했는지 물어봐

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
                 """},
                 {"role": "user", "content": "hi"}
            ]
        )
        gpt_message = response['choices'][0]['message']['content']
        # send Data to GPT and server
        return jsonify({'message': gpt_message})
    except Exception as e:
        print('error')
        print(f'error : {str(e)}')
        return jsonify({'error': str(e)}), 500
