from random import choice
from nltk.corpus import stopwords
from strsimpy.cosine import Cosine
from googletrans import Translator
from nltk.corpus import wordnet
from elasticsearch import Elasticsearch
import pymongo
import connectDB
import random
import pandas as pd
import Get_squadAnswer
import Get_squadBook
import config
from threading import Timer
from time import sleep

myClient: object
myBotData: object
myBookList: object
myCommonList: object
myUserList: object
Prompt_list: object
studentName_dic: object
test_count: int
correct_count: int
# Prompt_task_list = ['Time', 'Location', 'Affection', 'Life']
Prompt_task_list = ['Time']
classList = ["501", "505"]
# set chatMode to 'chatBook' or 'QA'
chatMode = 'QA'
# 每本書共有23頁(都從第2頁開始)
number_of_page = 23
# book_list = [   'Ralph the Puppy',
#                 'Birthday Presents',
#                 'My Special Friend',
#                 'Little Donkey',
#                 'Salt and Sugar']        
book_list = [   'A Journey of Love',
                "Mission I'm Possible",
                'One Two Three... Fly!',
                'Ryan the Rooster',
                "The Piano Isn't at Home"]

Question_Type = { 'Character'       :'人物',
                'Setting'           :'時間地點',
                'Action'            :'行為',
                'Feeling'           :'人物感受',
                'Causal_relations'  :'事情原因',
                'Outcome_resolution':'事情結果',
                'Prediction'        :'故事延伸'}
# 競技場的回合數
testTotalCount = 4

def check_input(req):
    print('scene: 確認說話內容')
    response = ''
    userSay = req['intent']['query']
    character = req['user']['character']
    player = req['user']['player']
    ending = ['沒有了', '沒了', '我說完了', '故事結束了', '沒有']

    if '就這樣' in userSay or userSay in ending:
        bookName = req['session']['params']['User_book']
        time = req['user']['lastSeenTime']
        player = req['user']['player']
        if player != 2:
            user_id = req['session']['params']['User_id']
        else:
            user_id = req['user']['User_id']
        session_id = req['session']['id']
        dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
        nowBook = myClient[dbBookName]
        myMaterialList = nowBook['MaterialTable']
        myDialogList = nowBook['S_R_Dialog']
        dialog_index = myDialogList.find().count()
        dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
        material_result = myMaterialList.find_one({})
        print("material_result", material_result)

        if player == 1:
            expand_scene = "expand"
        else:
            expand_scene = "expand_2players"
        if '戊班' in user_id and req['session']['params']['next_level']:
            # 獎勵機制
            user_result = myUserList.find_one({'User_id': user_id})
            user_result_updated = connectDB.copy.deepcopy(user_result)
            if 'Score' not in user_result_updated['BookTalkSummary'][bookName]:
                user_result_updated['BookTalkSummary'][bookName].update({'Score': 0})
            user_result_updated['BookTalkSummary'][bookName]['Score'] += 1
            print('update_user: ', user_result_updated)
            myUserList.update_one(user_result, {'$set': user_result_updated})
        # if character == "fish_classmate":
        #     # 判斷接下來要進哪個引導問題
        #     nowScene = req['session']['params']['NowScene']
        #     connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, nowScene)
        #     if nowScene == 'Prompt_character':
        #         # response_dict = {"scene": {
        #         #     "next": {
        #         #         'name': 'Prompt_action'
        #         #     }
        #         # }}
        #
        #         # 20210318 修改JSON格式
        #         response_dict = {
        #             "prompt": {
        #                 "firstSimple": {
        #                     "speech": [response],
        #                     "text": [response],
        #                     "delay": [2]
        #                 }
        #             },
        #             "scene": {
        #                 "next": {
        #                     "name": "Prompt_action"
        #                 }
        #             }
        #         }
        #     elif nowScene == 'Prompt_action' and 'Sentence_id' in material_result:
        #
        #         # 20210318 修改JSON格式
        #         response_dict = {
        #             "prompt": {
        #                 "firstSimple": {
        #                     "speech": [response],
        #                     "text": [response],
        #                     "delay": [len(response)/2]
        #                 }
        #             },
        #             "scene": {
        #                 "next": {
        #                     "name": "Prompt_dialog"
        #                 }
        #             }
        #         }
        #     else:
        #
        #         response_dict = {
        #             "prompt": {
        #                 "firstSimple": {
        #                     "speech": [response],
        #                     "text": [response],
        #                     "delay": [2]
        #                 }
        #             },
        #             "scene": {
        #                 "next": {
        #                     "name": "expand"
        #                 }
        #             }
        #         }
        # elif character == 'fish_teacher':
        #     response_dict = {
        #         "prompt": {
        #             "firstSimple": {
        #                 "speech": [response],
        #                 "text": [response],
        #                 "delay": [2]
        #             }
        #         },
        #         "scene": {
        #             "next": {
        #                 "name": "expand"
        #             }
        #         }
        #     }

        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [2]
                }
            },
            "scene": {
                "next": {
                    "name": expand_scene
                }
            }
        }



        if '戊班' in user_id and req['session']['params']['next_level']:
            response_dict.update({
                                    "prompt": {
                                          "firstSimple": {
                                              "speech": ["你講得很好呢！送你1顆星星。"],
                                              "text": ["你講得很好呢！送你1顆星星⭐。"],
                                              "delay": [6]

                                          },
                                          "score": 1
                                    },
                                    "session": {
                                        "params": {
                                            "next_level": False
                                        }
                                    }
                                })

    elif '我想問' in userSay and character == 'fish_teacher':
        question_count = req['session']['params']['question_count']
        question_count += 1
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [len(response) / 2]
                }
            },
            "session": {
                "params": {
                    "User_say": userSay,
                    "question_count": question_count
                }
            },
            "scene": {
                "next": {
                    "name": "Question"
                }
            }
        }

    elif '覺得' in userSay and player == 2:
        question_count = req['session']['params']['question_count']
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [len(response) / 2]
                }
            },
            "session": {
                "params": {
                    "User_say": userSay,
                    "question_count": question_count
                }
            },
            "scene": {
                "next": {
                    "name": "Feeling"
                }
            }
        }

    elif '太' in userSay or '非常' in userSay or '很' in userSay or '真' in userSay and player == 2:
        question_count = req['session']['params']['question_count']
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [len(response) / 2]
                }
            },
            "session": {
                "params": {
                    "User_say": userSay,
                    "question_count": question_count
                }
            },
            "scene": {
                "next": {
                    "name": "Assent"
                }
            }
        }

    else:
        scene = req['session']['params']['NextScene']
        if scene == "Prompt_response":
            dialog_count = req['session']['params']['dialog_count']
            sentence_id = req['session']['params']['sentence_id']
            noIdea_count = req['session']['params']['noIdea_count']
            question_count = req['session']['params']['question_count']
            User_say_len = req['session']['params']['User_say_len']
            dialog_count_limit = req['session']['params']['dialog_count_limit']

            if player == 2:
                user_dialog_count = req['session']['params']['user_dialog_count']


            # 儲存使用者說故事長度
            User_say_len.append(len(userSay))

            # 紀錄使用者不知道次數
            noIdea_content = ['不知道', '不會', '不曉得', '沒看過', '不清楚', '不明白']
            if userSay in noIdea_content:
                noIdea_count += 1

            if player != 2:
                response_dict = {
                    "prompt": {
                        "firstSimple": {
                            "speech": [response],
                            "text": [response],
                            "delay": [2]
                        }
                    },
                    "scene": {
                        "next": {
                            "name": scene
                        }
                    },
                    "session": {
                        "params": {
                            "User_say": userSay,
                            "dialog_count": dialog_count,
                            "sentence_id": sentence_id,
                            "noIdea_count": noIdea_count,
                            "question_count": question_count,
                            "User_say_len": User_say_len,
                            "dialog_count_limit": dialog_count_limit
                        }
                    }
                }
            else:
                response_dict = {
                    "prompt": {
                        "firstSimple": {
                            "speech": [response],
                            "text": [response],
                            "delay": [2]
                        }
                    },
                    "scene": {
                        "next": {
                            "name": scene
                        }
                    },
                    "session": {
                        "params": {
                            "User_say": userSay,
                            "dialog_count": dialog_count,
                            "sentence_id": sentence_id,
                            "noIdea_count": noIdea_count,
                            "question_count": question_count,
                            "User_say_len": User_say_len,
                            "user_dialog_count": user_dialog_count,
                            "dialog_count_limit": dialog_count_limit
                        }
                    }
                }

            # 戊班 獎勵機制
            response_dict['session']['params'].update({"next_level": True})

        else:
            # 20210318 修改JSON格式
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2]
                    }
                },
                "scene": {
                    "next": {
                        "name": scene
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                    }
                }
            }


    print(response)
    return response_dict


def connect():
    global myClient, myBotData, myBookList, myCommonList, myUserList, myUserSQuADList
    try:
        # myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
        myClient = pymongo.MongoClient("mongodb://localhost:27017/")
        myBotData = myClient.Chatbot
        myBookList = myBotData.bookList
        myCommonList = myBotData.commonList
        myUserList = myBotData.UserTable
        myUserSQuADList = myBotData.UserSQuADTable
    except Exception as e:
        print(e)

    return myBookList, myCommonList, myClient, myUserList, myUserSQuADList

def ESconnect():
    global es
    es = Elasticsearch("http://localhost:9200")


# 詢問班級
def user_login():
    print("scene: START_class")
    response = '哈囉！請先告訴我你的班級唷！'
    button_item = []
    for classID in classList:
        button_item.append({'title': classID})
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2],
                "expression": "happy"
            },
            'suggestions': button_item
        },
        "scene": {
            "next": {
                'name': 'input_userId'
            }
        }
    }
    # response = '魚姐姐現在正在休息唷！'
    # response_dict = {"prompt": {
    #     "firstSimple": {
    #         "speech": response,
    #         "text": response
    #     }},
    #     "scene": {
    #         "next": {
    #             'name': 'actions.scene.END_CONVERSATION'
    #         }
    #     }
    # }
    return response_dict


# 詢問座號
def input_userId(req):
    print("scene: START_id")
    userInput = req['intent']['query']
    button_item = []
    for classID in classList:
        button_item.append({'title': classID})
    # if userInput != '丁班' and userInput != '戊班' and userInput != 'Banban' and userInput != 'DingBan':
    if userInput not in classList:
        response = '要先點選班級對應的選項告訴我唷！'
        # 20210318 修改JSON格式
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [2],
                    "expression": "happy"
                },
                'suggestions': button_item
            },
            "scene": {
                "next": {
                    "name": "input_userId"
                }
            }
        }
    else:
        userClass = userInput
        response = '好唷！那你的座號是多少呢！'

        if chatMode == "chatBook":
            # 20210318 修改JSON格式
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    }
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                },
                "session": {
                    "params": {
                        "User_class": userClass,
                        "NextScene": "Get_bookName"
                    }
                }
            }
        elif chatMode == "QA":
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    }
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                },
                "session": {
                    "params": {
                        "User_class": userClass,
                        "NextScene": "SQuAD_gameMode"
                    }
                }
            }
        


    return response_dict

# 詢問進入模式
def SQuAD_gameMode(req):
    # 2022/11/14
    connect()
    ESconnect()
    print("scene: 選擇訓練場或競技場")
    userClass = req['session']['params']['User_class']
    response = '看到下面的兩個按鈕了嗎？<br>在訓練場中，你可以教自己的機器人回答各種有關故事的問題。在競技場中，你可以挑戰其他同學的機器人，考考他們的能力喔！<br>你想進入什麼模式呢？'                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
    if "User_id" in req['session']['params']:
        user_id = req['session']['params']['User_id']
    else:
        user_id = userClass + '_' + req['session']['params']['User_say'].replace('號', '')
    print('使用者：' + str(user_id))
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2],
                "expression": "happy"
            },
            "suggestions": [{'title': '訓練場'},
                            {'title': '競技場'}]
        },
        "scene": {
            "next": {
                "name": "SQuAD_Get_ChatbotStyle"
            }
        },
        "session": {
            "params": {
                "User_id": user_id,
                "User_class": userClass,
                "NextScene": "SQuAD_Get_ChatbotStyle"
            }
        }
    }

    print(response)
    return response_dict


# (訓練場)選擇機器人樣式
# (競技場)直接跳轉到Get_bookName
def SQuAD_Get_ChatbotStyle(req):
    connect()
    userClass = req['session']['params']['User_class']
    user_id = req['session']['params']['User_id']
    if 'game_mode' in req['session']['params']:
        gameMode = req['session']['params']['game_mode']
    else:
        gameMode = req['intent']['query']
    find_user = {'User_id': user_id}
    now_user = myUserSQuADList.find_one(find_user)
    response = ''
    response_dict = {}
    print(user_id, '選擇遊戲模式:', gameMode)
    if gameMode == "訓練場":
        if now_user is None:
            print("scene: 選擇機器人樣式")
            print(user_id, "無chatbot資料，開始自訂機器人")
            response = "你還沒有自己的機器人欸，在下面選擇一個你喜歡的機器人外型吧。"
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    },
                    "suggestions": [{'title': 'robot_0'},
                                    {'title': 'robot_1'},
                                    {'title': 'robot_2'},
                                    {'title': 'robot_3'},
                                    {'title': 'robot_4'},
                                    {'title': 'robot_5'}]
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                },
                "session": {
                    "params": {
                        "User_id": user_id,
                        "User_class": userClass,
                        "game_mode": gameMode,
                        "NextScene": "SQuAD_chatbotName"
                    }
                }
            }
        else:
            print(user_id, "有chatbot資料，機器人名稱為:", now_user['chatbotName'])
            chatbotName = now_user['chatbotName']
            chatbotStyle = now_user['chatbotStyle']
            response = "又見面了，我是" + chatbotName + "，歡迎來到訓練場！你準備好要開始了嗎？"
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    },
                    "suggestions": [{'title': '好'}]
                },
                "scene": {
                    "next": {
                        "name": "Get_bookName"
                    }
                },
                "session": {
                    "params": {
                        "User_id": user_id,
                        "User_class": userClass,
                        "NextScene": "Get_bookName",
                        "game_mode": gameMode,
                        "chatbotName": chatbotName,
                        "chatbotStyle": chatbotStyle
                    }
                }
            }
    elif gameMode == "競技場":
        print("scene: 跳轉到Get_bookName")
        response = "歡迎來到競技場！你可以挑戰一位機器人，問他" + str(testTotalCount) + "個問題，看看他能不能答出來喔！你今天想挑戰哪個機器人呢？"
        button_item = []
        AllUserData, testRankingIndex = connectDB.find_AllChatbotScore(myUserSQuADList)
        for i in range(len(AllUserData)):
            if AllUserData[i]['User_id'] == user_id:
                del AllUserData[i]
                break
        # 將User_id切分出班級和座號
        for i in range(len(AllUserData)):
            User_id_split = AllUserData[i]['User_id'].split("_")
            AllUserData[i]['User_id'] = User_id_split
        # AllUserData依照User_id排序
        AllUserData.sort(key = lambda AllUserData : list(map(int, AllUserData['User_id'])))
        for i in range(len(AllUserData)):
            button_item.append({'title': AllUserData[i]['chatbotName']})
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [2],
                    "expression": "happy"
                },
                'suggestions': button_item
            },
            "scene": {
                "next": {
                    "name": "Get_bookName"
                }
            },
            "session": {
                "params": {
                    "User_id": user_id,
                    "User_class": userClass,
                    "NextScene": "Get_bookName",
                    "game_mode": gameMode,
                    "allUserData": AllUserData
                }
            }
        }
    

    print(response)
    return response_dict

# 幫機器人取名
def SQuAD_chatbotName(req):
    userClass = req['session']['params']['User_class']
    user_id = req['session']['params']['User_id']
    gameMode = req['session']['params']['game_mode']
    chatbotStyle = req['session']['params']['User_say']
    response = ""
    response_dict = {}
    
    print("scene: 幫機器人取名")
    response = "哈囉~ 為了慶祝我們第一次見面，我的名字就交給你決定了，給我一個好聽的名字吧！"
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2],
                "expression": "happy"
            }
        },
        "scene": {
            "next": {
                "name": "Get_bookName"
            }
        },
        "session": {
            "params": {
                "User_id": user_id,
                "User_class": userClass,
                "NextScene": "Get_bookName",
                "game_mode": gameMode,
                "first_nameChatbot": True,
                "chatbotStyle": chatbotStyle
            }
        }
    }
    
    print(response)
    return response_dict

