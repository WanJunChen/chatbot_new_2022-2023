import copy
from elasticsearch.helpers import bulk


def updateUser(myUserList, userId, bookName, state, partner):
    bookTalkSummary = {'Finish': state, 'Partner': partner}

    if not list(myUserList.find()):
        # 資料庫無資料 > 直接新增一筆
        mydict = {'User_id': userId, 'BookTalkSummary': {bookName: bookTalkSummary}}
        myUserList.insert_one(mydict)
    else:
        find_user = {'User_id': userId}
        now_user = myUserList.find_one(find_user)
        # 若沒有該使用者之資料
        if now_user is None:
            # 直接新增一筆
            mydict = {'User_id': userId, 'BookTalkSummary': {bookName: bookTalkSummary}}
            myUserList.insert_one(mydict)
        # 有該使用者資料
        else:
            if bookName in now_user['BookTalkSummary']:
                # 有該本書之資料 > 更新內容
                user_book_result = copy.deepcopy(now_user)
                for book_data in user_book_result['BookTalkSummary'].keys():
                    if book_data == bookName:
                        user_book_result['BookTalkSummary'][book_data] = bookTalkSummary
                myUserList.update_one(find_user, {"$set": user_book_result})
            else:
                # 同一筆資料下新增key值
                user_book_result = copy.deepcopy(now_user)
                user_book_result['BookTalkSummary'].update({bookName: bookTalkSummary})
                myUserList.update_one(find_user, {"$set": user_book_result})


def addDialog(dialogList, dialog_id, speaker_id, content, time, session_id, prompt_phase):

    mydict = {'Dialog_id': dialog_id, 'Speaker_id': speaker_id, 'Content': content, 'Phase': prompt_phase,
              'Time': time, 'Session_id': session_id}
    dialogList.insert_one(mydict)
    print(mydict)

def addQADialog(dialogList, dialog_id, speaker_id, content, time, session_id, game_mode, prompt_phase):

    mydict = {'Dialog_id': dialog_id, 'Speaker_id': speaker_id, 'Content': content, 'Game_mode': game_mode, 'Phase': prompt_phase,
              'Time': time, 'Session_id': session_id}
    dialogList.insert_one(mydict)
    print(mydict)


def addFeedback(feedbackList, userId, sentiment, feedback):

    mydict = {'User_id': userId, 'Sentiment': sentiment, 'Content': feedback}
    feedbackList.insert_one(mydict)
    print(mydict)

def update_ChatbotTrainRecord(SQuADList, bookName, user_id):

    find_user = {'User_id': user_id}
    userSQuAD_result = copy.deepcopy(SQuADList.find_one(find_user))

    if bookName not in userSQuAD_result["QA_record"].keys():
        userSQuAD_result["QA_record"][bookName] = {}
        userSQuAD_result["QA_record"][bookName]['train_count'] = 0
        userSQuAD_result["QA_record"][bookName]['test_record'] = {}

    userSQuAD_result["QA_record"][bookName]['train_count'] += 1
    SQuADList.update_one(find_user, {"$set": userSQuAD_result})

def addNew_ChatbotTestRecord(SQuADList, Challenge_id, bookName, user_id_chatbot, user_id_challenger):
    # 新增一個新的挑戰紀錄
    find_user = {'User_id': user_id_chatbot}
    userSQuAD_result = copy.deepcopy(SQuADList.find_one(find_user))
    userSQuAD_result["QA_record"][bookName]['test_record'][str(Challenge_id)] = {
                                                                        'challenger_id': user_id_challenger,
                                                                        'test_count': 0,
                                                                        'corect_count': 0}
    SQuADList.update_one(find_user, {"$set": userSQuAD_result})


def update_ChatbotTestRecord(SQuADList, Challenge_id, bookName, chatbot_id):
    find_user = {'User_id': chatbot_id}
    userSQuAD_result = copy.deepcopy(SQuADList.find_one(find_user))
    userSQuAD_result["QA_record"][bookName]['test_record'][str(Challenge_id)]['test_count'] += 1
    SQuADList.update_one(find_user, {"$set": userSQuAD_result})

def update_ChatbotCorrectRecord(SQuADList, Challenge_id, BookName, chatbot_id):
    find_user = {'User_id': chatbot_id}
    userSQuAD_result = copy.deepcopy(SQuADList.find_one(find_user))
    userSQuAD_result["QA_record"][BookName]['test_record'][str(Challenge_id)]['corect_count'] += 1
    SQuADList.update_one(find_user, {"$set": userSQuAD_result})

def update_ES_doc(es, dbBookName, user_id, chatbotName, question, suggestion_Ans, reason, page_list, question4F, time):
    question = question.replace("?", "").replace("？", "")
    mydict = {  'User_id': user_id,
                'chatbotName': chatbotName,
                'Question': question,
                'Answer': suggestion_Ans,
                'reason': reason,
                'pages': page_list,
                '4F_type': question4F,
                'time': time}
    if reason == -1:
        del mydict['reason']

    query = [
        {
            '_index': dbBookName.lower(),
            '_op_type': 'index',
            "_source": mydict
        }
    ]
    bulk(es, query)

def search_ES_doc(es, dbBookName, user_id, question):
    question = question.replace("?", "").replace("？", "")
    search_ES_data = {"bool": {"must": [
        {
            "term": {
                    "User_id.keyword": user_id
            }
        },
        {
            "match": {
                "Question": {
                    "query": question
                }
            }
        }
    ]}}
    result = es.search(index = dbBookName.lower(), query = search_ES_data)
    return result