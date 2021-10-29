# -*- coding:utf-8 -*-
"""
@author: xinquan
@file: check_model.py
@time: 2021/10/22 10:08
@desc: 
"""
import os
import pickle as pkl
import warnings

import pandas as pd
import torch
import torch.nn.functional as F

from models import TextCNN

warnings.filterwarnings('ignore')  # 忽略一些警告,可以删除
from config.config import config
from utils import DatasetIterater


UNK, PAD = '<UNK>', '<PAD>'  # 未知字，padding符号


class CheckModel(object):
    def __init__(self):
        self.vocab_path = os.path.join(config.data_path, 'vocab_13.pkl')
        self.train_path = os.path.join(config.data_path, 'train.txt')
        self.pad_size = 152
        self.dev_path = os.path.join(config.data_path, 'dev.txt')
        self.test_path = os.path.join(config.data_path, 'test.txt')
        self.model_path = os.path.join(config.model_path, r'TextCNN_witsky_13.ckpt')
        self.stop_word_map = {
            'A:': 0,
            'B:': 0,
            "你好": 0,
            "喂": 0,
            '?': 0,
            '，': 0,
            "。": 0,
            "啊": 0,
            "哎": 0,
            "您好": 0,
            '、': 0
        }
        self.tokenizer = lambda x: [y for y in x]
        self.vocab = pkl.load(open(self.vocab_path, 'rb'))
        self.class_dict = self.get_class_dict()

    @staticmethod
    def get_class_dict():
        class_path = os.path.join(config.data_path, 'class.txt')
        fopen = open(class_path, 'r')
        index_num = 0
        class_dict = {}
        for one_line in fopen.readlines():
            one_line = one_line.strip()
            class_dict[str(index_num)] = one_line
            index_num += 1
        return class_dict

    def decode_text(self, content_list):
        contents = []
        for line in content_list:
            lin = line.strip()
            print('lin:', lin)
            if not lin:
                continue
            label = 0
            words_line = []
            token = self.tokenizer(lin)

            seq_len = len(token)
            if self.pad_size:
                if len(token) < self.pad_size:
                    token.extend([PAD] * (self.pad_size - len(token)))
                else:
                    token = token[:self.pad_size]
                    seq_len = self.pad_size
            # word to id
            for word in token:
                words_line.append(self.vocab.get(word, self.vocab.get(UNK)))
            contents.append((words_line, int(label), seq_len))
        return contents

    def evaluate(self, model, data_iter):
        model.eval()
        loss_total = 0
        reuslt_list = []
        task_amount = len(data_iter)
        task_num = 0
        with torch.no_grad():
            for texts, labels in data_iter:
                outputs = model(texts)
                loss = F.cross_entropy(outputs, labels)
                loss_total += loss
                predic = torch.max(outputs.data, 1)[1].cpu().numpy()
                predic_items = list(map(lambda x: self.class_dict[str(x)], predic))
                reuslt_list.extend(predic_items)
                print("{}/{}".format(task_amount, task_num))
                task_num += 1
        return reuslt_list

    def get_label(self, content_list: list):
        one_code_list = self.decode_text(content_list)
        test_iter = DatasetIterater(one_code_list, 256, torch.device('cuda' if torch.cuda.is_available() else 'cpu'))

        embedding = 'embedding_SougouNews.npz'
        config_model = TextCNN.Config(dataset='data_witsky', embedding=embedding)
        model = TextCNN.Model(config_model).to('cpu')
        model.load_state_dict(
            torch.load(
                self.model_path,
                map_location=lambda storage, loc: storage)
        )
        model.eval()
        predic_items = self.evaluate(model, test_iter)
        return predic_items

    def stop_word(self, input_txt: str):
        for one_word in self.stop_word_map:
            if one_word in input_txt:
                input_txt = input_txt.replace(one_word, '')
        return input_txt

    def func_get_txt(self, input_txt: str, input_items: str, limit_num: int):
        input_txt_list = input_txt.split('\n')
        if len(input_txt_list) <= 1:
            return input_txt.strip()
        input_txt_list = list(filter(lambda x: len(x.strip()) > limit_num, input_txt_list))
        input_txt_list = list(map(lambda x: self.stop_word(x), input_txt_list))
        result_txt = ''.join(input_txt_list)
        if len(result_txt) < limit_num:
            return input_items
        return result_txt

    def get_label_pd(self):
        data_pd = pd.read_excel(
            r"/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/data_witsky/data_witsky_11/all_test_11_7.xlsx",
            keep_default_na=False)
        items_list = list(data_pd['chat_adj'])
        chat_adj_list = list(data_pd['chat_adj'])
        # 对话数据拆分清洗
        items_list = list(map(lambda x, y: self.func_get_txt(x, y, 5), chat_adj_list, items_list))

        # 清洗
        items_list = list(
            map(lambda x: x.strip().replace('\t1', '').replace('\t2', '').replace('\t3', '').replace('\t4', ''),
                items_list))
        result_items_list = self.get_label(items_list)

        data_pd['item_sample'] = items_list
        data_pd['result_items_12'] = result_items_list
        data_pd.to_excel(
            r"/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/data_witsky/data_witsky_11/all_test_12.xlsx",
            index=False)


if __name__ == '__main__':
    import time

    t_start = time.time()
    cm = CheckModel()
    # predic_items = cm.get_label([
    #     '师傅我在那个碧景园就是小区对面你你的定位是准确的吧在那里网商贷了100米好好好嗯好不',
    #     '高德打车我已经到了对2分钟2分钟',
    #     '你那里贷款也做吗？征信不好没有社保这些的这您不管什么情况呢？呃查询有点多有几个再加上网贷还在还用完了是一天'
    # ])
    # print(predic_items)
    cm.get_label_pd()
    print("消耗时间是:{}".format(time.time() - t_start))

"""
你车在哪呢？我就把你定位那个苏丽处理宾馆吗？我们门口是没有呀我要按你那导航过来这这一个中国建设银行你知道吗？
嗯对你往前能再早一点贷贷款难懂一点是吧嗯在我全都再走一点


"""
