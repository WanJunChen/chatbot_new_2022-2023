from random import choice
from nltk.corpus import stopwords
from strsimpy.cosine import Cosine
from googletrans import Translator
from nltk.corpus import wordnet
import pymongo
import connectDB
import random
import nltk
from googletrans import Translator
# from emotfidf import EmoTFIDF
# import text2emotion as te
# from openpyxl import load_workbook
import pandas as pd


myClient: object
myBotData: object
myBookList: object
myCommonList: object
myUserList: object
list1 = ['Prompt_character', 'Prompt_action', 'Prompt_dialog', 'Prompt_event']


def test():
    # 本文，大意是歐巴馬卸任
    news_content = ''' "Kip and Tip went to the wood.\n Tip said, \"I am a very brave fox. Are you brave, too, Kip?\"\n Kip said, \"I am a very brave fox, too.\"\n They saw a log.\n Tip said, \"Can you jump over the log? I can!\"\n Tip jumped over the log.\n Kip looked at the log.\n He could not jump over the log.\n \"You are not a very brave fox,\" said Tip.\n Tip and Kip saw a tree in the wood.\n \"Can you jump up the tree?\" said Tip. \n \"I can!\"\n Tip jumped up the tree.\n \"You jump up the tree, too, Kip!\" he said.\n Kip looked at the tree.\n He could not jump up the tree.\n Tip said, \"You are not a very brave fox, Kip.\"\n Tip and Kip went a little way in the wood.\n They saw a pond.\n They saw some rocks in the pond.\n Tip said, \"Can you jump on the rocks, Kip? I can. I am a brave fox!\"\n Tip jumped on the rocks.\n Tip went into the water!\n \"Help me, Kip!\" he said.\n \"I can help you!\" said Kip.\n Kip jumped into the water.\n He helped Tip.\n \"You are a very brave fox, Kip,\" said Tip.\n \"You helped me!\"\n Kip was glad he could help Tip. Tip was glad, too!"'''
    sentence_list = news_content.split('\n')

    stopwords = nltk.corpus.stopwords.words('english')
    word_frequencies = {}
    for word in nltk.word_tokenize(news_content):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequncy = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word] / maximum_frequncy)

    sentence_scores = {}
    for sent in sentence_list:
        print(sent)
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30 and '"' not in sent and 'said' not in sent and 'says' not in sent and 'asks' not in sent:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    import heapq
    summary_sentences = heapq.nlargest(6, sentence_scores, key=sentence_scores.get)
    # summary = ' '.join(summary_sentences)
    summary = ""
    # 根据原文中的句子顺序显示最上面的句子
    for sentence in sentence_list:
        if sentence in summary_sentences and sentence not in summary:
            # print(sentence)
            summary += sentence
    print(summary)
    translator = Translator()
    sentence_Translate = translator.translate(summary, src="en", dest="zh-TW").text
    print(sentence_Translate)

def Prompt_event(req):
    find_common = {'type': 'common_Prompt_action'}
    find_common_result = myCommonList.find_one(find_common)
    response = choice(find_common_result['content'])
    response_len = []

    # session_id = req['session']['id']
    # time = req['user']['lastSeenTime']
    bookName = 'Max Has A Fish'
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']
    myMaterialList = nowBook['MaterialTable']

    # 計數器 -> 跳到結束scene
    dialog_count = 5
    # sentence_id 抓取 20210429
    sentence_id = [1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0]

    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本動作
    response_tmp = ''
    # for verb in find_material_result['Main_Verb']:

    # 20210429



    while True:

        result = list(myVerbList.find({'C1': random.choice(find_material_result['Character']), 'Verb': find_material_result['Main_Verb'][0] }))

        if len(result):
            result = random.choice(result)
            print("主要腳色與動作",result)
            result_sentence_id = result['Sentence_Id']
            print(result_sentence_id)

        else:
            # 找主要腳色句子
            result = list(myVerbList.find({'C1': random.choice(find_material_result['Character'])}))
            print("主要腳色",result)
            if len(result):
                result = random.choice(result)
                result_sentence_id = result['Sentence_Id']
                print(result['Sentence_translate'])
                print(result_sentence_id)
            else:
                # 找主要動詞句子
                result = random.choice(list(myVerbList.find({'Verb': find_material_result['Main_Verb'][0]})))
                result_sentence_id = result['Sentence_Id']
                print("主要動作",result)
                print(result_sentence_id)
                if 'C1' not in result:
                    result = random.choice(list(myVerbList.find()))
                    result_sentence_id = result['Sentence_Id']
                    print("隨機依據", result)
                    print(result_sentence_id)

        print("len",len(list(myVerbList.find())))

        if result_sentence_id not in sentence_id:
            break
        else:
            try:
                result = random.choice(list(myVerbList.find({"Sentence_Id" : choice([i for i in range(0,len(list(myVerbList.find()))) if i not in sentence_id])})))
                result_sentence_id = result['Sentence_Id']
                print("排除重複", result)
                print(result_sentence_id)
                break
            except IndexError:
                print("強制到下個階段")
                break


    # if response_tmp != '':
    #     response_tmp += '，還有'
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
    # connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    # 20210318 修改JSON格式
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
                "NowScene": "Prompt_event",
                "NextScene": "Prompt_response"
            }
        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    print(response)
    response_dict['prompt'].update({'sentence_id': sentence_id,'dialog_count': dialog_count+1})
    return response_dict


