# -*- coding:utf-8 -*-
"""
@author: xinquan
@file: data_process.py
@time: 2021/10/25 13:49
@desc: 数据样本处理模块
"""
import json
import os
import warnings

import pandas as pd

warnings.filterwarnings('ignore')  # 忽略一些警告,可以删除
root_path = os.path.split(os.path.realpath(__file__))[0]  # 获取该脚本的地址,有效避免Linux和Windows文件路径格式不一致等问题,可以删除

base_date_path = r'/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/THUCNews/data_witsky_11'
origin_pd_path = os.path.join(base_date_path, "all_test_7.xlsx")

stop_word_map = {
    'A:': 0,
    'B:': 0,
    "你好": 0,
    "喂": 0,
    '?': 0,
    '，': 0,
    "。": 0,
    "啊": 0,
    "哎": 0,
    "您好": 0
}

"""第三级函数"""


def stop_word(input_txt: str):
    """
    第三级函数:去停用词
    """
    for one_word in stop_word_map:
        if one_word in input_txt:
            input_txt = input_txt.replace(one_word, '')
    return input_txt


def adjust_chat(chat_list):
    """
    第三级函数:转换格式
    """
    result_str = ""
    role_dict = {0: "A", 1: "B"}
    if chat_list is None:
        return ""

    for one_chat_info in chat_list:
        one_role = role_dict[one_chat_info["channel_id"]]
        one_txt = one_chat_info["text"]
        format_txt = "{0}:{1}\n".format(one_role, one_txt)
        result_str += format_txt
    return result_str


"""功能函数"""


def func_adjust_chat():
    """
    功能函数:将原始格式的对话数据,转换成查看方便的格式
    """

    one_pd = pd.read_excel(r'/Users/zhuxinquan/Desktop/诚智天扬/data/mqi_aqc_report_字段调整.xlsx', keep_default_na=False)

    full_words_list = list(one_pd['full_words'])
    result_list = []
    for one_full_words in full_words_list:
        print(type(one_full_words), one_full_words)
        try:
            one_full_words = json.loads(one_full_words)
        except:
            one_full_words = ""
        # one_full_words = one_full_words
        one_full_words = adjust_chat(one_full_words)
        result_list.append(one_full_words)

    one_pd["chat_adj"] = result_list
    one_pd.to_excel(r'/Users/zhuxinquan/Desktop/诚智天扬/data/mqi_aqc_report_字段调整_step1.xlsx', index=False)


def func_adjust_ChatTxt(input_txt: str, input_items: str, limit_num: int):
    """
    功能函数:将对话数据,清洗去干扰项,并转换成预料
    """
    input_txt_list = input_txt.split('\n')
    if len(input_txt_list) <= 1:
        return input_txt.strip()
    input_txt_list = list(filter(lambda x: len(x.strip()) > limit_num, input_txt_list))
    input_txt_list = list(map(lambda x: stop_word(x), input_txt_list))
    result_txt = ''.join(input_txt_list)
    if len(result_txt) < limit_num:
        input_items = input_items.replace("A:", "").replace("B:", "").replace("\t", '').replace("\n", '')
        return input_items
    return result_txt


"""模块函数"""


def module_make_sample():
    """
    模块函数:将整理的excel文件数据,转换成可以放入模型的txt文件
    """
    fwrite_train = open(os.path.join(base_date_path, 'train.txt'), 'w')
    fwrite_dev = open(os.path.join(base_date_path, 'dev.txt'), 'w')
    fwrite_test = open(os.path.join(base_date_path, 'test.txt'), 'w')
    origin_pd_path = r'/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/' \
                     r'THUCNews/data_witsky_11/all_test_11_6.xlsx'
    data_pd = pd.read_excel(origin_pd_path, keep_default_na=False)

    result_list = []
    for t_index, t_value in data_pd.iterrows():
        t_chat_adj = t_value['chat_adj']
        t_item = t_value['item_sample']
        sample_txt = func_adjust_ChatTxt(t_chat_adj, t_item, 5)
        sample_txt = "{}\t{}\n".format(sample_txt, t_value['label'])
        # sample_txt = "{}".format(sample_txt)
        print(sample_txt.strip())
        result_list.append(sample_txt)
    data_pd["item_sample"] = result_list

    train_list = data_pd[data_pd['kind'] == 'train']['item_sample']
    dev_list = data_pd[data_pd['kind'] == 'train']['item_sample']
    test_list = data_pd[data_pd['kind'] == 'train']['item_sample']

    fwrite_train.writelines(train_list)
    fwrite_dev.writelines(dev_list)
    fwrite_test.writelines(test_list)

    fwrite_train.close()
    fwrite_dev.close()
    fwrite_test.close()
    data_pd.to_excel(
        r'/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/THUCNews/data_witsky_11/all_test_11_7.xlsx',
        index=False)