# 詢問書名
def Get_bookName(req):
    print("scene: 詢問書名")
    user_result = ""
    if chatMode == "chatbook":
        global studentName_dic

        response_speech = ""
        response_list = []
        response_speech_list = []
        response_len = []

        if 'User_second_check' in req['session']['params'].keys():
            second_check = req['session']['params']['User_second_check']
        else:
            second_check = False
        if second_check:
            response = ''
            user_id = req['session']['params']['User_id']
        else:
            userClass = req['session']['params']['User_class']
            if userClass == 'DingBan':
                userClass = '丁班'
            if userClass == 'Banban':
                userClass = '戊班'

            # 獲取全班姓名
            df = pd.read_excel('student.xlsx', sheet_name=userClass)
            studentName_dic = df.set_index('座號')['姓名'].to_dict()

            player = req['user']['player']
            if player != 2:
                user_id = userClass + req['session']['params']['User_say'].replace('號', '')
            else:
                user_id = req['user']['User_id']
            print('使用者：' + str(user_id))
            # 取得 myBookList, myCommonList, myClient, myUserList, myUserSQuADList
            connect()  
            response = ""
            response_dict = {}
            book_record = ''
            find_condition = {'type': 'common_start'}
            find_result = myCommonList.find_one(find_condition)
            response = choice(find_result['content'])
            response_speech = response
            response_list = [response]
            response_speech_list = [response_speech]
            response_len = [2]
            # 取得該使用者紀錄
            if list(myUserList.find()):
                user_exist = myUserList.find_one({"User_id": user_id})
                if user_exist is not None:
                    find_condition = {'type': 'common_combine'}
                    find_result = myCommonList.find_one(find_condition)
                    allBook = list(user_exist["BookTalkSummary"].keys())
                    allBook.reverse()
                    for i in range(len(allBook[0:2])):
                        if i > 0:
                            book_record += choice(find_result['content']) + allBook[i].replace("_", " ")
                        else:
                            book_record += allBook[i].replace("_", " ")
                    find_condition = {'type': 'common_registered'}
                    find_result = myCommonList.find_one(find_condition)
                    response = choice(find_result['content']).replace('X', book_record)
                    response_speech = response
                    response_list = [response]
                    response_speech_list = [response_speech]

                    if userClass == '戊班':
                        response_tmp = '這學期活動你已經累積XX顆星星⭐囉！'
                        response_tmp_2 = '這學期活動你已經累積XX顆星星囉！'
                        total_star = 0
                        user_result = myUserList.find_one({'User_id':user_id})
                        for book_key in user_result['BookTalkSummary'].keys():
                            if "Score" in user_result['BookTalkSummary'][book_key]:
                                total_star += user_result['BookTalkSummary'][book_key]['Score']
                        if total_star > 0:
                            response_tmp = response_tmp.replace('XX', str(total_star))
                            response_tmp_2 = response_tmp_2.replace('XX', str(total_star))
                            response_list = [response_tmp, response]
                            response_speech_list = [response_tmp_2, response_speech]
                            response_len = [len(response_tmp) / 2, 1]
            # 20210318 修改JSON格式
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": response_speech_list,
                        "text": response_list,
                        "delay": response_len,
                        "expression": "happy"
                    }
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                },
                "session": {
                    "params": {
                        "User_id": user_id,
                        "NextScene": "match_book",
                        "next_level": False,
                        "studentName": studentName_dic
                    }
                }
            }
    elif chatMode == "QA":
        gameMode = req['session']['params']['game_mode']
        user_id = req['session']['params']['User_id']
        userClass = req['session']['params']['User_class']
        response = ''
        response_dict = {}
        button_item = []
        userSay = req['intent']['query']
        # 詢問書名的開頭通用句
        find_condition = {'type': 'common_check_book'}
        find_result = myCommonList.find_one(find_condition)
        if gameMode == '訓練場':
            chatbotStyle = req['session']['params']['chatbotStyle']
            # 如果此名字已經有其他機器人使用，再退回SQuAD_chatbotName重新取名
            for UserChatbot in myUserSQuADList.find():
                if UserChatbot['chatbotName'] == userSay:
                    response = '這個名字已經有人用過了，麻煩你再想一個別的吧。'
                    response_dict = {
                        "prompt": {
                            "firstSimple": {
                                "speech": [response],
                                "text": [response],
                                "delay": [2],
                                "expression": "happy"
                            }
                        },
                        "scene": {
                            "next": {
                                "name": "Get_bookName"
                            }
                        },
                        "session": {
                            "params": {
                                "User_id": user_id,
                                "User_class": userClass,
                                "NextScene": "Get_bookName",
                                "game_mode": gameMode,
                                "chatbotStyle": chatbotStyle
                            }
                        }
                    }
                    return response_dict


            find_user = {'User_id': user_id}
            user_result = myUserSQuADList.find_one(find_user)
            # 若沒有該使用者之資料
            if user_result is None:
                # 直接新增一筆
                mydict = {'User_id': user_id, 'chatbotName': userSay, 'chatbotStyle': chatbotStyle, 'QA_record': {}}
                myUserSQuADList.insert_one(mydict)
                response = "從現在起，我就叫做" + userSay + "了喔。" + choice(find_result['content'])
                chatbotName = userSay
            else:
                response = choice(find_result['content'])
                chatbotName = req['session']['params']['chatbotName']
            for index in range(len(book_list)):
                response += "<br>" + str(index + 1) + ". " + book_list[index]
                button_item.append({'title': index + 1})

            leaderboardContent, testRankingIndex = connectDB.find_AllChatbotScore(myUserSQuADList)
            User_TestRecord = connectDB.find_DB_ChatbotQArecord(myUserSQuADList, user_id)
            User_TrainRecord = connectDB.search_ES_TrainContent(es, user_id)
            AllTrainCount, trainRankingIndex = connectDB.find_AllUser_trainCount(myUserSQuADList)
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    },
                    "suggestions": button_item
                },
                "scene": {
                    "next": {
                        'name': 'Prompt_SQuAD'
                    }
                },
                "session": {
                    "params": {
                        "User_id": user_id,
                        "chatbotName": chatbotName,
                        "NextScene": "Prompt_SQuAD",
                        "User_TrainRecord": User_TrainRecord,
                        "AllTrainCount": AllTrainCount,
                        "trainRankingIndex": trainRankingIndex,
                        "User_TestRecord": User_TestRecord,
                        "leaderboardContent": leaderboardContent,
                        "testRankingIndex": testRankingIndex,
                        "chatbotStyle": chatbotStyle
                    }
                }
            }
        elif gameMode == '競技場':
            # userSay是指被選擇的機器人
            chatbotName = userSay
            find_user = {'chatbotName': chatbotName}
            user_result = myUserSQuADList.find_one(find_user)
            print("現在被選中的機器人是", user_result)
            chatbotStyle = user_result['chatbotStyle']
            
            # 只提供此機器人學過的故事作為按鈕
            index = 0
            global challenge_bookList
            challenge_bookList = []
            if len(user_result['QA_record']) != 0:
                response = "嗨！我是" + chatbotName + "，以下是我有讀過的書，你可以挑一本來考我喔！"
                for key, value in user_result['QA_record'].items():
                    response += "<br>" + str(index + 1) + ". " + key
                    challenge_bookList.append(key)
                    button_item.append({'title': index + 1})
                    index += 1
            else:
                response = chatbotName + "的主人還沒有跟他分享任何故事，去挑戰其他人吧。"
                response_dict = {
                    "prompt": {
                        "firstSimple": {
                            "speech": [response],
                            "text": [response],
                            "delay": [2],
                            "expression": "happy"
                        },
                        "suggestions": [{'title':"返回"}]
                    },
                    "scene": {
                        "next": {
                            'name': 'SQuAD_Get_ChatbotStyle'
                        }
                    },
                    "session": {
                        "params": {
                            "User_id": user_id,
                            "User_class": userClass,
                            "game_mode": gameMode,
                            "NextScene": "SQuAD_Get_ChatbotStyle"
                        }
                    }
                }
                
                return response_dict

            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    },
                    "suggestions": button_item
                },
                "scene": {
                    "next": {
                        'name': 'Prompt_SQuAD'
                    }
                },
                "session": {
                    "params": {
                        "User_id": user_id,
                        "chatbotName": chatbotName,
                        "NextScene": "Prompt_SQuAD",
                        "chatbotStyle": chatbotStyle
                    }
                }
            }
        
        

    print(response)
    return response_dict

# 根據相似度比對結果顯示書名選項給使用者直接點選
def match_book(req):
    print('scene: 比對書名')
    global Prompt_list
    userSay = req['session']['params']['User_say']
    session_id = req['session']['id']
    character = req['user']['character']
    player = req['user']['player']
    connect()
    if 'User_first_match' in req['session']['params'].keys():
        first_match = req['session']['params']['User_first_match']
    else:
        first_match = True
    # 抓出所有書名
    bookDB = []
    for i in myBookList.find():
        bookDB.append(i['bookName'])
        bookDB.append(i['bookNameTranslated'])
    # print(bookDB)
    if first_match:
        # 第一次先找出相似書名給使用者確認
        similarity_book = {}
        for index in range(len(bookDB)):
            cosine = Cosine(2)
            s1 = userSay.lower()
            s2 = bookDB[index].lower()
            p1 = cosine.get_profile(s1)
            p2 = cosine.get_profile(s2)
            if p1 == {}:
                # 避免輸入字串太短
                break
            else:
                print(s2 + '，相似度：' + str(cosine.similarity_profiles(p1, p2)))
                value = cosine.similarity_profiles(p1, p2)
                if value >= 0.45:
                    if index == 0:
                        similarity_book[bookDB[index]] = value
                    else:
                        if index % 2 == 0:
                            similarity_book[bookDB[index]] = value
                        else:
                            similarity_book[bookDB[index - 1]] = value
        sort_similarity_book = sorted(similarity_book.items(), key=lambda x: x[1], reverse=True)
        print(sort_similarity_book)
        if len(sort_similarity_book) == 0:
            second_check = True
            first_match = True
            # 無相似書籍 重新輸入
            find_common = {'type': 'common_book_F'}
            find_common_result = myCommonList.find_one(find_common)
            response = choice(find_common_result['content'])


            # 20210318 修改JSON格式
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expression": "frightened"

                    }
                },
                "session": {
                    "params": {
                        "User_first_match": first_match,
                        "User_second_check": second_check
                    }
                },
                "scene": {
                    "next": {
                        "name": "Get_bookName"
                    }
                }
            }
        else:
            first_match = False
            button_item = []
            temp_bookList = {}
            allBook = ''
            for index in range(len(sort_similarity_book[0:5])):
                temp_bookList[str(index + 1)] = sort_similarity_book[index][0]
                button_item.append({'title': str(index + 1)})
                if index == 0:
                    allBook += str(index + 1) + '：' + sort_similarity_book[index][0]
                else:
                    allBook += "、" + str(index + 1) + '：' + sort_similarity_book[index][0]
            button_item.append({'title': '都不是'})
            response = '我有看過 ' + allBook + " 你是在指哪一本呢? 告訴我書名對應的號碼吧"


            # 20210318 修改JSON格式
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expressionP": 2,
                        "expressionA": 1
                    },
                    "suggestions": button_item
                },
                "session": {
                    "params": {
                        "User_first_match": first_match,
                        "User_temp_bookList": temp_bookList
                    }
                }
            }
    else:
        userInput = req['intent']['query']
        temp_bookList = req['session']['params']['User_temp_bookList']
        # 依照使用者按下的按鈕(userInput)來配對書名
        if userInput in temp_bookList.keys():
            time = req['user']['lastSeenTime']
            user_id = req['session']['params']['User_id']
            bookName = temp_bookList[userInput]
            dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
            nowBook = myClient[dbBookName]

            myDialogList = nowBook['S_R_Dialog']
            
            book_finish = False

            dialog_index = myDialogList.find().count()
            if dialog_index == 0:
                dialog_id = 0
            else:
                dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
            find_common = {'type': 'common_book_T'}
            find_common_result = myCommonList.find_one(find_common)
            response = choice(find_common_result['content'])

            # 取得書本紀錄
            if list(myUserList.find()):
                user_data_load = myUserList.find_one({"User_id": user_id})
                # 確認有該本書
                if user_data_load is not None and bookName in user_data_load["BookTalkSummary"].keys():
                    # 書本狀態紀錄為已完成
                    if user_data_load["BookTalkSummary"][bookName]["Finish"]:
                        if chatMode == 'chatBook':
                            find_condition = {'type': 'common_finished_T'}
                            find_result = myCommonList.find_one(find_condition)
                            response = choice(find_result['content'])
                        book_finish = True

            # 記錄對話過程
            connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
            
            if book_finish:
                first_match = True
                second_check = True

                # 20210318 修改JSON格式
                response_dict = {
                    "prompt": {
                        "firstSimple": {
                            "speech": [response],
                            "text": [response],
                            "delay": [2],
                            "expressionP": 1,
                            "expressionA": 1
                        },
                        "suggestions": button_item
                    },
                    "session": {
                        "params": {
                            "User_first_match": first_match,
                            "User_second_check": second_check
                        }
                    },
                    "scene": {
                        "next": {
                            'name': 'Get_bookName'
                        }
                    }
                }
            elif chatMode == 'chatBook':
                # 比對到且沒有讀完 開始聊書
                state = False
                # 建立使用者資料
                player = req['user']['player']
                if player != 2:
                    user_id = req['session']['params']['User_id']
                    connectDB.updateUser(myUserList, user_id, bookName, state, "None")
                else:
                    user_id = req['user']['User_id']
                    partner = req['user']['partner']
                    userClass = req['session']['params']['User_class']
                    partner = userClass + partner
                    connectDB.updateUser(myUserList, user_id, bookName, state, partner)
                    connectDB.updateUser(myUserList, partner, bookName, state, user_id)


                dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
                nowBook = myClient[dbBookName]
                myMaterialList = nowBook['MaterialTable']
                material_result = myMaterialList.find_one({})

                if 'Sentence_id' in material_result:
                    if player == 1:
                        Prompt_list = ['Prompt_character', 'Prompt_action', 'Prompt_dialog', 'Prompt_event']
                    else:
                        # Prompt_list = ['Prompt_beginning', 'Prompt_character_sentiment',  'Prompt_action_sentiment']
                        # Prompt_list = ['Prompt_character', 'Prompt_character_sentiment', 'Prompt_character_experience', 'Prompt_vocabulary', 'Prompt_action_reason', 'Prompt_action_experience']
                        Prompt_list = ['Prompt_character']
                else:
                    if player == 1:
                        Prompt_list = ['Prompt_character', 'Prompt_action', 'Prompt_event']
                    else:
                        # Prompt_list = ['Prompt_character', 'Prompt_character_sentiment', 'Prompt_character_experience', 'Prompt_vocabulary', 'Prompt_action_reason', 'Prompt_action_experience']
                        Prompt_list = ['Prompt_character']
                if player == 1:
                    random.shuffle(Prompt_list)

                    # 20210318 修改JSON格式
                    response_dict = {
                        "prompt": {
                            "firstSimple": {
                                "speech": [response],
                                "text": [response],
                                "delay": [2],
                                "expressionP": 1,
                                "expressionA": 1
                            }
                        },
                        "session": {
                            "params": {
                                "User_book": bookName,
                                "dialog_count": 0,
                                "sentence_id": [],
                                "noIdea_count": 0,
                                "question_count": 0,
                                "User_say_len": [],
                                "dialog_count_limit": 3
                            }
                        },
                        "scene": {
                            "next": {
                                'name': Prompt_list[0]
                            }
                        }
                    }
                else:
                    response_dict = {
                        "prompt": {
                            "firstSimple": {
                                "speech": [response],
                                "text": [response],
                                "delay": [2],
                                "expression": "happy"
                            }
                        },
                        "session": {
                            "params": {
                                "User_book": bookName,
                                "dialog_count": 0,
                                "sentence_id": [],
                                "noIdea_count": 0,
                                "question_count": 0,
                                "User_say_len": [],
                                "user_dialog_count": {},
                                "dialog_count_limit": 5
                            }
                        },
                        "scene": {
                            "next": {
                                'name': Prompt_list[0]
                            }
                        }
                    }

                Prompt_list.pop(0)
        else:
            first_match = True
            second_check = True
            # 重新輸入
            response = '再跟我說一次書名吧！'

            # 20210318 修改JSON格式
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expressionP": -1,
                        "expressionA": -1
                    }
                },
                "session": {
                    "params": {
                        "User_first_match": first_match,
                        "User_second_check": second_check
                    }
                },
                "scene": {
                    "next": {
                        'name': 'Get_bookName'
                    }
                }
            }

    print(response)
    return response_dict

def get_thinkingWord():
    # 思考中的通用句
    find_common = {'type': 'common_thinking'}
    find_common_result = myCommonList.find_one(find_common)
    result = choice(find_common_result['content'])
    return result

