import json
import requests
import pymongo

# Google翻譯
import googletrans
from googletrans import Translator
translator = Translator()

def get_squadAnswer(question, localServer):
    # print(' >>>>> Start "Player Ask then Robot Answer" Conversation! <<<<<')

    # 本機
    if(localServer):
        resp = requests.post("http://127.0.0.1:4220/squad",
                            data={"question": question})  # 要跟inference.py設的一樣
    # 有顯卡那台
    else:
        resp = requests.post("http://140.115.53.220:4220/squad",
                            data={"question": question})  # 要跟inference.py設的一樣

    # response放的是SQuAD生成的答案
    response = resp.json()

    
    
    return response