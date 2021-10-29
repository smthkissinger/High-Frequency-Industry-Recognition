# -*- coding:utf-8 -*-
"""
@author: xinquan
@file: mapper.py
@time: 2021/10/29 16:40
@desc: 
"""
import os
import warnings

from config.config import config_base

warnings.filterwarnings('ignore')  # 忽略一些警告,可以删除
root_path = os.path.split(os.path.realpath(__file__))[0]  # 获取该脚本的地址,有效避免Linux和Windows文件路径格式不一致等问题,可以删除


class Mapping(object):
    def __init__(self):
        super(Mapping, self).__init__()

        self.word_mapping = {}

    def load_data(self):
        pass


if __name__ == '__main__':
    mapping = Mapping()