# 引導使用者向機器人問問題
def Prompt_SQuAD(req):
    print('scene: 引導SQuAD問答')
    global challenge_bookList
    user_id = req['session']['params']['User_id']
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    userInput = req['intent']['query']
    chatbotName = req['session']['params']['chatbotName']
    gameMode = req['session']['params']['game_mode']
    thinking_word = get_thinkingWord()
    find_common = {'type': 'common_accept_question'}
    accept_question_result = myCommonList.find_one(find_common)
    find_common = {'type': 'common_book_T'}
    common_book_T_result = myCommonList.find_one(find_common)
    response = ""
    if gameMode == "訓練場":
        response += choice(common_book_T_result['content'])
        bookName = book_list[int(userInput)-1]
    elif gameMode == "競技場":
        bookName = challenge_bookList[int(userInput)-1]
    response += "看到右邊的書本內容了嗎，滑動看看吧。<br>" + choice(accept_question_result['content'])+"<br>(請在下方輸入你的問題)"
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['QA_Dialog']
    # 記錄對話過程
    dialog_index = myDialogList.find().count()
    if dialog_index == 0:
        dialog_id = 0
    else:
        dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addQADialog(myDialogList, dialog_id, 'chatbot', chatbotName, response, time, session_id, gameMode, req['scene']['name'])
    
    if gameMode == "訓練場":
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [2],
                    "expression": "happy"
                }
            },
            "scene": {
                "next": {
                    "name": "SQuAD_get_Type"
                }
            },
            "session": {
                "params": {
                    "User_book": bookName,
                    "NowScene": "Prompt_SQuAD",
                    "thinking_word": thinking_word,
                    "NextScene": "SQuAD_get_Type",
                    "game_mode": gameMode
                }
            }
        }
    elif gameMode == "競技場":
        # 建立一筆新的挑戰資料
        find_user = {'chatbotName': chatbotName}
        now_user = myUserSQuADList.find_one(find_user)
        Challenge_id = len(now_user["QA_record"][bookName]['test_record'])
        connectDB.addNew_ChatbotTestRecord(myUserSQuADList, Challenge_id, bookName, now_user['User_id'], user_id)
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [2],
                    "expression": "happy"
                }
            },
            "scene": {
                "next": {
                    "name": "SQuAD_get_Ans"
                }
            },
            "session": {
                "params": {
                    "User_book": bookName,
                    "NowScene": "Prompt_SQuAD",
                    "thinking_word": thinking_word,
                    "NextScene": "SQuAD_get_Ans",
                    "Challenge_id": Challenge_id,
                    "game_mode": gameMode
                }
            }
        }

    print(response)
    return response_dict

def SQuAD_get_Type(req):
    print('scene:  (SQuAD)詢問Type的問句類型')
    session_id = req['session']['id']
    user_id = req['session']['params']['User_id']
    time = req['user']['lastSeenTime']
    UserQuestion = req['intent']['query']
    gameMode = req['session']['params']['game_mode']
    chatbotName = req['session']['params']['chatbotName']
    bookName = req['session']['params']['User_book']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['QA_Dialog']
    response = '你的這個問題「XXX」是哪一類的問題呢？'
    response = response.replace('XXX', UserQuestion)
    button_item = []
    for key, value in Question_Type.items():
        button_item.append({'title': value})

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1

    # 記錄對話過程
    if len(UserQuestion) > 0:
        connectDB.addQADialog(myDialogList, dialog_id, 'Student', user_id, UserQuestion, time, session_id, gameMode, req['scene']['name'])
        connectDB.addQADialog(myDialogList, dialog_id + 1, 'chatbot', chatbotName, response, time, session_id, gameMode, req['scene']['name'])
        NextScene = "SQuAD_get_Ans"
    else:
        response = "請輸入你的問題"
        button_item = []
        NextScene = "SQuAD_get_Type"

    thinking_word = get_thinkingWord()
    response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [2],
                    "expression": "happy"
                },
                "suggestions": button_item
            },
            "scene": {
                "next": {
                    "name": NextScene
                }
            },
            "session": {
                "params": {
                    "User_book": bookName,
                    "NowScene": "SQuAD_get_Type",
                    "NextScene": NextScene,
                    "User_question": UserQuestion,
                    "thinking_word": thinking_word
                }
            }
        }
    print(response)
    return response_dict

def SQuAD_get_Ans(req):
    print('scene: (SQuAD)生成答案')
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    user_id = req['session']['params']['User_id']
    userInput = req['intent']['query']
    chatbotName = req['session']['params']['chatbotName']
    gameMode = req['session']['params']['game_mode']
    response = ""
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['QA_Dialog']
    button_item = []
    User_questionType = ''
    if gameMode == "訓練場":
        UserQuestion = req['session']['params']['User_question']
        for key, value in Question_Type.items():
            if userInput == value:
                User_questionType = key
        find_user = {'User_id': user_id}
        now_user = myUserSQuADList.find_one(find_user)
    elif gameMode == "競技場":
        UserQuestion = userInput
        Challenge_id = req['session']['params']['Challenge_id']
        find_user = {'chatbotName': chatbotName}
        now_user = myUserSQuADList.find_one(find_user)

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addQADialog(myDialogList, dialog_id, 'Student', user_id, userInput, time, session_id, gameMode, req['scene']['name'])
    
    
    # 「回答」的通用句
    thinking_word = get_thinkingWord()
    # 若SQuAD機器人知道答案的通用句
    find_common = {'type': 'common_answer_T'}
    find_common_result_answerT = myCommonList.find_one(find_common)
    # 若SQuAD機器人不知道答案的通用句
    find_common = {'type': 'common_answer_F'}
    find_common_result_answerF = myCommonList.find_one(find_common)
    # 徵求答案的通用句
    find_common = {'type': 'common_ask_for_answer'}
    find_common_result_askAnswer = myCommonList.find_one(find_common)

    Exist_Ans = False 
    Ans = ''
    answerFrom = None
    ask_for_Ans = False
    backToMainMenu = False
    # 從ElasticSearch知識庫中找紀錄
    if bookName in now_user["QA_record"].keys():
        ESBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
        result = connectDB.search_ES_doc(es, ESBookName, now_user['User_id'], UserQuestion)
        # 若UserQuestion有匹配到相似問句
        if len(result["hits"]["hits"]) != 0:
            print("ES中匹配到的紀錄:", result["hits"]["hits"])
            print("max_score:", result["hits"]['max_score'])
            if result["hits"]['max_score'] >= 2:
                # ES中找到合適的答案
                Ans = result["hits"]["hits"][0]["_source"]['Answer']
                answerFrom = 'ES'
                Exist_Ans = True
                if len(Ans) == 0:
                    Exist_Ans = False
    if Exist_Ans == False:
        print("ES中沒有適合的答案，執行SQuAD")
        # 將書名資料傳送給機器人伺服器
        try:
            Check = Get_squadBook.get_squadBook(dbBookName, False)
            print("機器人伺服器連線狀態 :", Check)
            if Check:
                Ans = Get_squadAnswer.get_squadAnswer(UserQuestion, False)
                if Ans == "NO_ANS":
                    # SQuAD沒有生成出答案
                    answerFrom = 'SQuAD'
                    Exist_Ans = False
                    Ans = None
                else:
                    # SQuAD有生成出答案
                    answerFrom = 'SQuAD'
                    Exist_Ans = True
        except ValueError:
            response = "不好意思喔...我不太舒服，你可以暫停一下，順便幫我告訴教室裡的大姊姊嗎？"
            

    if gameMode == "訓練場":
        # 訓練場會徵求答案
        if Exist_Ans == True:
            response = choice(find_common_result_answerT['content']).replace('XXX', Ans) + "<br>(請按下正確/錯誤的按鈕)"
            ask_for_Ans = False
            button_item = [ {'title': '正確'},
                            {'title': '錯誤'}]
            nextScene = "SQuAD_chatbot_Reply"
        elif len(answerFrom) != 0:
            response = choice(find_common_result_answerF['content']) + "，" + choice(find_common_result_askAnswer['content']) + "如果不知道就按下「不知道」"
            ask_for_Ans = True
            button_item = [{'title': '不知道'}]
            nextScene = "SQuAD_chatbot_Reply"
            
    elif gameMode == "競技場":
        backToMainMenu = False
        # 競技場不會徵求答案
        ask_for_Ans = False
        if Exist_Ans == True:
            response += choice(find_common_result_answerT['content']).replace('XXX', Ans)
            button_item = [ {'title': '正確'},
                            {'title': '錯誤'}]
            nextScene = "SQuAD_chatbot_Reply"
        else:
            test_count = len(now_user['QA_record'][bookName]['test_record'][str(Challenge_id)]['content'])

            correct_count = 0
            for i in range(test_count):
                if now_user['QA_record'][bookName]['test_record'][str(Challenge_id)]['content'][i]['result'] == True:
                    correct_count += 1

            print("test_count:", test_count, " correct_count:", correct_count)
            answerFrom = None
            if test_count < testTotalCount-1:
                response += choice(find_common_result_answerF['content']) + "，真可惜。<br>你可以繼續問我第" + str(test_count+2) + "題囉！"
                nextScene = "SQuAD_get_Ans"
            else:
                response += choice(find_common_result_answerF['content']) + "，真可惜。<br>好的，你已經問" + str(test_count+1) + "題了喔，"
                response += chatbotName +"答對了" + str(correct_count) + "題，答對率是" + str(int(correct_count/(test_count+1) * 100)) +"%。"
                response += "<br>回主選單繼續玩吧~"
                button_item = [{'title': '主選單'}]
                nextScene = "SQuAD_gameMode"
                backToMainMenu = True
            # 更新測驗紀錄
            connectDB.update_ChatbotTestRecord_content(myUserSQuADList, Challenge_id, bookName, now_user['User_id'], UserQuestion, None, answerFrom, False)
            
    # 記錄對話過程
    connectDB.addQADialog(myDialogList, dialog_id + 1, 'chatbot', chatbotName, req['session']['params']['thinking_word'] + '...' + response, time, session_id, gameMode, req['scene']['name'])
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            },
            "suggestions": button_item
        },
        "scene": {
            "next": {
                'name': nextScene
            }
        },
        "session": {
            "params": {
                "User_id": user_id,
                "User_questionType": User_questionType,
                "User_book": bookName,
                "ask_for_Ans": ask_for_Ans,
                "system_Ans": Ans,
                "User_question": UserQuestion,
                "thinking_word": thinking_word,
                "answerFrom": answerFrom,
                "NextScene": nextScene,
                "backToMainMenu": backToMainMenu
            }
        },
    }
    if gameMode == "競技場":
        response_dict['session']['params']['Challenge_id'] = Challenge_id
    return response_dict

def SQuAD_chatbot_Reply(req):
    print("使用者已按下正確/錯誤的按鈕 或 使用者已提出建議解答")
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    user_id = req['session']['params']['User_id']
    userSay = req['intent']['query']
    UserQuestion = req['session']['params']['User_question']
    system_Ans = req['session']['params']['system_Ans']
    chatbotName = req['session']['params']['chatbotName']
    gameMode = req['session']['params']['game_mode']
    UserQuestionType = req['session']['params']['User_questionType']
    bookName = req['session']['params']['User_book']
    answerFrom = req['session']['params']['answerFrom']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    response = ""
    nextScene = ""
    answer_result = False
    updateChatbotFile = False
    ask_for_Ans = False
    thinking_word = get_thinkingWord()
    backToMainMenu = False
    User_TrainRecord = ''
    trainDataList = nowBook['Train_Data']

    button_item = []
    # 當學生提出問句的建議解答後
    if req['session']['params']['ask_for_Ans'] == True:
        if userSay == "不知道":
            response = "好吧，那你就繼續問我其他問題吧！"
            nextScene = "SQuAD_get_Type"
            ask_for_Ans = False
            # 記錄訓練資料
            
            connectDB.add_DB_TrainData(trainDataList, user_id, UserQuestion, UserQuestionType, system_Ans, answerFrom, '錯誤', None, None, None, time)

        else:
            if len(userSay) != 0:
                response = "那你可以告訴我為什麼嗎？告訴我原因吧，如果不知道就按下「不知道」。"
                nextScene = "SQuAD_get_Reason"
                ask_for_Ans = False
            else:
                response = "請輸入你的答案"
                ask_for_Ans = True
                nextScene = "SQuAD_chatbot_Reply"
            button_item = [{'title': '不知道'}]
        print("學生問題:", UserQuestion, "學生建議答案:", userSay)
        
    # 機器人回答學生的問句，然後學生按下正確/錯誤鍵後
    else:
        # 若SQuAD機器人不知道答案的通用句
        find_common = {'type': 'common_answer_F'}
        find_common_result_answerF = myCommonList.find_one(find_common)
        if gameMode == "訓練場":
            if userSay == "正確":
                answer_result = True
                response = "太好了，你可以繼續問我問題囉！"
                updateChatbotFile = True
                ask_for_Ans = False
                # 將DB中該本書的訓練次數加一
                connectDB.update_ChatbotTrainRecord(myUserSQuADList, bookName, user_id)
                # 將問句、建議答案、頁數及原因存入ElasticSearch
                connectDB.update_ES_doc(es, dbBookName, user_id, chatbotName, UserQuestion, system_Ans, None, None, UserQuestionType, time)
                
                # 記錄訓練資料
                connectDB.add_DB_TrainData(trainDataList, user_id, UserQuestion, UserQuestionType, system_Ans, answerFrom, '正確', None, None, None, time)

                nextScene = "SQuAD_get_Type"
            elif userSay == "錯誤":
                answer_result = False
                response = choice(find_common_result_answerF['content']) + "，那你可以教教我正確答案是什麼嗎？"
                ask_for_Ans = True
                button_item = [{'title': '不知道'}]
                nextScene = "SQuAD_chatbot_Reply"
        elif gameMode == "競技場":
            Challenge_id = req['session']['params']['Challenge_id']
            find_user = {'chatbotName': chatbotName}
            now_user = myUserSQuADList.find_one(find_user)
            test_count = len(now_user['QA_record'][bookName]['test_record'][str(Challenge_id)]['content'])

            correct_count = 0
            for i in range(test_count):
                if now_user['QA_record'][bookName]['test_record'][str(Challenge_id)]['content'][i]['result'] == True:
                    correct_count += 1

            backToMainMenu = False
            print("test_count:", test_count, " correct_count:", correct_count)
            if userSay == "正確":
                answer_result = True
                response += "太好了。"
                correct_count += 1
            elif userSay == "錯誤":
                answer_result = False
                response += choice(find_common_result_answerF['content']) + "，真可惜。"

            if test_count < testTotalCount-1:
                response += "<br>你可以繼續問我第" + str(test_count+2) + "題囉！"
                nextScene = "SQuAD_get_Ans"
            else:
                response += "<br>好的，你已經問" + str(test_count+1) + "題了喔，"
                response += chatbotName +"答對了" + str(correct_count) + "題，答對率是" + str(int(correct_count/(test_count+1) * 100)) +"%。"
                response += "<br>回主選單繼續玩吧~"
                button_item = [{'title': '主選單'}]
                nextScene = "SQuAD_gameMode"
                backToMainMenu = True
            ask_for_Ans = False

            # 更新測驗紀錄
            connectDB.update_ChatbotTestRecord_content(myUserSQuADList, Challenge_id, bookName, now_user['User_id'], UserQuestion, system_Ans, answerFrom, answer_result)
    
    # 記錄對話
    myDialogList = nowBook['QA_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addQADialog(myDialogList, dialog_id, 'Student', user_id, userSay, time, session_id, gameMode, req['scene']['name'])
    connectDB.addQADialog(myDialogList, dialog_id + 1, 'chatbot', chatbotName, response, time, session_id, gameMode, req['scene']['name'])
    
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            },
            "suggestions": button_item
        },
        "scene": {
            "next": {
                'name': nextScene
            }
        },
        "session": {
            "params": {
                "User_id": user_id,
                "User_question": UserQuestion,
                "User_ans": userSay,
                "User_book": bookName,
                "system_Ans": system_Ans,
                "answerFrom": answerFrom,
                "ask_for_Ans": ask_for_Ans,
                "thinking_word": thinking_word,
                "NextScene": nextScene,
                "backToMainMenu": backToMainMenu
            }
        },
    }
    if updateChatbotFile == True:
        sleep(1)
        User_TrainRecord = connectDB.search_ES_TrainContent(es, user_id)
        AllTrainCount, trainRankingIndex = connectDB.find_AllUser_trainCount(myUserSQuADList)
        response_dict['session']['params']['User_TrainRecord'] = User_TrainRecord
        response_dict['session']['params']['AllTrainCount'] = AllTrainCount
        response_dict['session']['params']['trainRankingIndex'] = trainRankingIndex
    if gameMode == "競技場":
        response_dict['session']['params']['Challenge_id'] = Challenge_id
    print(response)
    return response_dict

# 詢問使用者此答案的原因
def SQuAD_get_Reason(req):
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    gameMode = req['session']['params']['game_mode']
    user_id = req['session']['params']['User_id']
    userSay = req['intent']['query']
    UserQuestion = req['session']['params']['User_question']
    UserAns = req['session']['params']['User_ans']
    chatbotName = req['session']['params']['chatbotName']
    system_Ans = req['session']['params']['system_Ans']
    bookName = req['session']['params']['User_book']
    answerFrom = req['session']['params']['answerFrom']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    
    find_common = {'type': 'common_elaboration'}
    find_common_result = myCommonList.find_one(find_common)
    response = choice(find_common_result['content']) + "這部分在故事的哪幾頁呢？點選頁數後按下傳送就好了喔"

    # 記錄對話
    myDialogList = nowBook['QA_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addQADialog(myDialogList, dialog_id, 'Student', user_id, userSay, time, session_id, gameMode, req['scene']['name'])
    connectDB.addQADialog(myDialogList, dialog_id + 1, 'chatbot', chatbotName, response, time, session_id, gameMode, req['scene']['name'])
    
    if userSay == "不知道":
        userSay = None
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            },
            "suggestions": [{'title': '沒有'}]

        },
        "params": {
            "NextScene": "SQuAD_get_Page"
        },
        "scene": {
            "next": {
                'name': "SQuAD_get_Page"
            }
        },
        "session": {
            "params": {
                "User_id": user_id,
                "User_question": UserQuestion,
                "User_ans": UserAns,
                "system_Ans": system_Ans,
                "User_reason": userSay,
                "answerFrom": answerFrom,
                "User_book": bookName,
                "NextScene": "SQuAD_get_Page"
            }
        },
    }

    print(response)
    return response_dict

