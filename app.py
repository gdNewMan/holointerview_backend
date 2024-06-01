from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPEN_API_KEY"),
    )
app = Flask(__name__)

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

questionCount = 0
_questionLimit = 7

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
    # Send BaseData to GPT
    # data will be the first question
    data = {
        "message": "hi"
    }
    return jsonify(data)


@app.route('/api/gpt', methods=['GET'])
def get_data():
    global questionCount
    if questionCount < len(sendingData):
        data = {
            "message": sendingData[questionCount]  # get GPT's answer
        }
        questionCount = questionCount + 1
    elif questionCount == len(sendingData):
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


@app.route('/api/gpt', methods=['POST'])
def chat():
    global recievedData

    if len(recievedData) == _questionLimit:  #추후 데이터를 받아올때 7을 어떻게 바꿀지
        recievedData.clear()

    recieved_texts = request.get_json()['message']
    recievedData.append(recieved_texts)
    print(recieved_texts)
    try:
        response = client.chat.completions.create(
            model = 'gpt-3.5-turbo-0125',
            messages=[
                 {"role": "system", "content": "너는 면접관이야"},
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



if __name__ == '__main__':
    app.run(debug=True)