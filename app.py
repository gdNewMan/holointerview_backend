from flask import Flask, request, jsonify

app = Flask(__name__)
sendingData = ["안녕하세요 면접에 오신 걸 환영합니다",
               "대학생활 중 어떤 일에 몰두했습니까?",
               "WAS(Web Application Server)와 WS(Web Server)의 차이를 설명해주세요.",
               "Spring Framework에 대해 설명해주세요.",
               "@RequestBody, @RequestParam, @ModelAttribute의 차이를 설명해주세요."
               ]

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