# 詢問使用者此答案的頁數
def SQuAD_get_Page(req):
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    user_id = req['session']['params']['User_id']
    userSay = req['intent']['query']
    gameMode = req['session']['params']['game_mode']
    chatbotName = req['session']['params']['chatbotName']
    UserQuestion = req['session']['params']['User_question']
    UserAns = req['session']['params']['User_ans']
    system_Ans = req['session']['params']['system_Ans']
    UserQuestionType = req['session']['params']['User_questionType']
    answerFrom = req['session']['params']['answerFrom']
    bookName = req['session']['params']['User_book']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    pages = None
    UserReason = req['session']['params']['User_reason']
    if "沒有" in userSay or len(userSay) == 0:
        response = "原來不在故事裡，謝謝你告訴我，你可以繼續問我問題囉！"
    else:
        pages = list(map(int, userSay.split(",")))
        response = "第" + userSay.replace(",", "、") + "頁，我記住了！謝謝你告訴我，你可以繼續問我問題囉！"
    
    # 將DB中該本書的訓練次數加一
    connectDB.update_ChatbotTrainRecord(myUserSQuADList, bookName, user_id)
    # 將問句、建議答案、頁數及原因存入ElasticSearch
    connectDB.update_ES_doc(es, dbBookName, user_id, chatbotName, UserQuestion, UserAns, UserReason, pages, UserQuestionType, time)
    
    # 記錄訓練資料
    trainDataList = nowBook['Train_Data']
    if system_Ans == None:
        connectDB.add_DB_TrainData(trainDataList, user_id, UserQuestion, UserQuestionType, system_Ans, None, None, UserAns, UserReason, pages, time)
    else:
        connectDB.add_DB_TrainData(trainDataList, user_id, UserQuestion, UserQuestionType, system_Ans, answerFrom, '錯誤', UserAns, UserReason, pages, time)
    thinking_word = get_thinkingWord()
    sleep(1)
    User_TrainRecord = connectDB.search_ES_TrainContent(es, user_id)
    AllTrainCount, trainRankingIndex = connectDB.find_AllUser_trainCount(myUserSQuADList)
    # 記錄對話
    myDialogList = nowBook['QA_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addQADialog(myDialogList, dialog_id, 'Student', user_id, userSay, time, session_id, gameMode, req['scene']['name'])
    connectDB.addQADialog(myDialogList, dialog_id + 1, 'chatbot', chatbotName, response, time, session_id, gameMode, req['scene']['name'])


    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            }
        },
        "scene": {
            "next": {
                'name': "SQuAD_get_Type"
            }
        },
        "session": {
            "params": {
                "User_id": user_id,
                "User_book": bookName,
                "answerFrom": answerFrom,
                "thinking_word": thinking_word,
                "NowScene": "SQuAD_get_Page",
                "NextScene": "SQuAD_get_Type",
                "User_TrainRecord": User_TrainRecord,
                "AllTrainCount": AllTrainCount,
                "trainRankingIndex": trainRankingIndex
            }
        },
    }

    print(response)
    return response_dict


# 角色引導
def Prompt_character(req):
    print('scene: 角色引導')
    find_common = {'type': 'common_Prompt_character'}
    find_common_result = myCommonList.find_one(find_common)
    response = choice(find_common_result['content'])


    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    user_dialog_count = {}
    dialog_count_limit = req['session']['params']['dialog_count_limit']

    player = req['user']['player']
    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本角色
    response_tmp = ''
    for character in find_material_result['Character']:
        if response_tmp != '':
            response_tmp += '，還有'
        response_tmp += character
    response = response.replace('XX', response_tmp)

    # 如果角色陣列長度為1：修改字串
    find_common = {'type': 'common_character_repeat'}
    find_common_repeat = myCommonList.find_one(find_common)
    response_tmp = choice(find_common_repeat['content'])

    if len(find_material_result['Character']) == 1:
        response_tmp = '你知道他有發生哪些事嗎？'

    if player == 2:
        response = response.replace("你", "你們")
        response_tmp = response_tmp.replace("你", "你們")

    response_len = [len(response) / 2, 1]
    response_list = [response, response_tmp]
    response += response_tmp

    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    dialog_count += 1


    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": response_list,
                "text": response_list,
                "delay": response_len,
                "expressionP": 3,
                "expressionA": 2

            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_character",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "user_dialog_count": user_dialog_count,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 動作引導
def Prompt_action(req):
    print('scene: 動作引導')
    find_common = {'type': 'common_Prompt_action'}
    find_common_result = myCommonList.find_one(find_common)
    response = choice(find_common_result['content'])
    response_len = []

    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']
    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本動作
    response_tmp = ''
    # for verb in find_material_result['Main_Verb']:

    # 20210510 更改抓主要動作 -> 需要判斷有沒有主詞
    while True:
        result = random.choice(list(myVerbList.find({'Verb': find_material_result['Main_Verb'][0]})))
        result_sentence_id = result['Sentence_Id']
        print("result", result)
        if 'C1' in result:
            break


    # # if response_tmp != '':
    # #     response_tmp += '，還有'
    # response_tmp += result['Sentence_translate']
    for word in ['。', '！', '：']:
        response_tmp = response_tmp.replace(word, ' ')
    response = response.replace('XX', response_tmp)

    find_common = {'type': 'common_action_repeat'}
    find_common_repeat = myCommonList.find_one(find_common)
    response_tmp = choice(find_common_repeat['content'])
    response_list = [response, response_tmp]
    response_len = [len(response) / 2, 1]
    response += response_tmp
    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    sentence_id.append(result_sentence_id)
    dialog_count += 1


    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": response_list,
                "text": response_list,
                "delay": response_len,
                "expressionP": 3,
                "expressionA": 2
            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_action",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 對話引導
def Prompt_dialog(req):
    print('scene: 對話引導')
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']
    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 找出隨機一段對話
    find_common = {'type': 'common_Prompt_dialog'}
    find_common_result = myCommonList.find_one(find_common)
    response = choice(find_common_result['content'])
    dialog_sentenceID = choice(find_material_result['Sentence_id'])
    result = myVerbList.find_one({'Sentence_Id': dialog_sentenceID})['Sentence_translate'] + 'X' + myVerbList.find_one({'Sentence_Id': dialog_sentenceID + 1})['Sentence_translate']

    for word in ['。', '，', '！', '：']:
        result = result.replace(word, ' ')
    dialog = result.replace('X', '，然後 ')
    find_common = {'type': 'common_dialog_repeat'}
    find_common_repeat = myCommonList.find_one(find_common)
    response_tmp = choice(find_common_repeat['content'])
    response += dialog
    response_list = [response, response_tmp]
    response_len = [len(response) / 2, 1]
    response += response_tmp
    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    sentence_id.append(dialog_sentenceID)
    sentence_id.append(dialog_sentenceID + 1)
    dialog_count += 1


    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": response_list,
                "text": response_list,
                "delay": response_len,
                "expressionP": 3,
                "expressionA": 2
            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_dialog",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 接龍引導
def Prompt_event(req):
    print('scene: 接龍引導')
    find_common = {'type': 'common_Prompt_action'}
    find_common_result = myCommonList.find_one(find_common)

    response = choice(find_common_result['content'])
    response_len = []

    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']


    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']
    myMaterialList = nowBook['MaterialTable']


    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本動作
    response_tmp = ''

    # 20210429 抓主要事件 (主要動詞與角色 -> 主要角色 -> 主要動詞：需符合有主詞C1 -> 隨機抓取 )
    while True:
        result = list(myVerbList.find({'C1': random.choice(find_material_result['Character']), 'Verb': find_material_result['Main_Verb'][0]}))
        if len(result):
            result = random.choice(result)
            print("主要角色與動作",result)
            result_sentence_id = result['Sentence_Id']
            # print(result_sentence_id)
        else:
            # 找主要角色句子
            result = list(myVerbList.find({'C1': random.choice(find_material_result['Character'])}))
            print("主要角色",result)
            if len(result):
                result = random.choice(result)
                result_sentence_id = result['Sentence_Id']
                # print(result['Sentence_translate'])
                # print(result_sentence_id)
            else:
                # 找主要動詞句子
                result = random.choice(list(myVerbList.find({'Verb': find_material_result['Main_Verb'][0]})))
                result_sentence_id = result['Sentence_Id']
                print("主要動作",result)
                # print(result_sentence_id)
                if 'C1' not in result:
                    result = random.choice(list(myVerbList.find()))
                    result_sentence_id = result['Sentence_Id']
                    print("隨機依據", result)
                    # print(result_sentence_id)


        if result_sentence_id not in sentence_id:
            break
        else:
            try:
                result = random.choice(list(myVerbList.find({"Sentence_Id" : choice([i for i in range(0, len(list(myVerbList.find()))) if i not in sentence_id])})))
                result_sentence_id = result['Sentence_Id']
                print("排除重複", result)
                break
            except IndexError:
                print("強制到下個階段")
                # 目前是不會遇到此問題
                break


    sentence_id.append(result_sentence_id)
    dialog_count += 1

    response_tmp += result['Sentence_translate']
    for word in ['。', '！', '：']:
        response_tmp = response_tmp.replace(word, ' ')
    response = response.replace('XX', response_tmp)

    find_common = {'type': 'common_action_repeat'}
    find_common_repeat = myCommonList.find_one(find_common)
    response_tmp = choice(find_common_repeat['content'])
    response_list = [response, response_tmp]
    response_len = [len(response) / 2, 1]
    response += response_tmp
    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": response_list,
                "text": response_list,
                "delay": response_len,
                "expressionP": 3,
                "expressionA": 2

            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_event",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    # response_dict['prompt'].update({'sentence_id': sentence_id,'dialog_count': dialog_count})
    return response_dict

# 任務引導
# def Prompt_task(req):
#     print('scene: 任務引導')
#     global Prompt_task_list
#     random.shuffle(Prompt_task_list)
#
#     # 任務 Prompt 通用句待改?
#     find_common = {'type': 'common_Prompt_action'}
#     find_common_result = myCommonList.find_one(find_common)
#
#     response = choice(find_common_result['content'])
#
#     session_id = req['session']['id']
#     time = req['user']['lastSeenTime']
#     bookName = req['session']['params']['User_book']
#     dialog_count = req['session']['params']['dialog_count']
#     sentence_id = req['session']['params']['sentence_id']
#     noIdea_count = req['session']['params']['noIdea_count']
#     question_count = req['session']['params']['question_count']
#     User_say_len = req['session']['params']['User_say_len']
#     dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_')
#     nowBook = myClient[dbBookName]
#     myDialogList = nowBook['S_R_Dialog']
#
#
#     # 搜尋對話素材
#     find_myDialogList_result = list(myDialogList.find(
#         {'Phase': 'Prompt_task', 'Task': Prompt_task_list[0], 'Speaker_id': {"$ne": 'chatbot'}}))
#
#     # 對話素材是否存在(有無人回應過)
#     if len(find_myDialogList_result):
#
#
#         find_myDialogList_result = random.choice(find_myDialogList_result)
#
#         # 判斷「生活」任務
#         if Prompt_task_list[0] != "Life":
#             response = response.replace('XX', find_myDialogList_result['Content'])
#         else:
#             response = '跟你說' + find_myDialogList_result['Content'] + '，'
#
#         # 判斷不同任務提供對應response
#         if Prompt_task_list[0] == "Time":
#             response += '那還發生什麼事情？'
#         elif Prompt_task_list[0] == "Location":
#             response += '那哪裡還發生什麼事情呢？'
#         elif Prompt_task_list[0] == "Affection":
#             response += '那你還看到什麼？覺得他的心情如何？'
#         elif Prompt_task_list[0] == "Life":
#             response += '那故事裡讓你想到生活中什麼？'
#     else:
#         if Prompt_task_list[0] == "Time":
#             response = '你知道故事裡發生什麼事情呢？'
#         elif Prompt_task_list[0] == "Location":
#             response = '說說看故事裡他們在哪裡做什麼呢？'
#         elif Prompt_task_list[0] == "Affection":
#             response = '書本裡他們遇到什麼事情心情如何？'
#         elif Prompt_task_list[0] == "Life":
#             response = '這本故事讓你聯想到生活中什麼？'
#
#
#     dialog_count += 1
#
#     # 20210318 修改JSON格式
#     response_dict = {
#         "prompt": {
#             "firstSimple": {
#                 "speech": [response],
#                 "text": [response],
#                 "delay": [2]
#
#             }
#         },
#         "session": {
#             "params": {
#                 "NowScene": "Prompt_task",
#                 "NextScene": "Prompt_response",
#                 "task": Prompt_task_list[0],
#                 "dialog_count": dialog_count,
#                 "sentence_id": sentence_id,
#                 "noIdea_count": noIdea_count,
#                 "question_count": question_count,
#                 "User_say_len": User_say_len,
#                 "dialog_count_limit": dialog_count_limit
#             }
#         },
#         "scene": {
#             "next": {
#                 'name': 'check_input'
#             }
#         }
#     }
#     print(response)
#
#     # 記錄對話
#     myDialogList = nowBook['S_R_Dialog']
#     dialog_index = myDialogList.find().count()
#     dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
#     connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'],
#                         Prompt_task_list[0])
#
#     # response_dict['prompt'].update({'sentence_id': sentence_id,'dialog_count': dialog_count})
#     return response_dict

# 雙人聊天開頭
def Prompt_beginning(req):
    print('scene: 雙人聊天開頭')
    # find_common = {'type': 'common_Prompt_character'}
    # find_common_result = myCommonList.find_one(find_common)
    # response = choice(find_common_result['content'])
    response = "你們先聊聊看到了什麼吧！"
    response_len = []

    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']

    player = req['user']['player']
    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本角色
    response_tmp = ''
    # response_tmp = choice(find_material_result['Character'])
    # for character in find_material_result['Character']:
    #     if response_tmp != '':
    #         response_tmp += '，還有'
    #     response_tmp += character
    print(response_tmp)
    # response = response.replace('XX', response_tmp)

    # 如果角色陣列長度為1：修改字串
    # find_common = {'type': 'common_character_repeat'}
    # find_common_repeat = myCommonList.find_one(find_common)
    # response_tmp = choice(find_common_repeat['content'])

    # if len(find_material_result['Character']) == 1:
    #     response_tmp = '你知道他有發生哪些事嗎？'
    # response_tmp = '那你最喜歡誰呢？'



    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    dialog_count += 1


    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2],
                "expression": "happy"
            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_beginning",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "user_dialog_count": user_dialog_count,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 角色情感引導
def Prompt_character_sentiment(req):
    print('scene: 角色情感引導')
    # find_common = {'type': 'common_Prompt_character'}
    # find_common_result = myCommonList.find_one(find_common)
    # response = choice(find_common_result['content'])
    response = "我最喜歡XX"
    response_len = []

    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']

    player = req['user']['player']
    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']
    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本角色
    response_tmp = ''
    response_tmp = choice(find_material_result['Character'])
    # for character in find_material_result['Character']:
    #     if response_tmp != '':
    #         response_tmp += '，還有'
    #     response_tmp += character
    print(response_tmp)
    response = response.replace('XX', response_tmp)

    # 找主要角色句子
    similarity_sentence = {}
    result = ""
    try:
        result = "，因為" + random.choice(list(myVerbList.find({'C1': response_tmp})))['Sentence_translate']
        result_sentence_id = result['Sentence_Id']
        print(result_sentence_id)
        print(result)

    except IndexError:
        # 找C1與角色相似度高句子
        all_cursor = myVerbList.find()

        # 使用相似度比對
        for cursor in all_cursor:

            cosine = Cosine(2)
            s1 = response_tmp
            if 'C1' in cursor:
                s2 = cursor['C1']

                p1 = cosine.get_profile(s1)
                p2 = cosine.get_profile(s2[0])
                if p1 == {}:
                    # 避免輸入字串太短
                    break
                else:
                    # print('第' + str(cursor['Sentence_Id']) + '句相似度：' + str(cosine.similarity_profiles(p1, p2)))
                    value = cosine.similarity_profiles(p1, p2)
                    if value >= 0.5:
                        similarity_sentence[cursor['Sentence_Id']] = value
        # similarity_sentence = sorted(similarity_sentence.items(), key=lambda x: x[1], reverse=True)

        # 存在相似
        if len(similarity_sentence.keys()):
            result_sentence_id = random.sample(similarity_sentence.keys(), 1)[0]
            result = "，因為" + myVerbList.find({"Sentence_Id": result_sentence_id})[0]['Sentence_translate']
            # print(result_sentence_id)
            print(result)

    response += result
    response_tmp = '那你們最喜歡誰呢？'
    response_len = [len(response) / 2, 1]
    response_list = [response, response_tmp]
    response += response_tmp

    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    sentence_id.append(result_sentence_id)
    dialog_count += 1


    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": response_list,
                "text": response_list,
                "delay": response_len,
                "expression": "happy"
            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_character_sentiment",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "user_dialog_count": user_dialog_count,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 事件情感引導
