import json
import requests
import pymongo

def get_squadBook(book, localServer):
    # print(' >>>>> Start "Player Ask then Robot Answer" Conversation! <<<<<')

    # 本機
    if(localServer):
        resp = requests.post("http://127.0.0.1:4220/squad_getBook",
                            data={"book": book})  # 要跟inference.py設的一樣
    # 有顯卡那台
    else:
        resp = requests.post("http://140.115.53.220:4220/squad_getBook",
                            data={"book": book})  # 要跟inference.py設的一樣

    # response的內容會是true或false，代表是否成功比對到書名
    response = resp.json()

    
    
    return response