Prompt_task_list = ['Time', 'Location', 'Affection', 'Life']


def Prompt_character_sentiment(req):
    print('角色引導')
    # find_common = {'type': 'common_Prompt_character'}
    # find_common_result = myCommonList.find_one(find_common)
    # response = choice(find_common_result['content'])
    response = "我最喜歡XX"
    response_len = []


    bookName = 'Max Has A Fish'
    # dialog_count = req['session']['params']['dialog_count']
    # sentence_id = req['session']['params']['sentence_id']
    # noIdea_count = req['session']['params']['noIdea_count']
    # question_count = req['session']['params']['question_count']
    # User_say_len = req['session']['params']['User_say_len']

    # player = req['user']['player']
    # if player == 2:
    #     user_dialog_count = req['session']['params']['user_dialog_count']
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_')
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

    # 20211005
    # 找主要角色句子
    similarity_sentence = {}
    translator = Translator()
    try:
        result = random.choice(list(myVerbList.find({'C1': "a fish" })))['Sentence_translate']
        result_sentence_id = result['Sentence_Id']
        print(result_sentence_id)
        print(result)
        print("主要角色", result)

    except IndexError:

        all_cursor = myVerbList.find()

        # 使用相似度比對
        for cursor in all_cursor:

            cosine = Cosine(2)
            s1 = 'a fish'
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
        print(similarity_sentence.keys())
        if len(similarity_sentence.keys()):
            result_sentence_id = random.sample(similarity_sentence.keys(), 1)[0]
            result = myVerbList.find({"Sentence_Id": result_sentence_id})[0]['Sentence_translate']
            print(result_sentence_id)
            print(result)






    response_tmp = '那你們最喜歡誰呢？'
    response_len = [len(response) / 2, 1]
    response_list = [response, response_tmp]
    response += response_tmp


    # 記錄對話
    # myDialogList = nowBook['S_R_Dialog']
    # dialog_index = myDialogList.find().count()
    # dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    # dialog_count += 1

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

def Prompt_character_experience(req):
    print('角色經驗引導')

    find_common = {'type': 'common_Prompt_character_experience'}
    find_common_result = myCommonList.find_one(find_common)
    response = choice(find_common_result['content'])


    bookName = 'Max Has A Fish'

    sentence_id = [1,2,3]



    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']


    # 列出提示句子中上次出現角色
    response_tmp = myVerbList.find_one({'Sentence_Id': sentence_id[-1]})['C1']

    print(response_tmp)
    response = response.replace("XX", response_tmp[0])

    # # 記錄對話
    # myDialogList = nowBook['S_R_Dialog']
    # dialog_index = myDialogList.find().count()
    # dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])



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
                "NowScene": "Prompt_experence",
                "NextScene": "Prompt_response",

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