def Prompt_action_sentiment(req):
    print('scene: 事件情感引導')
    # find_common = {'type': 'common_Prompt_action'}
    # find_common_result = myCommonList.find_one(find_common)
    # response = choice(find_common_result['content'])
    response = "XX讓我印象深刻，"
    response_len = []

    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    player = req['user']['player']
    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']
    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本動作
    response_tmp = ''
    # for verb in find_material_result['Main_Verb']:

    # 20210510 更改抓主要動作 -> 需要判斷有沒有主詞
    while True:
        result = random.choice(list(myVerbList.find({'Verb': find_material_result['Main_Verb'][0]})))
        result_sentence_id = result['Sentence_Id']
        print("result", result)
        if 'C1' in result:
            break

    # if response_tmp != '':
    #     response_tmp += '，還有'
    response_tmp += result['Sentence_translate']
    for word in ['。', '！', '：']:
        response_tmp = response_tmp.replace(word, ' ')
    response = response.replace('XX', response_tmp)


    response_tmp = '那你們最喜歡故事哪個地方呢？'
    response_list = [response, response_tmp]
    response_len = [len(response) / 2, 1]
    response += response_tmp
    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    sentence_id.append(result_sentence_id)
    dialog_count += 1

    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": response_list,
                "text": response_list,
                "delay": response_len,
                "expression": "happy"
            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_action_sentiment",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "user_dialog_count": user_dialog_count,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 詞彙引導
def Prompt_vocabulary(req):
    print('scene: 詞彙引導')
    # find_common = {'type': 'common_Prompt_action'}
    # find_common_result = myCommonList.find_one(find_common)
    # response = choice(find_common_result['content'])

    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    player = req['user']['player']
    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']
    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本動作

    print(find_material_result['Main_Verb'][0])
    response = "書本裡提到" + find_material_result['Main_Verb'][0] + "，我們來講講看是什麼意思呢？"





    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])


    dialog_count += 1

    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": 2,
                "expression": "happy"
            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_vocabulary",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "user_dialog_count": user_dialog_count,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 事件原因引導
def Prompt_action_reason(req):
    print('scene: 事件原因引導')
    # find_common = {'type': 'common_Prompt_action'}
    # find_common_result = myCommonList.find_one(find_common)
    # response = choice(find_common_result['content'])

    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    player = req['user']['player']
    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']
    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本動作

    translator = Translator()
    word_Translate = translator.translate(find_material_result['Main_Verb'][0], src="en", dest="zh-TW").text
    response = "我知道" + find_material_result['Main_Verb'][0] + "是" + word_Translate + "的意思，像是書裡提到"

    # 抓主要動作 -> 需要判斷有沒有主詞
    while True:
        result = random.choice(list(myVerbList.find({'Verb': find_material_result['Main_Verb'][0]})))
        result_sentence_id = result['Sentence_Id']
        print("result", result['Sentence_translate'])
        if 'C1' in result:
            response += result['Sentence_translate']
            break

    C1_Translate = translator.translate(result['C1'][0], src="en", dest="zh-TW").text
    response_tmp = "你們覺得" + C1_Translate + "為什麼要" + find_material_result['Main_Verb'][0]


    response_list = [response, response_tmp]
    response_len = [len(response) / 2, 1]
    response += response_tmp

    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    sentence_id.append(result_sentence_id)
    dialog_count += 1

    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech":  response_list,
                "text":  response_list,
                "delay": response_len,
                "expression": "happy"
            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_action_reason",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "user_dialog_count": user_dialog_count,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 角色經驗引導
def Prompt_character_experience(req):
    print('scene: 角色經驗引導')

    find_common = {'type': 'common_Prompt_character_experience'}
    find_common_result = myCommonList.find_one(find_common)
    response = choice(find_common_result['content'])

    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']

    player = req['user']['player']
    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']

    # 列出提示句子中上次出現角色
    response_tmp = myVerbList.find_one({'Sentence_Id': sentence_id[-1]})['C1']

    print(response_tmp)
    response = response.replace("XX", response_tmp[0])

    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    dialog_count += 1


    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2],
                "expression": "happy"
            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_character_experience",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "user_dialog_count": user_dialog_count,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 事件經驗引導
