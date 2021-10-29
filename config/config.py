# -*- coding:utf-8 -*-
"""
@author: xinquan
@file: config.py
@time: 2021/10/22 10:10
@desc: 
"""
import os
import time
import warnings
from datetime import timedelta

warnings.filterwarnings('ignore')  # 忽略一些警告,可以删除
root_path = os.path.split(os.path.realpath(__file__))[0]  # 获取该脚本的地址,有效避免Linux和Windows文件路径格式不一致等问题,可以删除


class Config(object):
    def __init__(self):
        self.base_path = root_path.replace("/config", "")  # 项目的根目录
        self.model_path = os.path.join(self.base_path, 'THUCNews/saved_dict')
        self.data_path = os.path.join(self.base_path, 'THUCNews/data_witsky_11')


config = Config()
