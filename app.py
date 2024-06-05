from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from flask_cors import CORS
from models import db, User, Education, JobExperience, ProjectExp
import os

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPEN_API_KEY"),
    )

app = Flask(__name__)
# CORS(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://test_user:test_user@119.67.85.26/PROJECT'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = os.urandom(24)

# db.init_app(app)

#Example Data
#================================================================================================
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
#================================================================================================

#History Message to send to GPT
history_messages=[
                 {"role": "system", "content": "너는 면접관이야 면접질문만 하면 돼 질문은 한번에 하나씩만 해줘 질문을 할때는 순서를 앞에 붙여줘"},
                ]
questionCount = 1
_questionLimit = 4

# DataBase Section
@app.route('/api/database', methods=['GET'])
def get_feedback_data():
    global questionCount
    if questionCount > len(sendingData):
        questionCount = 0
    print(recievedData)
    print(questionCount)
    if questionCount < len(sendingData):
        # Get question
        question = sendingData[questionCount]
        # Get user answer
        answerUser = recievedData[questionCount+1]
        # Get GPT answer
        answerGPT = bestAnswer[questionCount]
        data = {
            "answerGPT": answerGPT,
            "answerUser": answerUser,
            "question": question,
        }
    else:
        data = {}
    questionCount = questionCount+1
    return jsonify(data)


# GPT Section
@app.route('/api/set', methods=['POST'])
def set_user():
    global questionCount
    questionCount = 0
    
    #get data from database
    # Send BaseData to GPT
    # data will be the first question
    data = {
        "message": "안녕하세요 면접에 오신 걸 환영합니다"
    }
    history_messages.append({"role": "assistant", "content": data['message']})
    return jsonify(data)


# @app.route('/api/gpt', methods=['GET'])
# def get_data():
#     global questionCount
#     if questionCount < _questionLimit:
#         app.logger.info(f'chatted questionCount: {questionCount}')
#         data = {
#             "message": sendingData[questionCount]  # get GPT's answer
#         }
#         questionCount = questionCount + 1
#     elif questionCount == _questionLimit:
#         app.logger.info(f'ending questionCount: {questionCount}')
#         data = {
#             "message": "수고하셨습니다"
#         }
#         questionCount = questionCount + 1
#     else:
#         app.logger.info(f'empty questionCount: {questionCount}')
#         questionCount = 0
#         data = {
#             "message": ""
#         }
#         app.logger.info(f'before return questionCount: {questionCount}')
#     return jsonify(data)


@app.route('/api/gpt', methods=['POST'])
def chat():
    """
    Chat with GPT
    and save the conversation to the history_messages
    return: GPT's answer
    """
    # global recievedData
    global questionCount
    global history_messages
    recieved_texts = request.get_json()['message']
    # recievedData.append(recieved_texts)#Save to DataBase
    try:
        #Save user's message to history_messages to gpt remmeber conversation
        history_messages.append({"role": "user", "content": recieved_texts})
        #Send to GPT
        response = client.chat.completions.create(
            presence_penalty=0.8,
            temperature=0.6,
            model = 'gpt-3.5-turbo-0125',
            messages=history_messages
        )
        #Get GPT's answer
        gpt_message = response.choices[0].message.content
        #Save GPT's message to history_messages
        history_messages.append({"role": "assistant", "content": gpt_message})
        #추후 데이터베이스에 저장
        if questionCount < _questionLimit:
            data = {
                "message": gpt_message  # get GPT's answer
            }
            questionCount = questionCount + 1
        elif questionCount == _questionLimit:
            data = {
                "message": "수고하셨습니다"
            }
            questionCount = 0
        return jsonify(data)#return to flutter
    except Exception as e:
        print('error')
        print(f'error : {str(e)}')
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