def Prompt_action_experience(req):
    print('scene: 事件經驗引導')

    find_common = {'type': 'common_Prompt_action_experience'}
    find_common_result = myCommonList.find_one(find_common)
    response = choice(find_common_result['content'])

    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    bookName = req['session']['params']['User_book']
    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']

    player = req['user']['player']
    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    # myVerbList = nowBook['VerbTable']

    # 列出提示句子中上次出現角色
    # response_tmp = myVerbList.find_one({'Sentence_Id': sentence_id[-1]})['C1']
    #
    # print(response_tmp)
    # response = response.replace("XX", response_tmp[0])

    # 記錄對話
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    dialog_count += 1

    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2],
                "expression": "happy"
            }
        },
        "session": {
            "params": {
                "NowScene": "Prompt_action_experience",
                "NextScene": "Prompt_response",
                "dialog_count": dialog_count,
                "sentence_id": sentence_id,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len,
                "user_dialog_count": user_dialog_count,
                "dialog_count_limit": dialog_count_limit
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    return response_dict

# 系統回覆
def Prompt_response(req, predictor, senta):
    print('scene: 系統回覆')
    global Prompt_list, Prompt_task_list
    user_nonsense = 0
    task = ""
    userSay = req['session']['params']['User_say']
    player = req['user']['player']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']
        partner = req['user']['partner']

    userClass = req['session']['params']['User_class']
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    character = req['user']['character']

    bookName = req['session']['params']['User_book']
    nowScene = req['session']['params']['NowScene']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    myVerbList = nowBook['VerbTable']

    if nowScene == 'Prompt_task':
        task = req['session']['params']['task']

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, nowScene)
    # connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, nowScene, task)



    dialog_count = req['session']['params']['dialog_count']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    # 比對故事
    matchStory_all = False
    match_response = ''
    match_repeat = ''
    stop_words = list(stopwords.words('english'))
    for i in ["yourself", "there", "once", "having", "they", "its", "yours", "itself", "is", "him", "themselves",
              "are",
              "we", "these", "your", "his", "me", "were", "her", "himself", "this", "our", "their", "ours", "had",
              "she", "all", "no", "them", "same", "been", "have", "yourselves", "he", "you", "herself", "has",
              "myself",
              "those", "i", "being", "theirs", "my", "against", "it", "she's", 'hers']:
        stop_words.remove(i)
    for i in range(len(stop_words)):
        stop_words[i] = " " + stop_words[i] + " "
    stop_words.extend([' . ', ' , ', '"', ' ! '])

    similarity_sentence = {}
    post_similarity = ''
    twoColumn = []
    trans_word = ''
    translator = Translator()
    # 解決time out狀況
    translator_error = False
    # 將原句翻譯
    try:
        trans_word = translator.translate(userSay, src='zh-TW', dest="en").text
    except Exception as e:
        print(e)
        translator_error = True

    all_cursor = myVerbList.find()
    if not translator_error:
        for word in stop_words:
            post_similarity = trans_word.replace(word, ' ')
        print("USER input:" + str(post_similarity))


        # 20210519 全文相似度比對
        sample_book = myBookList.find_one({'bookName': bookName.replace('_', ' ')})['story_content']
        for word in stop_words:
            sample_book = sample_book.replace(word, ' ')

        cosine = Cosine(2)
        p1 = cosine.get_profile(post_similarity)
        p2 = cosine.get_profile(sample_book.replace('   ', ' ').replace('  ', ' '))
        if p1 == {}:
            # 避免輸入字串太短
            user_nonsense = 1
            print("太短")
        else:
            if cosine.similarity_profiles(p1, p2) == 0:
                # 亂說話相似度0
                user_nonsense = 1
            # 全文相似度
            print(cosine.similarity_profiles(p1, p2))

        # 使用者沒有亂說話
        if user_nonsense == 0:
            # 使用相似度比對
            for cursor in all_cursor:
                cosine = Cosine(2)
                s1 = post_similarity
                s2 = cursor['Sentence']
                for word in stop_words:
                    s2 = s2.replace(word, ' ')
                print(s2)
                p1 = cosine.get_profile(s1)
                p2 = cosine.get_profile(s2)
                if p1 == {}:
                    # 避免輸入字串太短
                    break
                else:
                    # print('第' + str(cursor['Sentence_Id']) + '句相似度：' + str(cosine.similarity_profiles(p1, p2)))
                    value = cosine.similarity_profiles(p1, p2)
                    if value >= 0.5:
                        similarity_sentence[cursor['Sentence_Id']] = value
            similarity_sentence = sorted(similarity_sentence.items(), key=lambda x: x[1], reverse=True)
            print('similarity_sentence：' + str(similarity_sentence))

    if list(similarity_sentence):
        # 有相似的句子
        result = predictor.predict(
            sentence = trans_word
        )
        user_c1 = []
        user_v = []
        user_c2 = []
        v = False
        userColumn_count = 0
        for j in range(len(result['pos'])):
            if v == False and (
                    result['pos'][j] == 'PROPN' or result['pos'][j] == 'NOUN' or result['pos'][j] == 'PRON'):
                if result['words'][j] not in user_c1:
                    user_c1.append(result['words'][j])
                continue
            if (result['pos'][j] == 'VERB' and result['predicted_dependencies'][j] != 'aux') or (
                    result['pos'][j] == 'AUX' and result['predicted_dependencies'][j] == 'root'):
                v = True
                if result['words'][j] not in user_v:
                    user_v.append(result['words'][j])
                continue
            if v == True and (result['pos'][j] == 'PROPN' or result['pos'][j] == 'NOUN'):
                if result['words'][j] not in user_c2:
                    user_c2.append(result['words'][j])
                continue
        # 找出使用者說的話的主動詞
        if list(user_c1):
            userColumn_count += 1
        if list(user_v):
            userColumn_count += 1
        if list(user_c2):
            userColumn_count += 1

        print('USER輸入中的S:' + str(user_c1) + ',V:' + str(user_v) + ',O:' + str(user_c2) + '欄位數量：' + str(
            userColumn_count))

        # 使用者輸入結構超過兩欄位才判斷
        if userColumn_count >= 2:
            for similarity_index in similarity_sentence:
                print(similarity_index[0])
                match_sentence_id = similarity_index[0]

                matchColumn_count = 0
                checkC1 = False
                checkC2 = False
                checkVerb = False

                storyMatch_count = 0
                story_c1 = myVerbList.find_one(
                    {'Sentence_Id': similarity_index[0], "C1": {'$exists': True}})
                if story_c1 is not None:
                    story_c1 = myVerbList.find_one({'Sentence_Id': similarity_index[0]})['C1']
                    storyMatch_count += 1
                story_v = myVerbList.find_one(
                    {'Sentence_Id': similarity_index[0], "Verb": {'$exists': True}})
                if story_v is not None:
                    story_v = myVerbList.find_one({'Sentence_Id': similarity_index[0]})['Verb']
                    storyMatch_count += 1
                story_c2 = myVerbList.find_one(
                    {'Sentence_Id': similarity_index[0], "C2": {'$exists': True}})
                if story_c2 is not None:
                    story_c2 = myVerbList.find_one({'Sentence_Id': similarity_index[0]})['C2']
                    storyMatch_count += 1
                # 滿足兩個欄位
                if storyMatch_count > 1:
                    # 先比對C1
                    word_case = []
                    if not checkC1 and story_c1 is not None:
                        for word in user_c1:
                            word_case = [word, word.lower(), word.capitalize()]
                        word_case = list(set(word_case))
                        # word是否在storyC1中
                        for index in word_case:
                            for c1_index in story_c1:
                                if c1_index == index:
                                    print(c1_index)
                                    checkC1 = True
                                    matchColumn_count += 1
                                    break
                            if checkC1:
                                break
                    # 找V
                    if not checkVerb and story_v is not None:
                        word_morphy = []
                        word_case = []
                        for word in user_v:
                            for i in wordnet._morphy(word, pos='v'):
                                word_morphy.append(i)
                        for index in word_morphy:                            
                            try:
                                trans_word_pre = translator.translate(index, src='en', dest="zh-TW").text
                                trans_word = translator.translate(trans_word_pre, dest="en").extra_data[
                                    'parsed']
                                if len(trans_word) > 3:
                                    for i in trans_word[3][5][0]:
                                        if i[0] == 'verb':
                                            for trans_word_index in i[1]:
                                                word_case.append(trans_word_index[0])
                                            break
                            except Exception as translator_error:
                                print(translator_error)
                                continue
                        word_case.extend(word_morphy)
                        print(word_case)
                        for index in word_case:
                            for v_index in story_v:
                                verb_allResult = wordnet._morphy(v_index, pos='v')
                                for j in verb_allResult:
                                    if j == index:
                                        print(index)
                                        checkVerb = True
                                        matchColumn_count += 1
                                        break
                                if checkVerb:
                                    break
                            if checkVerb:
                                break
                    # 找C2
                    if not checkC2 and story_c2 is not None:
                        word_case = []
                        for word in user_c2:
                            # 找同義字
                            try:
                                trans_word_pre = translator.translate(word, src='en', dest="zh-TW").text
                                trans_word = translator.translate(trans_word_pre, dest="en").extra_data[
                                    'parsed']
                                if len(trans_word) > 3:
                                    for i in trans_word[3][5][0]:
                                        if i[0] == 'noun':
                                            for index in i[1]:
                                                word_case.append(index[0])
                                            break
                            except Exception as translator_error:
                                print(translator_error)
                                continue
                            word_case.extend([word.lower(), word.capitalize()])
                        word_case = list(set(word_case))
                        print(word_case)
                        for index in word_case:
                            for c2_index in story_c2:
                                if c2_index == index:
                                    print(index)
                                    checkC2 = True
                                    matchColumn_count += 1
                                    break
                            if checkC2:
                                break

                    if matchColumn_count == 2:
                        if similarity_index[0] not in twoColumn:
                            twoColumn.append(similarity_index[0])
                    print(str(checkC1) + ',' + str(checkC2) + ',' + str(checkVerb))
                    all_cursor = myVerbList.find()
                    if matchColumn_count == 3:
                        # 比對成功
                        matchStory_all = True
                        find_common = {'type': 'common_match_T'}
                        find_common_result = myCommonList.find_one(find_common)

                        exist_elaboration = myVerbList.find_one(
                            {"Sentence_Id": similarity_index[0], "Student_elaboration": {'$exists': True}})

                        print("Sentence_Id", similarity_index[0])
                        if exist_elaboration is not None:
                            # 若有學生曾輸入過的詮釋 > 回答該句
                            find_common_QA = {'type': 'common_QA'}
                            find_common_result_QA = myCommonList.find_one(find_common_QA)
                            match_repeat = choice(find_common_result_QA['content']) + choice(
                                all_cursor[similarity_index[0]]['Student_elaboration'])
                            match_response = choice(find_common_result['content'])
                        else:
                            result = all_cursor[similarity_index[0]]['Sentence_translate']
                            for word in ['。', '，', '！', '“', '”', '：']:
                                result = result.replace(word, ' ')
                            match_repeat = result
                            match_response = choice(find_common_result['content'])
                        break
                    else:
                        similarity_sentence.remove(similarity_index)
    noMatch = False

    if matchStory_all:
        if userClass == '戊班':
            # 獎勵機制
            user_result = myUserList.find_one({'User_id': user_id})
            user_result_updated = connectDB.copy.deepcopy(user_result)
            if 'Score' not in user_result_updated['BookTalkSummary'][bookName]:
                user_result_updated['BookTalkSummary'][bookName].update({'Score': 0})
            user_result_updated['BookTalkSummary'][bookName]['Score'] += 3
            print('update_user: ', user_result_updated)
            myUserList.update_one(user_result, {'$set': user_result_updated})

            common_result = myCommonList.find_one({'type': 'common_score'})
            response_star = choice(common_result['content'])
            response_star = response_star.replace('X', '3')
            response_star_copy = response_star
            response_star += '⭐' * 3
            # user_result_updated['BookTalkSummary'][bookName]['Score']
            response = match_response + match_repeat + response_star + '！' + '那接下來還有嗎？'
            response_speech = match_response + match_repeat + response_star_copy + '！' + '那接下來還有嗎？'
        else:
            response = match_response + match_repeat + '那接下來還有嗎？'
            response_speech = match_response + match_repeat + '那接下來還有嗎？'
    else:
        if len(twoColumn) != 0:
            print('有兩欄位的')
            twoColumnMatch = choice(twoColumn)
            print(twoColumnMatch)
            match_sentence_id = twoColumnMatch
            # 比對成功
            find_common = {'type': 'common_match_T'}
            find_common_result = myCommonList.find_one(find_common)
            exist_elaboration = myVerbList.find_one(
                {"Sentence_Id": twoColumnMatch, "Student_elaboration": {'$exists': True}})
            if exist_elaboration is not None:
                # 若有學生曾輸入過的詮釋 > 回答該句
                find_common_QA = {'type': 'common_QA'}
                find_common_result_QA = myCommonList.find_one(find_common_QA)
                response = choice(find_common_result['content'])
                match_repeat = choice(find_common_result_QA['content']) + choice(all_cursor[twoColumnMatch]['Student_elaboration'])
            else:
                result = all_cursor[twoColumnMatch]['Sentence_translate']
                for word in ['。', '，', '！', '“', '”', '：']:
                    result = result.replace(word, ' ')
                match_repeat = result
                response = choice(find_common_result['content'])

            if userClass == '戊班':
                # 獎勵機制
                user_result = myUserList.find_one({'User_id': user_id})
                user_result_updated = connectDB.copy.deepcopy(user_result)
                if 'Score' not in user_result_updated['BookTalkSummary'][bookName]:
                    user_result_updated['BookTalkSummary'][bookName].update({'Score': 0})
                user_result_updated['BookTalkSummary'][bookName]['Score'] += 3
                print('update_user: ', user_result_updated)
                myUserList.update_one(user_result, {'$set': user_result_updated})

                common_result = myCommonList.find_one({'type': 'common_score'})
                response_star = choice(common_result['content'])
                response_star = response_star.replace('X', '3')
                response_star_copy = response_star
                response_star += '⭐' * 3

                response_speech = response + match_repeat + response_star_copy + '！' + '那接下來還有嗎？'
                response += match_repeat + response_star + '！' + '那接下來還有嗎？'

            else:
                response += match_repeat + '那接下來還有嗎？'
                response_speech = response
        else:
            # 沒比對到的固定回覆
            find_common = {'type': 'common_Prompt_response'}
            find_common_result = myCommonList.find_one(find_common)
            response = choice(find_common_result['content'])
            response_speech = response
            noMatch = True

    task = ""

    dialog_count += 1


    # 計算各個使用者"連續"對話數
    if player == 2:
        partner_tmp = userClass + partner
        if user_id in user_dialog_count:
            user_dialog_count[user_id] += 1
        else:
            user_dialog_count[user_id] = 1
        user_dialog_count[partner_tmp] = 0


    # 20210506 對話計數 紀錄比對到的句子
    if not noMatch:
        sentence_id.append(match_sentence_id)


    if dialog_count < dialog_count_limit and player == 1:

        # 20210505 沒比對到 且 場景在 Prompt_event
        if noMatch and nowScene == 'Prompt_event':

            # 找正確句子 上次比對到句子的下一句話
            count = 1
            while True:
                nextSentence = myVerbList.find_one({"Sentence_Id": sentence_id[-1] + count})

                # 避免句數超過抓不到採取隨機抓
                if nextSentence is None:
                    nextSentence = random.choice(list(myVerbList.find()))

                # 符合有主詞條件
                if 'C1' in nextSentence:
                    break
                else:
                    count += 1

            response = '好像不是這樣' + ' 書本提到句子是'
            response_tmp = nextSentence['Sentence'] + '<br>' + ' 意思是 ' + nextSentence[
                'Sentence_translate'] + ' 那接下來怎麼了?'
            response_speech_tmp = nextSentence['Sentence'] + ' 意思是 ' + nextSentence[
                'Sentence_translate'] + ' 那接下來怎麼了?'
            response_list = [response, response_tmp]
            response_speech_list = [response, response_speech_tmp]
            sentence_id.append(nextSentence['Sentence_Id'])

            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": response_speech_list,
                        "text": response_list,
                        "delay": [2],
                        "expression": "frightened"
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        'name': 'check_input'
                    }
                }
            }

            response += response_tmp
        # 使用者回答無關內容
        elif user_nonsense == 1:

            response = "你說得跟內容無關喔！告訴我發生什麼了吧！"
            response_speech = response
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response_speech],
                        "text": [response],
                        "delay": [2],
                        "expression": "frightened"
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                }
            }
        # 目前場景在 Prompt_task
        elif nowScene == 'Prompt_task':
            # 回應句子
            response_tmp = ""
            # 紀錄目前任務
            task = Prompt_task_list[0]

            # 判斷目前任務是否為「生活」
            if task != "Life":
                # 非生活任務 正面回應 + Prompt新任務通用句處理
                find_common = {'type': 'common_match_T'}
                find_common_result = myCommonList.find_one(find_common)
                response = choice(find_common_result['content'])

                find_common = {'type': 'common_Prompt_action'}
                find_common_result = myCommonList.find_one(find_common)
                response_tmp = choice(find_common_result['content'])
            else:
                # 生活根據情感正負向回應
                # Senta情感分析
                input_dict = {"text": [userSay]}
                results = senta.sentiment_classify(data = input_dict)
                print("senta result", results)
                if results[0]['sentiment_key'] == "positive" and results[0]['positive_probs'] >= 0.7:
                    response = "聽起來很棒耶！"
                elif results[0]['sentiment_key'] == "positive":
                    response = "哦哦哦哦哦哦！我了解了！"
                else:
                    response = "聽起來很不好耶！"

            # 釋放目前任務
            Prompt_task_list.pop(0)

            # Prompt_task_list為空
            if len(Prompt_task_list) == 0:
                Prompt_task_list = ['Time', 'Location', 'Affection', 'Life']
                random.shuffle(Prompt_task_list)

            task = Prompt_task_list[0]

            # 搜尋對話素材
            find_myDialogList_result = list(myDialogList.find(
                {'Phase': 'Prompt_task', 'Task': Prompt_task_list[0], 'Speaker_id': {"$ne": 'chatbot'}}))

            # 對話素材是否存在(有無人回應過)
            if len(find_myDialogList_result):

                find_myDialogList_result = random.choice(find_myDialogList_result)

                # 判斷「生活」任務
                if Prompt_task_list[0] != "Life":
                    response_tmp = response_tmp.replace('XX', find_myDialogList_result['Content'])
                else:
                    response_tmp = '跟你說' + find_myDialogList_result['Content'] + '，'

                # 判斷不同任務提供對應response
                if Prompt_task_list[0] == "Time":
                    response_tmp += '那還發生什麼事情？'
                elif Prompt_task_list[0] == "Location":
                    response_tmp += '那哪裡還發生什麼事情呢？'
                elif Prompt_task_list[0] == "Affection":
                    response_tmp += '那你還看到什麼？覺得他的心情如何？'
                elif Prompt_task_list[0] == "Life":
                    response_tmp += '那故事裡讓你想到生活中什麼？'
            else:
                if Prompt_task_list[0] == "Time":
                    response_tmp = '你知道故事裡發生什麼事情呢？'
                elif Prompt_task_list[0] == "Location":
                    response_tmp = '說說看故事裡他們在哪裡做什麼呢？'
                elif Prompt_task_list[0] == "Affection":
                    response_tmp = '書本裡他們遇到什麼事情心情如何？'
                elif Prompt_task_list[0] == "Life":
                    response_tmp = '這本故事讓你聯想到生活中什麼？'

            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response, response_tmp],
                        "text": [response, response_tmp],
                        "delay": [2]
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                        "task": task,
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                }
            }
            response += response_tmp



        elif nowScene == 'Prompt_character_sentiment':
            # 回應句子
            response = ""

            if dialog_count == 2:
                response = "為什麼你喜歡阿？"
            elif dialog_count == 3:
                response = "如果是你會怎麼做？"

            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                }
            }
            # response += response_tmp

        else:

            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response_speech],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                }
            }

    elif dialog_count < dialog_count_limit and player == 2:

        if user_dialog_count[user_id] == 3:
            user_dialog_count[user_id] = 0
            if noMatch:
                response = ""
                response_speech = ""
            question_count = req['session']['params']['question_count']
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response_speech],
                        "text": [response],
                        "delay": [len(response) / 2]
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "user_dialog_count": user_dialog_count,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": "Moderator"
                    }
                }
            }
        elif user_nonsense == 1:

            response = "你說得跟內容無關喔！告訴我發生什麼了吧！"
            response_speech = response
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response_speech],
                        "text": [response],
                        "delay": [2],
                        "expression": "frightened"
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "user_dialog_count": user_dialog_count,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                }
            }
        elif dialog_count == 3 and nowScene != "Prompt_vocabulary":
            if noMatch:
                response = ""
                response_speech = ""
            question_count = req['session']['params']['question_count']
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response_speech],
                        "text": [response],
                        "delay": [len(response) / 2]
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "user_dialog_count": user_dialog_count,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": "Moderator_connect"
                    }
                }
            }
        # 進度Real場景
        # elif dialog_count == 2:
        #     if noMatch:
        #         response = ""
        #         response_speech = ""
        #     question_count = req['session']['params']['question_count']
        #     response_dict = {
        #         "prompt": {
        #             "firstSimple": {
        #                 "speech": [response_speech],
        #                 "text": [response],
        #                 "delay": [len(response) / 2]
        #             }
        #         },
        #         "session": {
        #             "params": {
        #                 "User_say": userSay,
        #                 "dialog_count": dialog_count,
        #                 "sentence_id": sentence_id,
        #                 "noIdea_count": noIdea_count,
        #                 "question_count": question_count,
        #                 "User_say_len": User_say_len,
        #                 "user_dialog_count": user_dialog_count,
        #                 "dialog_count_limit": dialog_count_limit
        #             }
        #         },
        #         "scene": {
        #             "next": {
        #                 "name": "Real"
        #             }
        #         }
        #     }
        # elif dialog_count == 4:
        #     if noMatch:
        #        response = ""
        #        response_speech = ""
        #     question_count = req['session']['params']['question_count']
        #     response_dict = {
        #         "prompt": {
        #             "firstSimple": {
        #                 "speech": [response_speech],
        #                 "text": [response],
        #                 "delay": [len(response) / 2],
        #                 "expression": "happy"
        #             }
        #         },
        #         "session": {
        #             "params": {
        #                 "User_say": userSay,
        #                 "dialog_count": dialog_count,
        #                 "sentence_id": sentence_id,
        #                 "noIdea_count": noIdea_count,
        #                 "question_count": question_count,
        #                 "User_say_len": User_say_len,
        #                 "user_dialog_count": user_dialog_count
        #                 "dialog_count_limit": dialog_count_limit
        #             }
        #         },
        #         "scene": {
        #             "next": {
        #                 "name": "Nonsense"
        #             }
        #         }
        #     }
        else:
            if noMatch:
               response = ""
               response_speech = ""
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response_speech],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    }
                },
                "session": {
                    "params": {
                        "User_say": userSay,
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "user_dialog_count": user_dialog_count,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": "check_input"
                    }
                }
            }
    else:
        # 換提示場景 判斷剩下場景是否為空
        if '戊班' in user_id and req['session']['params']['next_level']:
            # 獎勵機制
            user_result = myUserList.find_one({'User_id': user_id})
            user_result_updated = connectDB.copy.deepcopy(user_result)
            if 'Score' not in user_result_updated['BookTalkSummary'][bookName]:
                user_result_updated['BookTalkSummary'][bookName].update({'Score': 0})
            user_result_updated['BookTalkSummary'][bookName]['Score'] += 1
            print('update_user: ', user_result_updated)
            myUserList.update_one(user_result, {'$set': user_result_updated})

        if not Prompt_list:
            # 空場景
            if player == 1:
                Prompt_list.append("expand")
            else:
                Prompt_list.append("expand_2players")
        else:
            dialog_count = 0



        # 獎勵機制 戊班在場景中有講過話給星星，除了Prompt_event場景
        if '戊班' in user_id and req['session']['params']['next_level'] and nowScene != 'Prompt_event':
            response = ""
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": ["你講得很好呢！送你1顆星星。"],
                        "text": ["你講得很好呢！送你1顆星星⭐。"],
                        "delay": [6],
                        "expression": "excited"
                    },
                    "score": 1
                },
                "session": {
                    "params": {
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "next_level": False,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": Prompt_list[0]
                    }
                }
            }

        else:
            response = ""
            # 20211006 雙人階段稱讚回復
            if player == 2:
                response = random.choice(['你們都講得很好呢！', '你們說的很好唷！', '你們講得很不錯！', '沒錯！沒錯！你們說的真好'])
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2],
                        "expression": "happy"
                    }
                },
                "session": {
                    "params": {
                        "dialog_count": dialog_count,
                        "sentence_id": sentence_id,
                        "noIdea_count": noIdea_count,
                        "question_count": question_count,
                        "User_say_len": User_say_len,
                        "dialog_count_limit": dialog_count_limit
                    }
                },
                "scene": {
                    "next": {
                        "name": Prompt_list[0]
                    }
                }
            }

        Prompt_list.pop(0)

        if player == 2:
            response_dict['session']['params'].update({"user_dialog_count": user_dialog_count})




    # 20210408
    if not noMatch and userClass == '戊班':
        response_dict['prompt'].update({'score': 3})
    # 20210406 星星圖片
    # if not noMatch and userClass == '戊班':
    #     response_dict['prompt'].update({
    #                                     'content': {
    #                                         'image': {
    #                                             'url': 'https://pngimg.com/uploads/star/star_PNG41495.png',
    #                                             'alt': 'star'
    #                                         }
    #                                     }
    #                                 })

    # 記錄對話過程
    if response != "":
        dialog_index = myDialogList.find().count()
        dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
        connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, nowScene)
        # connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, nowScene, task)

    print(response)
    return response_dict

# 學生提問單字句子
def Question(req):
    print('scene: Question')
    userSay = req['session']['params']['User_say']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    dialog_count = req['session']['params']['dialog_count']
    time = req['user']['lastSeenTime']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    player = req['user']['player']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id']

    # 抓取使用者之前對話話題
    count = 1
    if dialog_count > 1:
        while True:
            last_user_dialog = myDialogList.find_one({'Session_id': session_id, 'Dialog_id': dialog_id - count})
            if '我想問' not in last_user_dialog['Content']:
                response_tmp = "那你剛剛說的 " + last_user_dialog['Content'] + "，接下來還發生了什麼呢?"
                break
            else:
                count += 2
    else:
        response_tmp = "回到剛剛的話題 接下來還發生了什麼呢?"

    # 記錄對話過程
    dialog_id += 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])

    replace_list = ["我想問", "是", "什麼", "甚麼", "意思", "?"]
    for que_word in replace_list:
        userSay = userSay.replace(que_word, "")

    translator = Translator()
    sentence_Translate = translator.translate(userSay, src="en", dest="zh-TW").text
    response = "我知道這個意思是 " + sentence_Translate
    response_list = [response, response_tmp]
    print(sentence_Translate)



    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": response_list,
                "text": response_list,
                "delay": [2],
                "expressionP": 1,
                "expressionA": 1
            }
        },
        "params": {
            "NextScene": "Prompt_response"
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }

    response += response_tmp
    # 記錄對話
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    return response_dict

# 表示感受
def Feeling(req):
    print('scene: Feeling')
    userSay = req['session']['params']['User_say']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    dialog_count = req['session']['params']['dialog_count']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    time = req['user']['lastSeenTime']
    partner = req['user']['partner']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    player = req['user']['player']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id']

    feeling = random.choice(['positive', 'negative', 'neutral'])

    response = ""
    if feeling == 'positive':
        response += '我覺得很棒耶，'
    elif feeling == 'negative':
        response += '我覺得沒有，'
    else:
        response += '我覺得還好，'


    if int(partner) in studentName_dic:
        partner_name = studentName_dic[int(partner)]
    else:
        partner_name = partner + "號"
    response += '那XX你覺得呢？'
    response = response.replace("XX", partner_name)

    # 記錄對話過程
    dialog_id += 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])




    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            }
        },
        "params": {
            "NextScene": "Prompt_response"
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }


    # 記錄對話
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    return response_dict

# 表示認同
def Assent(req):
    print('scene: Assent')
    userSay = req['session']['params']['User_say']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    dialog_count = req['session']['params']['dialog_count']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    time = req['user']['lastSeenTime']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    player = req['user']['player']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id']

    res_assent = random.choice(["沒錯，我也是這樣想！", "對阿對阿，就是那樣！", '哈哈哈我也這麼覺得耶！'])
    response = res_assent



    # 記錄對話過程
    dialog_id += 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])




    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            }
        },
        "params": {
            "NextScene": "Prompt_response"
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }


    # 記錄對話
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    return response_dict