def Prompt_action_thinking(req):
    print('動詞引導')
    # find_common = {'type': 'common_Prompt_action'}
    # find_common_result = myCommonList.find_one(find_common)
    # response = choice(find_common_result['content'])

    response_len = []

    # session_id = req['session']['id']
    # time = req['user']['lastSeenTime']
    bookName = 'Max Has A Fish'
    # dialog_count = req['session']['params']['dialog_count']
    # sentence_id = req['session']['params']['sentence_id']
    # noIdea_count = req['session']['params']['noIdea_count']
    # question_count = req['session']['params']['question_count']
    # User_say_len = req['session']['params']['User_say_len']
    # player = req['user']['player']
    # if player == 2:
    #     user_dialog_count = req['session']['params']['user_dialog_count']

    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_')
    nowBook = myClient[dbBookName]
    myVerbList = nowBook['VerbTable']
    myMaterialList = nowBook['MaterialTable']
    # 搜尋書本素材
    find_material_result = myMaterialList.find_one({})
    # 列出書本動作
    response_tmp = ''
    translator = Translator()
    word_Translate = translator.translate(find_material_result['Main_Verb'][0], src="en", dest="zh-TW").text
    response = "我知道" + find_material_result['Main_Verb'][0] + "是" + word_Translate + "的意思，像是書裡提到"

    # 抓主要動作 -> 需要判斷有沒有主詞
    while True:
        result = random.choice(list(myVerbList.find({'Verb': find_material_result['Main_Verb'][0]})))
        result_sentence_id = result['Sentence_Id']
        print("result", result)
        if 'C1' in result:
            response += result['Sentence_translate']
            break

    # if response_tmp != '':
    #     response_tmp += '，還有'
    # response_tmp += result['Sentence_translate']
    for word in ['。', '！', '：']:
        response_tmp = response_tmp.replace(word, ' ')
    response = response.replace('XX', response_tmp)

    response_tmp = '那你們覺得' + + '？'
    response_list = [response, response_tmp]
    response_len = [len(response) / 2, 1]
    response += response_tmp
    # 記錄對話
    # myDialogList = nowBook['S_R_Dialog']
    # dialog_index = myDialogList.find().count()
    # dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
    #
    # sentence_id.append(result_sentence_id)
    # dialog_count += 1

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


def Question(req):
    # userSay = req['session']['params']['User_say']
    # bookName = req['session']['params']['User_book']
    # session_id = req['session']['id']
    # time = req['user']['lastSeenTime']
    # dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_')
    # nowBook = myClient[dbBookName]
    # myDialogList = nowBook['S_R_Dialog']
    # user_id = req['session']['params']['User_id']
    # 記錄對話過程
    # dialog_index = myDialogList.find().count()
    # dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])

    userSay = "我想問it is a good day!"
    userSay = userSay.replace("我想問", "")
    translator = Translator()
    sentence_Translate = translator.translate(userSay, src="en", dest="zh-TW").text
    response = "我知道這個意思是 " + sentence_Translate
    print(sentence_Translate)

    # 記錄對話
    # dialog_index = myDialogList.find().count()
    # dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])
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

    # 20210318 修改JSON格式
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
    return response_dict


def connect():
    global myClient, myBotData, myBookList, myCommonList, myUserList
    try:
        # myClient = pymongo.MongoClient("mongodb://root:ltlab35316@140.115.53.196:27017/")
        myClient = pymongo.MongoClient("mongodb://localhost:27017/")
        myBotData = myClient.Chatbot
        myBookList = myBotData.bookList
        myCommonList = myBotData.commonList
        myUserList = myBotData.UserTable
    except Exception as e:
        print(e)

    return myBookList, myCommonList, myClient, myUserList

