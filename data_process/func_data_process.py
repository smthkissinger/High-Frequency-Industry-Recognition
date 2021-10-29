# -*- coding:utf-8 -*-
"""
@author: xinquan
@file: func_data_process.py
@time: 2021/10/25 13:35
@desc: 
"""
import os
import glob
import warnings

import pandas as pd

warnings.filterwarnings('ignore')  # 忽略一些警告,可以删除
root_path = os.path.split(os.path.realpath(__file__))[0]  # 获取该脚本的地址,有效避免Linux和Windows文件路径格式不一致等问题,可以删除


def func_filled():
    """
    填充某个字段
    :return:
    """
    all_path = glob.glob(r"/Users/zhuxinquan/Desktop/已完成数据/迭代/*.xlsx")
    target_map = {}
    for one_path in all_path:
        print(one_path)
        one_pd = pd.read_excel(one_path, keep_default_na=False)
        one_pd = one_pd[['words_result', 'chat_adj']]
        tmp_words_result = one_pd['words_result']
        tmp_chat_adj = one_pd['chat_adj']
        for t_key, t_value in zip(tmp_words_result, tmp_chat_adj):
            target_map[t_key] = t_value

    print(len(target_map))
    base_pd = pd.read_excel(r'/Users/zhuxinquan/Desktop/project_witsky/Text-Classification-pytorch/data_witsky/data_witsky_2/all_test_2.xlsx',
                            keep_default_na=False)
    target_list = list(base_pd["items"])
    result_list = []
    for one in target_list:
        if one in target_map:
            result_list.append(target_map[one])
        else:
            result_list.append("")
    base_pd['chat_adj'] = result_list
    base_pd.to_excel(r"/Users/zhuxinquan/Desktop/project_witsky/Text-Classification-pytorch/data_witsky/data_witsky_2/all_test_3.xlsx",
                     index=False)


if __name__ == '__main__':
    func_filled()