# 機器人胡言亂語
def Nonsense(req):
    print('scene: Nonsense')
    userSay = req['session']['params']['User_say']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    dialog_count = req['session']['params']['dialog_count']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    time = req['user']['lastSeenTime']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    player = req['user']['player']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']

    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id']

    find_common = {'type': 'common_nonsense'}
    find_result = myCommonList.find_one(find_common)
    response = choice(find_result['content'])


    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本角色
    response_tmp = choice(find_material_result['Character'])
    response = response.replace('XX', response_tmp)


    # 記錄對話過程
    dialog_id += 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])




    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            }
        },
        "params": {
            "NextScene": "Prompt_response",
            "dialog_count": dialog_count,
            "sentence_id": sentence_id,
            "noIdea_count": noIdea_count,
            "question_count": question_count,
            "User_say_len": User_say_len,
            "user_dialog_count": user_dialog_count,
            "dialog_count_limit": dialog_count_limit

        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }


    # 記錄對話
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    return response_dict

# 機器人說小朋友說過的話
def Real(req):
    print('scene: Real')
    userSay = req['session']['params']['User_say']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    dialog_count = req['session']['params']['dialog_count']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    time = req['user']['lastSeenTime']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    player = req['user']['player']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']

    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id']


    find_result = list(myDialogList.find({"$and": [{"Speaker_id": {'$ne': 'chatbot'}},
                                                   {"Speaker_id": {'$ne': 'Chatbot'}},
                                                   {"Content": {"$regex": "^.{5,}$"}}]}))

    if not len(find_result):
        # 沒有學生對話
        response = ""
    else:
        # 取學生對話最相似句子
        similarity_sentence = {}
        for dialog in find_result:
            cosine = Cosine(2)
            p1 = cosine.get_profile(userSay)
            p2 = cosine.get_profile(dialog['Content'])
            if p1 == {}:
                # 字串太短
                break
            else:
                value = cosine.similarity_profiles(p1, p2)
                similarity_sentence[dialog['Content']] = value

        similarity_sentence = sorted(similarity_sentence.items(), key=lambda x: x[1], reverse=True)
        print('similarity_sentence：' + str(similarity_sentence))

        # 判斷空串列
        if len(similarity_sentence):
            # 取最相似句子
            response = str(similarity_sentence[0][0])
        else:
            # 隨機選取
            response = random.choice(find_result)['Content']


    # 記錄對話過程
    dialog_id += 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])




    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            }
        },
        "params": {
            "NextScene": "Prompt_response",
            "dialog_count": dialog_count,
            "sentence_id": sentence_id,
            "noIdea_count": noIdea_count,
            "question_count": question_count,
            "User_say_len": User_say_len,
            "user_dialog_count": user_dialog_count,
            "dialog_count_limit": dialog_count_limit

        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }


    # 記錄對話
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    return response_dict

# 機器人協調換人說
def Moderator(req):
    print('Moderator')
    userSay = req['session']['params']['User_say']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    dialog_count = req['session']['params']['dialog_count']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']

    time = req['user']['lastSeenTime']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    player = req['user']['player']
    partner = req['user']['partner']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']

    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id']


    res_moderator = random.choice(["XX講得很好喔！OO有什麼想法嗎？", "OO也說說看你覺得如何？", 'OO換你說說看吧！', "OO你在想什麼呢？"])
    user_id_tmp = user_id.replace("戊班", "").replace("丁班", "")
    # 判斷座號有無學生姓名
    if int(user_id_tmp) in studentName_dic:
        name = studentName_dic[int(user_id_tmp)]
    else:
        name = user_id_tmp + "號"
    if int(partner) in studentName_dic:
        partner_name = studentName_dic[int(partner)]
    else:
        partner_name = partner + "號"
    response = res_moderator.replace("XX", name).replace("OO", partner_name)

    # 記錄對話過程
    dialog_id += 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])




    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            }
        },
        "params": {
            "NextScene": "Prompt_response",
            "dialog_count": dialog_count,
            "sentence_id": sentence_id,
            "noIdea_count": noIdea_count,
            "question_count": question_count,
            "User_say_len": User_say_len,
            "user_dialog_count": user_dialog_count,
            "dialog_count_limit": dialog_count_limit

        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }


    # 記錄對話
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    return response_dict

# 機器人協調換人說
def Moderator_connect(req):
    print('scene: 協調串連')
    userSay = req['session']['params']['User_say']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    dialog_count = req['session']['params']['dialog_count']
    dialog_count_limit = req['session']['params']['dialog_count_limit']
    sentence_id = req['session']['params']['sentence_id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    nowScene = req['session']['params']['NowScene']
    time = req['user']['lastSeenTime']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    player = req['user']['player']
    partner = req['user']['partner']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']

    if player == 2:
        user_dialog_count = req['session']['params']['user_dialog_count']

    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id']

    res_moderator = ""
    if nowScene == "Prompt_character":
        res_moderator = random.choice(["OO你有看到和XX相同的地方嗎？", "XX說到的地方，OO你覺得如何？"])
    elif nowScene == "Prompt_action_reason" or nowScene == "Prompt_character_sentiment":
        res_moderator = random.choice(["OO你覺得XX說得如何？", "OO你覺得XX說得怎麼樣？說說你的想法吧！", 'OO說說你對XX講的想法吧！'])
    elif nowScene == "Prompt_action_experience" or nowScene == "Prompt_character_experience":
        res_moderator = random.choice(["OO也有和XX遇過相同事情嗎？", "OO你和XX有類似經驗嗎？", "OO你覺得XX說得怎麼樣？說說你的想法吧！", 'OO說說你對XX講的想法吧！'])




    user_id_tmp = user_id.replace("戊班", "").replace("丁班", "")

    # 判斷座號有無學生姓名
    if int(user_id_tmp) in studentName_dic:
        name = studentName_dic[int(user_id_tmp)]
    else:
        name = user_id_tmp + "號"
    if int(partner) in studentName_dic:
        partner_name = studentName_dic[int(partner)]
    else:
        partner_name = partner + "號"
    response = res_moderator.replace("XX", name).replace("OO", partner_name)

    # 記錄對話過程
    dialog_id += 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])




    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [2]
            }
        },
        "params": {
            "NextScene": "Prompt_response",
            "dialog_count": dialog_count,
            "sentence_id": sentence_id,
            "noIdea_count": noIdea_count,
            "question_count": question_count,
            "User_say_len": User_say_len,
            "user_dialog_count": user_dialog_count,
            "dialog_count_limit": dialog_count_limit

        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }


    # 記錄對話
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    return response_dict


# 學生心得回饋
def expand(req):
    print("scene: Expand")
    user_id = req['session']['params']['User_id']
    bookName = req['session']['params']['User_book']
    time = req['user']['lastSeenTime']
    session_id = req['session']['id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    userClass = req['session']['params']['User_class']
    if 'User_expand' in req['session']['params'].keys():
        expand_user = req['session']['params']['User_expand']
    else:
        expand_user = False
    if not expand_user:

        find_common_expand = {'type': 'common_expand'}
        common_result_expand = myCommonList.find_one(find_common_expand)
        find_common = {'type': 'common_like'}
        find_result = myCommonList.find_one(find_common)
        # 戊班星星總數
        if userClass == '戊班':
            # 原始:目前為止你有OO顆星星了！ .replace('OO', str(total_star))
            star_response = '你在這本書已經拿到XX顆星星⭐囉！'
            user_result = myUserList.find_one({'User_id': user_id})
            book_star = 0
            total_star = 0
            if "Score" in user_result['BookTalkSummary'][bookName]:
                book_star = user_result['BookTalkSummary'][bookName]['Score']
            for book_key in user_result['BookTalkSummary'].keys():
                if "Score" in user_result['BookTalkSummary'][book_key]:
                    total_star += user_result['BookTalkSummary'][book_key]['Score']
            star_response = star_response.replace('XX', str(book_star))
            response = choice(common_result_expand['content']) + ' ' + star_response + ' ' + choice(find_result['content'])
            response_speech = response.replace('⭐', '')
        else:
            response = choice(common_result_expand['content']) + ' ' + choice(find_result['content'])
            response_speech = response
        expand_user = True
        # 記錄對話過程
        dialog_index = myDialogList.find().count()
        dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
        connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
        # response_dict = {"prompt": {
        #     "firstSimple": {
        #         "speech": response,
        #         "text": response
        #     }, 'suggestions': [{'title': '喜歡'},
        #                        {'title': '還好'},
        #                        {'title': '不喜歡'}]},
        #     'session': {
        #         'params': {
        #             'User_expand': expand_user
        #         }
        #     }
        # }

        # 20210318 修改JSON格式
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response_speech],
                    "text": [response],
                    "delay": [2],
                    "expressionP": 3,
                    "expressionA": 1
                },
                "suggestions": [{"title": "喜歡"},
                                {"title": "還好"},
                                {"title": "不喜歡"}]
            },
            "session": {
                "params": {
                    "User_expand": expand_user
                }
            }
        }
        # if userClass == '戊班':
        #     response_dict['prompt']['firstSimple']['speech'] = response.replace('⭐', '')
        #     print("response_dict['prompt']['firstSimple']['speech']",response_dict['prompt']['firstSimple']['speech'])
    else:
        response = ''
        expressionP = 0
        expressionA = 0
        expression = ""
        suggest_like = False
        dialog_index = myDialogList.find().count()
        dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
        userSay = req['intent']['query']
        connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id,
                            req['scene']['name'])
        scene = 'feedback'
        if userSay == '還好' or userSay == '普通':
            response = '這樣啊！那是為甚麼呢？'
            suggest_like = False
            expression = "frightened"
        elif userSay == '喜歡':
            # 接續詢問使用者喜歡故事的原因
            find_common = {'type': 'common_like_response'}
            find_common2 = {'type': 'common_like_expand'}
            find_result = myCommonList.find_one(find_common)
            find_result2 = myCommonList.find_one(find_common2)
            response = choice(find_result['content']) + ' ' + choice(find_result2['content'])
            suggest_like = True
            expressionP = 3
            expressionA = 1
        elif userSay == '不喜歡':
            find_common = {'type': 'common_like_F_expand'}
            find_result = myCommonList.find_one(find_common)
            response = choice(find_result['content'])
            suggest_like = False
            expressionP = -5
            expressionA = -1
        else:
            scene = 'expand'
            expressionP = 3
            expressionA = 1
        expand_user = False
        dialog_index = myDialogList.find().count()
        dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
        connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
        # response_dict = {"prompt": {
        #     "firstSimple": {
        #         "speech": response,
        #         "text": response
        #     }},
        #     "scene": {
        #         "next": {
        #             'name': scene
        #         }
        #     },
        #     "session": {
        #         "params": dict(User_sentiment=suggest_like,
        #                        User_state=state, User_expand=expand_user)}
        # }

        # 20210318 修改JSON格式
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [2],
                    "expressionP": expressionP,
                    "expressionA": expressionA
                }
            },
            "session": {
                "params": dict(User_sentiment=suggest_like,
                               User_expand=expand_user,
                               noIdea_count=noIdea_count,
                               question_count=question_count,
                               User_say_len=User_say_len)
            },
            "scene": {
                "next": {
                    'name': scene
                }
            }
        }


    print(response)
    return response_dict




# 從資料庫中取資料做為機器人給予學生之回饋
def feedback(req):
    print('scene: Feedback')
    state = True
    userSay = req['intent']['query']
    user_id = req['session']['params']['User_id']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myFeedback = nowBook['Feedback']
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # 記錄對話過程
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])
    find_common = {'type': 'common_feedback'}
    find_result = myCommonList.find_one(find_common)
    find_feedback_student = {'type': 'common_feedback_student'}
    result_feedback_student = myCommonList.find_one(find_feedback_student)
    suggest_like = req['session']['params']['User_sentiment']
    find_like = {'Sentiment': suggest_like}
    result_like = myFeedback.find(find_like)
    if result_like.count() == 0:
        response = '哦！原來是這樣啊！我了解了，'
    else:
        if result_like.count() > 2:
            choose_number = random.sample(range(0, result_like.count() - 1), 2)
            response = choice(find_result['content']) + " " + result_like[choose_number[0]]['Content'] + "，" + choice(
                result_feedback_student['content']) + " " + result_like[choose_number[1]]['Content']
        elif result_like.count() == 2:
            response = choice(find_result['content']) + " " + result_like[0]['Content'] + "，" + choice(
                result_feedback_student['content']) + " " + result_like[1]['Content']
        else:
            choose_number = 0
            response = choice(find_result['content']) + " " + result_like[choose_number]['Content']

    response_tmp = '我可以推薦你一些書，你想看看嗎？'
    # response_dict = {"prompt": {
    #     "firstSimple": {
    #         "speech": response,
    #         "text": response
    #     },
    #     'suggestions': [{'title': '好'}, {'title': '不用了'}]},
    #     "scene": {
    #         "next": {
    #             'name': 'Check_suggestion'
    #         }
    #     }
    # }

    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response, response_tmp],
                "text": [response, response_tmp],
                "delay": [len(response) / 2, 1],
                "expressionP": 3,
                "expressionA": 1
            },
            "suggestions": [{'title': '好'}, {'title': '不用了'}]
        },
        "session": {
            "params": {
                "User_state": state,
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len

            }
        },
        "scene": {
            "next": {
                "name": "Check_suggestion"
            }
        }
    }

    response += response_tmp
    connectDB.updateUser(myUserList, user_id, bookName, state, "None")
    connectDB.addFeedback(myFeedback, user_id, suggest_like, userSay)
    # 記錄對話過程
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
    print(response)
    return response_dict


# 學生心得回饋
def expand_2players(req):
    print("scene: Expand_2players")

    user_id = req['user']['User_id']
    bookName = req['session']['params']['User_book']
    time = req['user']['lastSeenTime']
    session_id = req['session']['id']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    partner = req['user']['partner']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    userClass = req['session']['params']['User_class']
    if 'User_expand' in req['session']['params'].keys():
        expand_user = req['session']['params']['User_expand']
    else:
        expand_user = False
    if 'Partner_expand' in req['session']['params'].keys():
        Partner_expand = req['session']['params']['Partner_expand']
    else:
        Partner_expand = False
    if not expand_user:
        find_common_expand = {'type': 'common_expand'}
        common_result_expand = myCommonList.find_one(find_common_expand)
        find_common = {'type': 'common_like'}
        find_result = myCommonList.find_one(find_common)
        # 戊班星星總數
        if userClass == '戊班':
            # 原始:目前為止你有OO顆星星了！ .replace('OO', str(total_star))
            star_response = '你在這本書已經拿到XX顆星星⭐囉！'
            user_result = myUserList.find_one({'User_id': user_id})
            book_star = 0
            total_star = 0
            if "Score" in user_result['BookTalkSummary'][bookName]:
                book_star = user_result['BookTalkSummary'][bookName]['Score']
            for book_key in user_result['BookTalkSummary'].keys():
                if "Score" in user_result['BookTalkSummary'][book_key]:
                    total_star += user_result['BookTalkSummary'][book_key]['Score']
            star_response = star_response.replace('XX', str(book_star))
            response = choice(common_result_expand['content']) + ' ' + star_response + ' ' + choice(find_result['content'])
            response_speech = response.replace('⭐', '')
        else:
            response = choice(common_result_expand['content']).replace('你', '你們') + ' ' + choice(find_result['content']).replace('你', '你們')
            response_speech = response
        expand_user = True
        # 記錄對話過程
        dialog_index = myDialogList.find().count()
        dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
        connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
        # response_dict = {"prompt": {
        #     "firstSimple": {
        #         "speech": response,
        #         "text": response
        #     }, 'suggestions': [{'title': '喜歡'},
        #                        {'title': '還好'},
        #                        {'title': '不喜歡'}]},
        #     'session': {
        #         'params': {
        #             'User_expand': expand_user
        #         }
        #     }
        # }

        # 20210318 修改JSON格式
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response_speech],
                    "text": [response],
                    "delay": [2]
                },
                "suggestions": [{"title": "喜歡"},
                                {"title": "還好"},
                                {"title": "不喜歡"}]
            },
            "session": {
                "params": {
                    "User_expand": expand_user,
                }
            }
        }
        # if userClass == '戊班':
        #     response_dict['prompt']['firstSimple']['speech'] = response.replace('⭐', '')
        #     print("response_dict['prompt']['firstSimple']['speech']",response_dict['prompt']['firstSimple']['speech'])

    else:
        if not Partner_expand:
            find_common = {'type': 'common_like'}
            find_result = myCommonList.find_one(find_common)
            # 判斷座號有無學生姓名
            if int(partner) in studentName_dic:
                partner_name = studentName_dic[int(partner)]
            else:
                partner_name = partner + "號"
            response = choice(find_result['content']).replace('你', partner_name)
            response_speech = response
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response_speech],
                        "text": [response],
                        "delay": [2],
                    },
                    "suggestions": [{"title": "喜歡"},
                                    {"title": "還好"},
                                    {"title": "不喜歡"}]
                },
                "session": {
                    "params": {
                        "User_expand": expand_user,
                        "Partner_expand": True,
                        "Partner_expand": partner
                    }
                }
            }
        else:
            response = ''
            suggest_like = False
            dialog_index = myDialogList.find().count()
            dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
            userSay = req['intent']['query']
            connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id,
                                req['scene']['name'])
            scene = 'feedback_2players'
            if userSay == '還好' or userSay == '普通':
                response = '這樣啊！那是為什麼呢？'
                suggest_like = False
            elif userSay == '喜歡':
                # 接續詢問使用者喜歡故事的原因
                find_common = {'type': 'common_like_response'}
                find_common2 = {'type': 'common_like_expand'}
                find_result = myCommonList.find_one(find_common)
                find_result2 = myCommonList.find_one(find_common2)
                response = choice(find_result['content']) + ' ' + choice(find_result2['content']).replace('你', '你們')
                suggest_like = True
                expressionP = 3
                expressionA = 1
            elif userSay == '不喜歡':
                find_common = {'type': 'common_like_F_expand'}
                find_result = myCommonList.find_one(find_common)
                response = choice(find_result['content']).replace('你', '你們')
                suggest_like = False
            else:
                scene = 'expand_2players'

            expand_user = False
            dialog_index = myDialogList.find().count()
            dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
            connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
            # response_dict = {"prompt": {
            #     "firstSimple": {
            #         "speech": response,
            #         "text": response
            #     }},
            #     "scene": {
            #         "next": {
            #             'name': scene
            #         }
            #     },
            #     "session": {
            #         "params": dict(User_sentiment=suggest_like,
            #                        User_state=state, User_expand=expand_user)}
            # }

            # 20210318 修改JSON格式
            response_dict = {
                "prompt": {
                    "firstSimple": {
                        "speech": [response],
                        "text": [response],
                        "delay": [2]
                    }
                },
                "session": {
                    "params": dict(User_sentiment=suggest_like,
                                   User_expand=expand_user,
                                   noIdea_count=noIdea_count,
                                   question_count=question_count,
                                   User_say_len=User_say_len,
                                   dialog_count=0,
                                   dialog_count_limit=2)
                },
                "scene": {
                    "next": {
                        'name': scene
                    }
                }
            }


    print(response)
    return response_dict