def Real(req):
    global Prompt_task_list
    random.shuffle(Prompt_task_list)
    user_say = "魚"
    # find_common = {'type': 'common_Prompt_action'}
    # find_common_result = myCommonList.find_one(find_common)
    # response = choice(find_common_result['content'])
    # response_len = []

    # session_id = req['session']['id']
    # time = req['user']['lastSeenTime']
    bookName = 'Max Has A Fish'
    dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_')
    nowBook = myClient[dbBookName]
    # myVerbList = nowBook['VerbTable']
    myDialogList = nowBook['S_R_Dialog']
    # 搜尋對話素材

    # dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_')
    # nowBook = myClient[dbBookName]
    # myDialogList = nowBook['S_R_Dialog']
    # user_id = req['session']['params']['User_id']
    #
    # dialog_index = myDialogList.find().count()
    # dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id']

    # find_common = {'type': 'common_nonsense'}
    find_result = list(myDialogList.find({"$and": [{"Speaker_id": {'$ne': 'chatbot'}}, {"Speaker_id": {'$ne': 'Chatbot'}}, {'Content': {"$regex": "^.{5,}$"}}]}))
    if not len(find_result):
        print("error")
    else:
        print("find")
    print(find_result)

    # 取學生對話最相似句子
    similarity_sentence = {}
    for dialog in find_result:
        cosine = Cosine(2)
        p1 = cosine.get_profile(user_say)
        p2 = cosine.get_profile(dialog['Content'])
        if p1 == {}:
            # 避免輸入字串太短
            break
        else:
            value = cosine.similarity_profiles(p1, p2)
            similarity_sentence[dialog['Content']] = value

    similarity_sentence = sorted(similarity_sentence.items(), key=lambda x: x[1], reverse=True)
    print('similarity_sentence：' + str(similarity_sentence))

    print(len(similarity_sentence))
    if len(similarity_sentence):
        response = str(similarity_sentence[0][0])
    else:
        response = random.choice(find_result)['Content']
    print(response)
    #
    # bookName = req['session']['params']['User_book']
    # dbBookName = bookName.replace("'", "").replace('!', '').replace(",", "").replace(' ', '_')
    # nowBook = myClient[dbBookName]
    # myMaterialList = nowBook['MaterialTable']
    # # 搜尋書本素材
    # find_material_result = myMaterialList.find_one({})
    # # 列出書本角色
    # response_tmp = choice(find_material_result['Character'])
    # response = response.replace('XX', response_tmp)
    #
    # # 記錄對話過程
    # dialog_id += 1
    # connectDB.addDialog(myDialogList, dialog_id, 'Student ' + user_id, userSay, time, session_id, req['scene']['name'])
    #
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


        },
        "scene": {
            "next": {
                'name': 'check_input'
            }
        }
    }
    #
    # # 記錄對話
    # dialog_index = myDialogList.find().count()
    # dialog_id = myDialogList.find()[dialog_index - 1]['Dialog_id'] + 1
    # connectDB.addDialog(myDialogList, dialog_id, 'chatbot', response, time, session_id, req['scene']['name'])

    return response_dict
def test_random():


    random.shuffle(list1)

    print("list:", list1)
    list1.pop(0)
    list1.pop(0)
    list1.pop(0)
    list1.pop(0)

    print(list1)

    if not list1:
        print("no")
    else:
        print("yes")

    ch_list = [66, 105, 110, 103, 111, 32, 104, 104, 104]
    for character in ch_list:
        print(chr(character), end="")

if __name__ == "__main__":


    # comment = "Dan opens up his diamond store."
    # emTFIDF = EmoTFIDF()
    #
    # emTFIDF.set_text(comment)
    # print(emTFIDF.em_frequencies)
    # text = "Dan opens up his diamond store."
    # print(te.get_emotion(text))
    connect()
    req = "{'handler': {'name': 'Prompt_action'}, 'intent': {'params': {}, 'query': ''}, 'scene': {'name': 'Prompt_action'}, 'session': {'id': '0p5ndhm67n03rbjyb0gd8g5hbltkbl', 'params': {'NextScene': 'Prompt_response', 'User_class': '戊班', 'User_say': 'too cool', 'User_id': '戊班88', 'next_level': False, 'User_first_match': False, 'User_temp_bookList': {'1': 'TOO COOL'}, 'User_book': 'TOO COOL', 'NowScene': 'Prompt_character'}}, 'user': {'lastSeenTime': '2021-04-28 17:24:08'}}"
    # Prompt_action(req)
    # Question(req)
    # Prompt_response(req)
    # Prompt_task(req)
    # Real(req)
    # Prompt_character_experience(req)

    df = pd.read_excel('student.xlsx', sheet_name="丁班")
    studentName_dic = df.set_index('座號')['姓名'].to_dict()
    if 1 in studentName_dic:
        print(studentName_dic[1])

