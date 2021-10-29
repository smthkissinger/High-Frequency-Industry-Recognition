# -*- coding:utf-8 -*-
"""
@author: xinquan
@file: ali_nlp_api.py
@time: 2021/9/26 16:46
@desc: 
"""
import os
import warnings

warnings.filterwarnings('ignore')  # 忽略一些警告,可以删除
root_path = os.path.split(os.path.realpath(__file__))[0]  # 获取该脚本的地址,有效避免Linux和Windows文件路径格式不一致等问题,可以删除
import requests
import json
import pprint


config_ip = '192.168.150.186:8321'
config_ip_local = '192.168.110.70:8080'


# 行业识别
def ali_getSceneByWord(input_word: str):
    config_url = 'http://'+config_ip+'/getSceneByWord'
    data = {
        "requestid": "111111",
        "msgs": [
            {
                "role": "0",
                "words": input_word
            }
        ]
    }
    data_json = json.dumps(data)
    res = requests.post(url=config_url, headers={"Content-Type": "application/json"}, data=data_json)
    res_test = res.text
    res_test = json.loads(res_test)
    result_industry = res_test["data"]["result"][0]["industry"]
    result_scene = res_test["data"]["result"][0]["scene"]
    return res_test, result_industry, result_scene


# 风险识别
def ali_getRiskTx(input_word: str):
    config_url = 'http://'+config_ip+'/getRiskTx'
    data = {
        "requestid": "111111",
        "msgs": [
            {
                "role": "0",
                "words": input_word
            }
        ]
    }
    data_json = json.dumps(data)
    res = requests.post(url=config_url, headers={"Content-Type": "application/json"}, data=data_json)
    res_test = res.text
    res_test = json.loads(res_test)
    try:
        res_risk = json.loads(res_test["data"]["predictResult"])
    except:
        print(input_word)
        return '', '无风险'
    res_risk = res_risk['result'][0]["label"]
    return res_test, res_risk


# 诈骗识别
def ali_getFraud(input_word: str):
    config_url = 'http://'+config_ip+'/getFraud'
    data = {
        "requestid": "111111",
        "msgs": [
            {
                "role": "0",
                "words": input_word
            }
        ]
    }
    data_json = json.dumps(data)
    res = requests.post(url=config_url, headers={"Content-Type": "application/json"}, data=data_json)
    res_test = res.text
    res_test = json.loads(res_test)
    res_swindle = json.loads(res_test['data']['predictResult'])
    res_swindle = res_swindle["result"]
    return res_test, res_swindle


if __name__ == '__main__':
    res_test, result_industry, result_scene = ali_getSceneByWord("我说。你在哪。喂。在哪里。喂。你在哪里，你的定位有些不对。我在陪我在北广场，这里。北广场地下停车库。在广场。我进不来的那个地方。喂。喂。喂。我在北广场地下停车库。我说地下停。我下不来的是我们的网约车，不能下来的。我这是我在上户口上面出口。上面出口你")
    print(res_test, result_industry, result_scene)
    # ali_getRiskTx("喂。啊。嗯，你那里有没有那个一氧化二氮呢？。1582打你。你养花哥的。嗯。消息啊。啊。没有没有。嗯好。嗯")
    # ali_getFraud()