# 從資料庫中取資料做為機器人給予學生之回饋
def feedback_2players(req):
    print('scene: Feedback_2players')
    state = True
    userSay = req['intent']['query']
    player = req['user']['player']
    partner = req['user']['partner']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']
    userClass = req['session']['params']['User_class']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count = req['session']['params']['dialog_count']
    dialog_count_limit = req['session']['params']['dialog_count_limit']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myFeedback = nowBook['Feedback']
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # 記錄對話過程
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])
    find_common = {'type': 'common_feedback'}
    find_result = myCommonList.find_one(find_common)
    find_feedback_student = {'type': 'common_feedback_student'}
    result_feedback_student = myCommonList.find_one(find_feedback_student)
    suggest_like = req['session']['params']['User_sentiment']
    find_like = {'Sentiment': suggest_like}
    result_like = myFeedback.find(find_like)
    if result_like.count() == 0:
        response = '哦！原來是這樣啊！我了解了，'
    else:
        if result_like.count() > 2:
            choose_number = random.sample(range(0, result_like.count() - 1), 2)
            response = choice(find_result['content']) + " " + result_like[choose_number[0]]['Content']
            # response_tmp = choice(result_feedback_student['content']) + " " + result_like[choose_number[1]]['Content']
        elif result_like.count() == 2:
            response = choice(find_result['content']) + " " + result_like[0]['Content']
            # response_tmp = choice(result_feedback_student['content']) + " " + result_like[1]['Content']
        else:
            choose_number = 0
            response = choice(find_result['content']) + " " + result_like[choose_number]['Content']

    # 判斷座號有無學生姓名
    if int(partner) in studentName_dic:
        partner_name = studentName_dic[int(partner)]
    else:
        partner_name = partner + "號"
    response_tmp2 = '那輪到' + partner_name + '分享一下你對這本書的想法吧！'
    # response_list = [response, response_tmp, response_tmp2]
    response_list = [response,  response_tmp2]
    response_len = [len(response) / 2,  1]

    if dialog_count < dialog_count_limit:
        dialog_count += 1
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": response_list,
                    "text": response_list,
                    "delay": response_len
                }
            },
            "session": {
                "params": {
                    "noIdea_count": noIdea_count,
                    "question_count": question_count,
                    "User_say_len": User_say_len,
                    "dialog_count": dialog_count,
                    "dialog_count_limit": dialog_count_limit

                }
            },
            "scene": {
                "next": {
                    "name": "feedback_2players"
                }
            }
        }

    else:
        response = '你們都分享的很棒呢！'
        response_tmp2 = "最後關於這本書，還有什麼想分享的呢？"
        response_list = [response, response_tmp2]
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": response_list,
                    "text": response_list,
                    "delay": [len(response) / 2, 2]
                },

            },
            "session": {
                "params": {
                    "User_state": state,
                    "noIdea_count": noIdea_count,
                    "question_count": question_count,
                    "User_say_len": User_say_len,
                    "dialog_count": 0,
                    "dialog_count_limit": 3

                }
            },
            "scene": {
                "next": {
                    "name": "summarize_2players"
                }
            }
        }

    partner = userClass + partner
    response += response_tmp2
    connectDB.updateUser(myUserList, user_id, bookName, state, partner)
    # connectDB.addFeedback(myFeedback, user_id, suggest_like, userSay)
    # 記錄對話過程
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
    print(response)
    return response_dict


# 學生總結
def summarize_2players(req):
    print('scene: 書本總結')
    state = True
    userSay = req['intent']['query']
    player = req['user']['player']
    partner = req['user']['partner']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']
    userClass = req['session']['params']['User_class']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dialog_count = req['session']['params']['dialog_count']
    dialog_count_limit = req['session']['params']['dialog_count_limit']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]

    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # 記錄對話過程
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])

    # 判斷座號有無學生姓名
    if int(partner) in studentName_dic:
        partner_name = studentName_dic[int(partner)]
    else:
        partner_name = partner + "號"
    response = '輪到' + partner_name + '最後講講看你對這本書的想法吧！'
    if dialog_count < dialog_count_limit:
        if dialog_count == 1:
            res_moderator = random.choice(["OO你覺得XX說得如何？", "OO你覺得XX說得怎麼樣？說說你的想法吧！", 'OO說說你對XX講的想法吧！'])
            user_id_tmp = user_id.replace("戊班", "").replace("丁班", "")
            # 判斷座號有無學生姓名
            if int(user_id_tmp) in studentName_dic:
                name = studentName_dic[int(user_id_tmp)]
            else:
                name = user_id_tmp + "號"
            response = res_moderator.replace("XX", name).replace("OO", partner_name)
            

        elif dialog_count != 0:
            response = ""


        dialog_count += 1
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": [response],
                    "text": [response],
                    "delay": [2]
                }
            },
            "session": {
                "params": {
                    "noIdea_count": noIdea_count,
                    "question_count": question_count,
                    "User_say_len": User_say_len,
                    "dialog_count": dialog_count,
                    "dialog_count_limit": dialog_count_limit

                }
            },
            "scene": {
                "next": {
                    "name": "summarize_2players"
                }
            }
        }

    else:
        response = '哇！你們都說的真好！'
        response_tmp = '我可以推薦你們一些書，你們想看看嗎？'
        response_list = [response, response_tmp]
        response_dict = {
            "prompt": {
                "firstSimple": {
                    "speech": response_list,
                    "text": response_list,
                    "delay": [len(response) / 2]
                },
                "suggestions": [{'title': '好'}, {'title': '不用了'}]
            },
            "session": {
                "params": {
                    "User_state": state,
                    "noIdea_count": noIdea_count,
                    "question_count": question_count,
                    "User_say_len": User_say_len

                }
            },
            "scene": {
                "next": {
                    "name": "Check_suggestion"
                }
            }
        }
        response += response_tmp
    partner = userClass + partner
    connectDB.updateUser(myUserList, user_id, bookName, state, partner)
    # connectDB.addFeedback(myFeedback, user_id, suggest_like, userSay)
    # 記錄對話過程
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
    print(response)
    return response_dict


# 判斷是否進入推薦
def Check_suggestion(req):
    print('scene: Suggestion or not')
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    player = req['user']['player']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    userSay = req['intent']['query']
    player = req['user']['player']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']
    # 記錄對話過程
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])

    if userSay == '不用了':
        scene = 'exit_system'
        if player != 2:
            response = '好唷！謝謝你的分享！期待你下次的故事！Bye Bye！'
        else:
            response = '好唷！謝謝你們的分享！期待下次的故事！Bye Bye！'
    else:
        scene = 'suggestion'
        response = '好唷！沒問題！'

    # response_dict = {"prompt": {
    #     "firstSimple": {
    #         "speech": response,
    #         "text": response
    #     }},
    #     "scene": {
    #         "next": {
    #             'name': scene
    #         }
    #     }
    # }

    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response],
                "text": [response],
                "delay": [0],
                "expression": "happy"
            }
        },
        "session": {
            "params": {
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len

            }
        },
        "scene": {
            "next": {
                "name": scene
            }
        }
    }
    # 記錄對話過程
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
    print(response)
    return response_dict


# 依據學生喜好建議其他書籍
def suggestion(req):
    print("scene: Suggestion")
    connect()
    session_id = req['session']['id']
    suggest_like = req['session']['params']['User_sentiment']
    bookName = req['session']['params']['User_book']
    time = req['user']['lastSeenTime']
    player = req['user']['player']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    suggest_book = {}
    stop_words = list(stopwords.words('english'))
    for i in range(len(stop_words)):
        stop_words[i] = " " + stop_words[i] + " "
    stop_words.extend(['.', ',', '"', '!', "'s", '?'])
    # 與資料庫中其他書的內容作相似度比對
    sample_book = myBookList.find_one({'bookName': bookName.replace('_', ' ')})['story_content']
    comparison_book = myBookList.find({'bookName': {'$ne': bookName.replace('_', ' ')}})
    for word in stop_words:
        sample_book = sample_book.replace(word, ' ')
    story_content = ''
    for book in comparison_book:
        for word in stop_words:
            story_content = book['story_content'].replace(word, ' ')
        cosine = Cosine(2)
        p1 = cosine.get_profile(sample_book.replace('   ', ' ').replace('  ', ' '))
        p2 = cosine.get_profile(story_content.replace('   ', ' ').replace('  ', ' '))
        suggest_book[book['bookName']] = cosine.similarity_profiles(p1, p2)
    if suggest_like:
        # 學生喜歡則列出1本高相似度的書籍
        find_common = {'type': 'common_like_T'}
        find_result = myCommonList.find_one(find_common)
        sort_suggest_book = sorted(suggest_book.items(), key=lambda x: x[1], reverse=True)
    else:
        find_common = {'type': 'common_like_F'}
        find_result = myCommonList.find_one(find_common)
        sort_suggest_book = sorted(suggest_book.items(), key=lambda x: x[1], reverse=False)
    find_common_suggestion = {'type': 'common_suggestion_response'}
    find_suggestion = myCommonList.find_one(find_common_suggestion)
    response_suggestion_tmp = choice(find_suggestion['content'])
    response = choice(find_result['content']).replace('XX', sort_suggest_book[0][0]) + '\n'
    url = 'http://story.csie.ncu.edu.tw/storytelling/images/chatbot_books/' + sort_suggest_book[0][0].replace(' ',
                                                                                                              '%20').replace('\'','’') + '.jpg'
    print('URL:' + url)
    # response_dict = {"prompt": {
    #     "firstSimple": {
    #         "speech": response,
    #         "text": response
    #     },
    #     'suggestions': [{'title': '有興趣'}, {'title': '沒興趣'}],
    #     'content': {'image': {'url': url, 'alt': sort_suggest_book[0][0], 'height': 1, 'width': 1}}
    # },
    #     "scene": {
    #         "next": {
    #             'name': 'Check_input'
    #         }
    #     },
    #     'session': {
    #         'params':
    #             {'nowScene': 'Suggest', 'NextScene': 'Interest', 'suggest_book': sort_suggest_book[0:2]}
    #     }
    # }


    if player == 2:
        response = response.replace("你", "你們")
        response_suggestion_tmp = response_suggestion_tmp.replace("你", "你們")

    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": [response, response_suggestion_tmp],
                "text": [response, response_suggestion_tmp],
                "delay": [len(response) / 2, 1],
                "expression": "happy"
            },
            'suggestions': [{'title': '有興趣'}, {'title': '沒興趣'}],
            'content': {
                'image': {'url': url, 'alt': sort_suggest_book[0][0]}
            }
        },
        'session': {
            'params': {
                'nowScene': 'suggestion',
                'NextScene': 'Interest',
                'suggest_book': sort_suggest_book[0:2],
                "noIdea_count": noIdea_count,
                "question_count": question_count,
                "User_say_len": User_say_len
            }
        },
        "scene": {
            "next": {
                "name": 'check_input'
            }
        }
    }

    response += response_suggestion_tmp

    # 記錄對話
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
    print(response)
    return response_dict


def Interest(req):
    response = ""
    response_tmp = ""
    response_list = []
    response_speech_list = []
    delay_list = [2]
    userSay = req['session']['params']['User_say']
    sort_suggest_book = req['session']['params']['suggest_book']
    bookName = req['session']['params']['User_book']
    session_id = req['session']['id']
    time = req['user']['lastSeenTime']
    character = req['user']['character']
    noIdea_count = req['session']['params']['noIdea_count']
    question_count = req['session']['params']['question_count']
    User_say_len = req['session']['params']['User_say_len']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_').replace('.', '')
    nowBook = myClient[dbBookName]
    myDialogList = nowBook['S_R_Dialog']
    player = req['user']['player']
    if player != 2:
        user_id = req['session']['params']['User_id']
    else:
        user_id = req['user']['User_id']
    # 記錄對話過程
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])
    if userSay == '有興趣':
        for index in range(len(sort_suggest_book)):
            book_result = myBookList.find_one({'bookName': sort_suggest_book[index][0]})
            book_result_updated = connectDB.copy.deepcopy(book_result)
            if 'Interest' not in book_result_updated:
                book_result_updated.update({'Interest': 0})
            book_result_updated['Interest'] += 1
            myBookList.update_one(book_result, {'$set': book_result_updated})
    elif userSay == '沒興趣':
        print()

    expression = ""
    # 20210512 魚老師給評語
    if character == 'fish_teacher':
        if question_count > 0:
            response = '哇！這次有問單字很棒耶！👍 '
            response_speech = '哇！這次有問單字很棒耶！'
            response_list.append(response)
            response_speech_list.append(response_speech)
            delay_list = [len(response)/2, 2]

        # 分母不為零(都沒聊書)
        try:
            User_say_average = sum(User_say_len) / len(User_say_len)
            if User_say_average > 4 and len(User_say_len) > 3:
                response_tmp = '這次我們聊書聊得很多，謝謝你的分享！Bye Bye！'
                expression = "excited"
            elif User_say_average < 4 and noIdea_count == 0:
                response_tmp = '這次聊書聊得有點少喔，下次可以再跟我分享多一點！Bye Bye！'
                expression = "frightened"
            else:
                response_tmp = '我知道這次你看這本書內容不是很熟喔！下次加油！Bye Bye！'
                expression = "sad"
            response_list.append(response_tmp)
            response_speech_list.append(response_tmp)
            # User_say_average < 5 and noIdea_count > 0
        except ZeroDivisionError:
            response_tmp = '我知道你這次都沒有聊書喔！下次多聊一點加油！Bye Bye！'
            response_list.append(response_tmp)
            response_speech_list.append(response_tmp)
    else:
        response_tmp = '我知道了！那謝謝你的分享！期待你下次的故事！Bye Bye！'
        response_list.append(response_tmp)
        response_speech_list.append(response_tmp)

    if player == 2:
        for i in range(len(response_list)):
            response_speech_list[i] = response_speech_list[i].replace('你', '你們')
            response_list[i] = response_list[i].replace('你', '你們')


    # 20210318 修改JSON格式
    response_dict = {
        "prompt": {
            "firstSimple": {
                "speech": response_speech_list,
                "text": response_list,
                "delay": delay_list,
                "expression": expression
            }
        },
        "scene": {
            "next": {
                "name": "exit_system"
            }
        }
    }

    response += response_tmp
    # 記錄對話
    dialog_index = myDialogList.find().count()
    dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    return response_dict


def exit_system(req):
    print("scene: Exit")
    if 'User_id' in req['session']['params'].keys() and 'User_book' in req['session']['params'].keys():
        player = req['user']['player']
        if player != 2:
            user_id = req['session']['params']['User_id']
            connectDB.updateUser(myUserList, user_id, req['session']['params']['User_book'],
                                 req['session']['params']['User_state'], "None")
        else:
            user_id = req['user']['User_id']
            partner = req['user']['partner']
            userClass = req['session']['params']['User_class']
            partner = userClass + partner
            connectDB.updateUser(myUserList, user_id, req['session']['params']['User_book'],
                                 req['session']['params']['User_state'], partner)
            connectDB.updateUser(myUserList, partner, req['session']['params']['User_book'],
                                 req['session']['params']['User_state'], user_id)


