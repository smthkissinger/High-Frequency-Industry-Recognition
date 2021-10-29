# -*- coding:utf-8 -*-
"""
@author: xinquan
@file: Data_Process.py
@time: 2021/10/20 18:46
@desc: 
"""
import os
import warnings
import pandas as pd
import random

warnings.filterwarnings('ignore')  # 忽略一些警告,可以删除
current_path = os.path.split(os.path.realpath(__file__))[0]  # 获取该脚本的地址,有效避免Linux和Windows文件路径格式不一致等问题,可以删除
base_path = current_path.replace("data_process", "")


class Data_Process(object):
    def __init__(self):
        self.baseData_path = r'/Users/zhuxinquan/Desktop/已完成数据/迭代'

    def process_data_get_mark(self, target_file: str, target_mark: str):
        target_file_path = os.path.join(self.baseData_path, "{}.xlsx".format(target_file))
        print(target_file_path)
        target_pd = pd.read_excel(target_file_path, keep_default_na=False)
        # target_pd = target_pd.sample(n=5000, random_state=1)

        target_list = list(target_pd[target_mark])
        target_list = list(map(lambda x: str(x).strip() + "\t{}\n".format('1'), target_list))

        output_path = os.path.join(base_path, 'data_2', "{}.txt".format("其他"))
        fwrite = open(output_path, 'w')
        fwrite.writelines(target_list)
        fwrite.close()

    @staticmethod
    def get_train_dev_test(input_file: str, output_fie: str):

        # merge_txt
        merge_path = r'/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/data_2'
        merge_file = ["交通", '其他', '商品', '金融']
        all_lines = []
        for one_txt in merge_file:
            one_path = os.path.join(merge_path, "{}.txt".format(one_txt))
            one_file = open(one_path, 'r')
            one_lines = one_file.readlines()
            one_lines = list(map(lambda x: str(x).strip() + "\n", one_lines))
            print(len(one_lines))
            all_lines.extend(one_lines)
        print(len(all_lines))
        fwrite = open(r'/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/data_2/all.txt', 'w')
        fwrite.writelines(all_lines)
        fwrite.close()


        # fopen = open(input_file, 'r')
        # all_lines = fopen.readlines()
        random.shuffle(all_lines)
        train_list = []
        dev_list = []
        test_list = []

        for num_index in range(len(all_lines)):
            one_line = all_lines[num_index]
            mark_num = num_index % 10
            if mark_num == 0:
                test_list.append(one_line)
            elif mark_num <= 2:
                dev_list.append(one_line)
            else:
                train_list.append(one_line)

        fwrite_train = open(os.path.join(output_fie, 'train.txt'), 'w')
        fwrite_train.writelines(train_list)
        fwrite_dev = open(os.path.join(output_fie, 'dev.txt'), 'w')
        fwrite_dev.writelines(dev_list)
        fwrite_test = open(os.path.join(output_fie, 'test.txt'), 'w')
        fwrite_test.writelines(test_list)


if __name__ == '__main__':
    dp = Data_Process()
    # dp.process_data_get_mark('其他_sample', 'words_result')
    dp.get_train_dev_test('/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/data/all.txt',
                            "/Users/zhuxinquan/Desktop/project_witsky/High-Frequency-Industry-Recognition/data_2")