def model_normalization():
    """
        模块函数:去重
    """
    base_pd = pd.read_excel(
        r'/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/THUCNews/data_witsky_11/all_test_11_6.xlsx',
        keep_default_na=False)
    target_pd = pd.read_excel(r'/Users/zhuxinquan/Desktop/已完成数据/数据整理/外卖—step1.xlsx',
                              keep_default_na=False)

    target_type = 'item_sample'
    base_list = list(base_pd[target_type])
    base_list = list(set(base_list))
    base_list = list(map(lambda x: str(x).split("\t")[0], base_list))
    print(base_list)
    base_map = {t_k: t_v for t_k, t_v in zip(base_list, range(len(base_list)))}
    target_list = list(target_pd[target_type])
    result_list = []
    print(len(target_list))
    amount_len = len(target_list)
    count_num = 0
    for one_item in target_list:
        print("{}/{}".format(amount_len, count_num))
        if one_item in base_map:
            result_list.append(1)
        else:
            result_list.append(0)
        count_num += 1
    target_pd['normalization'] = result_list
    target_pd.to_excel(r'/Users/zhuxinquan/Desktop/已完成数据/数据整理/外卖—step2.xlsx', index=False)


def model_clean():
    origin_pd_path = r'/Users/zhuxinquan/Desktop/已完成数据/外卖.xlsx'
    data_pd = pd.read_excel(origin_pd_path, keep_default_na=False)

    result_list = []
    for t_index, t_value in data_pd.iterrows():
        t_chat_adj = t_value['chat_adj']
        t_item = t_value['chat_adj']
        sample_txt = func_adjust_ChatTxt(t_chat_adj, t_item, 5)
        # sample_txt = "{}".format(sample_txt)
        print(sample_txt.strip())
        result_list.append(sample_txt)
    data_pd["item_sample"] = result_list
    data_pd.to_excel(
        r'/Users/zhuxinquan/Desktop/已完成数据/数据整理/外卖—step1.xlsx',
        index=False)


"""临时模块"""


def temp_1():
    """
    临时数据处理
    """
    fopen = open(r'/Users/zhuxinquan/Desktop/陕西/20211026/recordcheck.txt', 'r', encoding='utf-8')
    all_lines = fopen.readlines()
    chat_adj_list = []
    item_sample_list = []
    for oneline in all_lines:
        oneline = oneline.strip()
        oneline_list = eval(oneline)
        target_list = eval(oneline_list[11])

        t_chat_adj = adjust_chat(target_list)
        sample_txt = func_adjust_ChatTxt(t_chat_adj, t_chat_adj, 5)
        sample_txt = "{}".format(sample_txt)

        chat_adj_list.append(t_chat_adj)
        item_sample_list.append(sample_txt)
    re_pd = pd.DataFrame({"chat_adj": chat_adj_list,
                          "item_sample": item_sample_list
                          })
    re_pd.to_excel("shanxi_aqc.xlsx", index=False)


def temp_2():
    """
    临时数据处理
    """
    fopen = open(r'/Users/zhuxinquan/Desktop/aqc_record_20211028.txt', 'r', encoding='utf-8')
    all_lines = fopen.readlines()
    chat_adj_list = []
    item_sample_list = []
    for oneline in all_lines:
        oneline = oneline.strip()
        print(oneline)
        try:
            oneline_list = eval(oneline)
        except:
            print(oneline)
            continue
        target_list = eval(oneline_list[11])
        t_chat_adj = adjust_chat(target_list)
        print(t_chat_adj)
        sample_txt = func_adjust_ChatTxt(t_chat_adj, t_chat_adj, 5)
        print(sample_txt)
        print()

        chat_adj_list.append(t_chat_adj)
        item_sample_list.append(sample_txt)
    re_pd = pd.DataFrame({"chat_adj": chat_adj_list,
                          "item_sample": item_sample_list
                          })
    re_pd.to_excel("shanxi_aqc_1.xlsx", index=False)


if __name__ == '__main__':
    module_make_sample()
    # model_normalization()
    # func_adjust_chat()
    # model_clean()
    # temp_2()
    pass
