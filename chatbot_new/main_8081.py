from flask import Flask, render_template,request,Response, jsonify, redirect, url_for
from flask_socketio import SocketIO, rooms
from flask_cors import *
from allennlp.predictors.predictor import Predictor
from nltk.corpus import wordnet as wn
import paddlehub as hub
import nltk
import chatbot_func
import chatbot_func_2
import pymongo
import connectDB


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'sldjfalsfnwlemnw'
socketio = SocketIO(app, cors_allowed_origins="*")

# 單人聊天
@app.route('/',methods=['POST','GET'])
def index():
	return render_template('chatbot.html')

@app.route('/expression',methods=['POST','GET'])
def expression():
	return render_template('chatbot_expression_new.html')

@app.route('/QAchatbot',methods=['POST','GET'])
def QAchatbot():
	return render_template('chatbot_QA.html')

@app.route('/QAchatbot/teacherLeaderboard',methods=['POST','GET'])
def QAchatbot_teacher():
	return render_template('chatbot_QA_teacher.html')

@app.route('/QAchatbot/leaderboard_data',methods=['POST','GET'])
def leaderboard_data():
	leaderboard_data = get_leaderboard_data()
	return leaderboard_data


@app.route('/talk',methods=['POST'])
def getJson():

	req = request.get_json()
	print(req)
	response_dict = analyze_Data(req)
	# try:
	# 	if req['handler']['name'] == 'evaluate':
	# 		response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor)
	# 		print(response_dict)
	# 	elif req['handler']['name'] == 'Prompt_response':
	# 		response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor, senta)
	# 		print(response_dict)
	# 	elif req['handler']['name'] == 'expand':
	# 		response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
	# 		print(response_dict)
	# 	else:
	# 		response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
	# 		print(response_dict)
	#
	# except TypeError:
	# 	response_dict = getattr(chatbot_func_2, req['handler']['name'])()
	# 	print(response_dict)

	return jsonify(response_dict)





# 多人聊天
@app.route('/chats/<int:roomID>',methods=['POST','GET'])
def chatroom(roomID):
	return render_template('chat.html', roomID=roomID)

@app.route('/login',methods=['POST','GET'])
def login_room():
	return render_template('login.html')

@app.route('/chats/<int:roomID>?classID=<int:classID>&userID=<int:userID>',methods=['POST','GET'])
def UserData(roomID, classID, userID):
	print(classID, userID)
	return redirect(url_for('chatroom', roomID=roomID))


@socketio.on('chat_send')
def chat_send(json):
	print('chat_send: ', str(json))

	roomID = None
	if json.get('roomID', None):
		roomID = json['roomID']
		req = json['postData']
		response_dict = analyze_Data(req)
		del json['postData']
		json['response'] = response_dict
	print('chat_recv_{roomID}'.format(roomID=roomID))
	socketio.emit('chat_recv_{roomID}'.format(roomID=roomID), json)

users_data = {}
@socketio.on('join')
def on_join(json):
    global users_data
    print('join', str(json))
    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']
        username = json['username']

    if roomID in users_data:
        print(users_data)
        users_data[roomID]["count"] += 1
        users_data[roomID]["users"][username] = users_data[roomID]["count"]
        print(users_data)
    else:
        users_data[roomID] = {"count": 1, "users": {username: 1}}
        # print(users_data)


    print("online user：", users_data[roomID]["count"])
    socketio.emit('user_count_{roomID}'.format(roomID=roomID), {"count": users_data[roomID]["count"], "users": users_data[roomID]["users"]})


@socketio.on('leave')
def on_leave(json):
    global users
    print('leave', str(json))
    roomID = None
    if json.get('roomID', None):
        roomID = json['roomID']
        username = json['username']


    users_data[roomID]["count"] -= 1
    del users_data[roomID]["users"][username]

    cnt_tmp = users_data[roomID]["count"]
    for username in users_data[roomID]["users"].keys():
        users_data[roomID]["users"][username] = cnt_tmp
        cnt_tmp -= 1

    print("online user：", users_data)
    socketio.emit('user_count_{roomID}'.format(roomID=roomID), {"count": users_data[roomID]["count"], "users": users_data[roomID]["users"]})


def analyze_Data(req):
	try:
		if req['handler']['name'] == 'evaluate':
			response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor)
			print(response_dict)
		elif req['handler']['name'] == 'Prompt_response':
			response_dict = getattr(chatbot_func_2, req['handler']['name'])(req, predictor, senta)
			print(response_dict)
		elif req['handler']['name'] == 'expand' or req['handler']['name'] == 'expand_2players':
			response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
			print(response_dict)
		else:
			response_dict = getattr(chatbot_func_2, req['handler']['name'])(req)
			print(response_dict)

	except TypeError:
		response_dict = getattr(chatbot_func_2, req['handler']['name'])()
		print(response_dict)

	return response_dict

def get_leaderboard_data():
    try:
        myClient = pymongo.MongoClient("mongodb://localhost:27017/")
        myBotData = myClient.Chatbot
        myUserSQuADList = myBotData.UserSQuADTable
    except Exception as e:
        print(e)
    leaderboardContent, testRankingIndex = connectDB.find_AllUser_trainCount(myUserSQuADList)
    train_leaderboard_data = {'leaderboardContent': leaderboardContent, 'RankingIndex': testRankingIndex}
    leaderboardContent, testRankingIndex = connectDB.find_AllChatbotScore(myUserSQuADList)
    test_leaderboard_data = {'leaderboardContent': leaderboardContent, 'RankingIndex': testRankingIndex}
    data = {'train_leaderboard': train_leaderboard_data, 'test_leaderboard': test_leaderboard_data}
    return data


if __name__ == "__main__":
	wn._morphy("test", pos='v')
	nltk.download('stopwords')
	senta = hub.Module(name="senta_bilstm")
	predictor = Predictor.from_path(
		"https://storage.googleapis.com/allennlp-public-models/biaffine-dependency-parser-ptb-2020.04.06.tar.gz")
	# app.run(debug=True, port=8080)
	socketio.run(app, port=8081, debug=True)
