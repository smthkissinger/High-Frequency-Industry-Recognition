# -*- coding:utf-8 -*-
"""
@author: xinquan
@file: data_collection.py
@time: 2021/10/14 14:28
@desc: 
"""
import glob
import json
import os
import pickle
import warnings
from multiprocessing import Pool

import pandas as pd

warnings.filterwarnings('ignore')  # 忽略一些警告,可以删除
root_path = os.path.split(os.path.realpath(__file__))[0]  # 获取该脚本的地址,有效避免Linux和Windows文件路径格式不一致等问题,可以删除
from ali_nlp_api_special import ali_getSceneByWord

origin_data_path = r"/Users/zhuxinquan/Desktop/step1_data/loans.xlsx"
result_data_path = r"/Users/zhuxinquan/Desktop/project_witsky/data_make/tmp"


class data_read_write():
    def data_read(self, filename):
        fopen = open(filename, 'rb')
        mydata = pickle.load(fopen)
        return mydata

    def data_write(self, filename, mydata):
        fopen = open(filename, 'wb')
        pickle.dump(mydata, fopen)
        fopen.close()


def collect_loans_filled():
    """
    贷款数据的补全
    :return:
    """
    data_pd = pd.read_excel(r"/Users/zhuxinquan/Desktop/step2_data/promotion_result.xlsx",
                            keep_default_na=False)

    all_res_test = []
    all_result_industry = []
    all_result_scene = []

    len_data_pd = len(data_pd)
    filled_num = 0
    for t_index, t_value in data_pd.iterrows():

        words_result = t_value["words_result"]
        all = t_value["all"]
        industry = str(t_value["industry"]).strip()
        scene = str(t_value["scene"]).strip()
        if len(scene) == 0:
            try:
                res_test, result_industry, result_scene = ali_getSceneByWord(words_result)
            except:
                res_test = ""
                result_industry = ""
                result_scene = ""
            print(t_index, len_data_pd, filled_num)
            filled_num += 1
            all_res_test.append(res_test)
            all_result_industry.append(result_industry)
            all_result_scene.append(result_scene)
        else:
            print(t_index, len_data_pd)
            all_res_test.append(all)
            all_result_industry.append(industry)
            all_result_scene.append(scene)

    data_pd["all"] = all_res_test
    data_pd["industry"] = all_result_industry
    data_pd["scene"] = all_result_scene
    data_pd.to_excel('promotion_result_filled.xlsx', index=False)


def collect_tg(data_pd, travel_num):
    """
    商品推广
    :return:
    """
    len_data_pd = len(data_pd)
    target_list = list(data_pd['words_result'])

    all_res_test = []
    all_result_industry = []
    all_result_scene = []
    count_num = 0
    for one_txt_index in target_list:
        one_txt = one_txt_index
        try:
            res_test, result_industry, result_scene = ali_getSceneByWord(one_txt)
            # print("{}_{}/{}".format(travel_num, len_data_pd, count_num))
            count_num += 1
        except:
            res_test = ""
            result_industry = ""
            result_scene = ""
        all_res_test.append(res_test)
        all_result_industry.append(result_industry)
        all_result_scene.append(result_scene)
    data_pd["all"] = all_res_test
    data_pd["industry"] = all_result_industry
    data_pd["scene"] = all_result_scene
    data_pd.to_excel(result_data_path + r'/商品推广数据_{}.xlsx'.format(travel_num), index=False)
    print("finish_{}".format(travel_num))


def cut_pd(listTemp, n):
    result_list = []
    for i in range(0, len(listTemp), n):
        result_list.append(listTemp[i:i + n])
    return result_list


def merge_pd():
    import glob
    all_path = glob.glob(result_data_path + r"/*.xlsx")
    result_list = []
    for one_path in all_path:
        tmp_pd = pd.read_excel(one_path, keep_default_na=False)
        result_list.append(tmp_pd)
    result_pd = pd.concat(result_list)
    result_pd = result_pd.sort_values(by='id', ascending=True)
    result_pd.to_excel("loans_result.xlsx", index=False)


# step1
def collect_tg_muli():
    # 切割文件
    data_path = origin_data_path
    data_pd = pd.read_excel(data_path, keep_default_na=False)
    list_pd = cut_pd(data_pd, 30)
    print(len(list_pd))
    pool = Pool(4)
    travel_num = 0
    for one_pd in list_pd:
        pool.apply_async(collect_tg, (one_pd, travel_num,))
        # collect_tg(one_pd, travel_num)
        travel_num += 1
    pool.close()  # 关闭进程池，关闭后po不再接受新的请求
    pool.join()
    merge_pd()
    print('task_finish')


# step2
def merge_create_tee_industry():
    import glob
    data_path = r'/Users/zhuxinquan/Desktop/step2_data/*.xlsx'
    data_path = glob.glob(data_path)
    print(data_path)

    # create tree:{INDUSTRY:SCENE}
    industry_dict = {}
    for one_path in data_path:
        print(one_path)
        tmp_pd = pd.read_excel(one_path, keep_default_na=False)
        tmp_pd = tmp_pd[["industry", "scene"]]
        tmp_pd = tmp_pd.drop_duplicates(
            subset=['industry', 'scene'],  # 去重列，按这些列进行去重
            keep='first'  # 保存第一条重复数据
        )

        industry_list = list(tmp_pd["industry"])
        scene_list = list(tmp_pd["scene"])
        for tmp_index in range(len(industry_list)):
            tmp_industry = industry_list[tmp_index]
            tmp_scene = scene_list[tmp_index]
            if tmp_industry in industry_dict:
                if tmp_scene not in industry_dict[tmp_industry]:
                    industry_dict[tmp_industry].append(tmp_scene)
            else:
                industry_dict[tmp_industry] = [tmp_scene]
    print(industry_dict)
    print("*" * 89)
    import pprint
    pprint.pprint(industry_dict)


def mkdir(path):
    folder = os.path.exists(path)

    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
        print("---  new folder...  ---")
        print("---  OK  ---")
    else:
        print("---  There is this folder!  ---")


def make_file():
    industry_dict = {
        '商品推广': ['购物中心', '食品生鲜类', '家电类', '宠物类', '洗护用品', '其他商品', '综合服饰', 'POS机', '日用百货类', '软件销售', '母婴用品', '智能硬件', '床品类',
                 '专业设备', '五金工具', '饰品类', '数码配件/电子产品', '园艺类', '保健品、营养品', '办公用品及耗材', '酒水', '家庭清洁'], '': [''],
        '互联网行业': ['电商平台', '云服务', '网络推广', '通用互联网服务', '新零售', '办公软件服务', '搜索排名服务', '网站制作'], '无行业': ['无行业'],
        '其他行业': ['其他行业'], '安装维修回收服务': ['安装维修回收服务'],
        '汽车行业': ['车辆买卖', '车辆配件及用品', '其他汽车服务', '汽车保养维修', '二手车买卖', '车辆代理', '加油/充电'], '旅游行业': ['旅行服务'],
        '教育行业': ['其他行业培训', '少儿教育', '艺术体育培训', '外语培训', '会计类培训', '课外辅导培优', '成人教育', '金融类培训', '学校教育', '幼儿园', '医学教育', '商业课程'],
        '运输行业': ['货运/快递物流', '海运', '客运服务'],
        '医疗行业': ['医疗整形', '美容会所', '医疗平台', '养老院或组织', '医疗保健服务', '医院', '口腔医疗', '宠物医院', '药店&医药公司', '第三方体检/检测机构', '其他医疗服务',
                 '医疗器械'], '房产行业': ['装修/设计', '家私/家居', '房地产商', '地产中介', '建材相关', '二手房买卖', '其他房地产相关'],
        '企业服务': ['招投标信息服务', '其他企业服务', '商标/财务/工商代理', '法律服务', '公司/资质办理转让', '办公设备租赁', '策划'],
        '文化行业': ['音像制品服务', '短视频服务', '影视传媒公司', '影视视频服务'],
        '金融行业': ['金融贷款', '金融催缴', '股票', '银行', '其他金融', '投资理财', '信用卡', '基金', '证券', '彩票', '融资', '承兑汇票'], '外卖配送': ['外卖配送'],
        '招商加盟': ['招商加盟'], '通讯行业': ['运营商', '运营商代理'], '市政单位': ['政府', '事业单位'], '游戏行业': ['线上游戏'], '家政行业': ['家政服务'],
        '保险行业': ['车险', '其他保险', '医疗/健康保险', '人寿保险', '社保', '意外伤害保险', '家庭财产保险', '企业财产险', '理财保险'], '人力资源': ['人力资源'],
        '休闲生活娱乐': ['其他生活娱乐', '瑜伽', '健身'], '会展营销': ['家装/家居/设计展', '汽车展', '其他行业展'], '安防行业': ['安防/消防服务'],
        '婚庆服务': ['婚庆摄影', '婚介公司', '婚礼策划公司'], '广告行业': ['广告/印刷服务'], '票务服务': ['票务服务'], '移民行业': ['留学移民', '移民中介'],
        '环保行业': ['环保服务']}
    industry_list = list(industry_dict.keys())
    industry_list = list(filter(lambda x: len(x) > 0, industry_list))
    print(industry_list)
    base_path = r'/Users/zhuxinquan/Desktop/step3_data'
    for one_industry in industry_list:
        print(os.path.join(base_path, one_industry))
        tmp_path = os.path.join(base_path, one_industry)
        mkdir(tmp_path)


def to_dump(input_dict: dict):
    output_path = r"/Users/zhuxinquan/Desktop/step3_data"
    for one_dict in input_dict:
        try:
            print(one_dict, input_dict[one_dict]["count"], len(input_dict[one_dict]["data_pd"]))
        except:
            print(input_dict[one_dict])
            continue
        industry_path = os.path.join(output_path, "{}.xlsx".format(one_dict))
        industry_pd = input_dict[one_dict]["data_pd"]
        industry_pd.to_excel(industry_path, index=False)


# step3
def merge_scene():
    industry_dict = {
        '商品推广': ['购物中心', '食品生鲜类', '家电类', '宠物类', '洗护用品', '其他商品', '综合服饰', 'POS机', '日用百货类', '软件销售', '母婴用品', '智能硬件', '床品类',
                 '专业设备', '五金工具', '饰品类', '数码配件/电子产品', '园艺类', '保健品、营养品', '办公用品及耗材', '酒水', '家庭清洁'], '': [''],
        '互联网行业': ['电商平台', '云服务', '网络推广', '通用互联网服务', '新零售', '办公软件服务', '搜索排名服务', '网站制作'], '无行业': ['无行业'],
        '其他行业': ['其他行业'], '安装维修回收服务': ['安装维修回收服务'],
        '汽车行业': ['车辆买卖', '车辆配件及用品', '其他汽车服务', '汽车保养维修', '二手车买卖', '车辆代理', '加油/充电'], '旅游行业': ['旅行服务'],
        '教育行业': ['其他行业培训', '少儿教育', '艺术体育培训', '外语培训', '会计类培训', '课外辅导培优', '成人教育', '金融类培训', '学校教育', '幼儿园', '医学教育', '商业课程'],
        '运输行业': ['货运/快递物流', '海运', '客运服务'],
        '医疗行业': ['医疗整形', '美容会所', '医疗平台', '养老院或组织', '医疗保健服务', '医院', '口腔医疗', '宠物医院', '药店&医药公司', '第三方体检/检测机构', '其他医疗服务',
                 '医疗器械'], '房产行业': ['装修/设计', '家私/家居', '房地产商', '地产中介', '建材相关', '二手房买卖', '其他房地产相关'],
        '企业服务': ['招投标信息服务', '其他企业服务', '商标/财务/工商代理', '法律服务', '公司/资质办理转让', '办公设备租赁', '策划'],
        '文化行业': ['音像制品服务', '短视频服务', '影视传媒公司', '影视视频服务'],
        '金融行业': ['金融贷款', '金融催缴', '股票', '银行', '其他金融', '投资理财', '信用卡', '基金', '证券', '彩票', '融资', '承兑汇票'], '外卖配送': ['外卖配送'],
        '招商加盟': ['招商加盟'], '通讯行业': ['运营商', '运营商代理'], '市政单位': ['政府', '事业单位'], '游戏行业': ['线上游戏'], '家政行业': ['家政服务'],
        '保险行业': ['车险', '其他保险', '医疗/健康保险', '人寿保险', '社保', '意外伤害保险', '家庭财产保险', '企业财产险', '理财保险'], '人力资源': ['人力资源'],
        '休闲生活娱乐': ['其他生活娱乐', '瑜伽', '健身'], '会展营销': ['家装/家居/设计展', '汽车展', '其他行业展'], '安防行业': ['安防/消防服务'],
        '婚庆服务': ['婚庆摄影', '婚介公司', '婚礼策划公司'], '广告行业': ['广告/印刷服务'], '票务服务': ['票务服务'], '移民行业': ['留学移民', '移民中介'],
        '环保行业': ['环保服务']}
    scene_dict = {}
    for one_ind in industry_dict:
        scene_dict[one_ind] = {"industry": one_ind, "count": 0}
    print(scene_dict)

    # 遍历文件夹
    all_target_data = glob.glob("/Users/zhuxinquan/Desktop/step2_data/*.xlsx")
    for one_target_path in all_target_data:
        target_data = pd.read_excel(one_target_path, keep_default_na=False)

        industry_list = list(target_data["industry"])
        industry_list = list(set(industry_list))
        industry_list = list(filter(lambda x: len(x) > 0, industry_list))
        print(one_target_path)
        print(industry_list)
        for one_scene in industry_list:
            tmp_pd = target_data[target_data['industry'] == one_scene]
            if len(tmp_pd) == 0:
                continue
            if scene_dict[one_scene]['count'] == 0:
                scene_dict[one_scene]["data_pd"] = tmp_pd
                scene_dict[one_scene]["count"] += 1
            else:
                origin_pd = scene_dict[one_scene]["data_pd"]
                origin_pd = pd.concat([tmp_pd, origin_pd])
                scene_dict[one_scene]["data_pd"] = origin_pd
                scene_dict[one_scene]["count"] += 1

        # import pprint
        # pprint.pprint(scene_dict)
        # exit("pass")
    to_dump(scene_dict)
    # exit("pass")
    # import pprint
    # pprint.pprint(scene_dict)


# step4
def adjust_mark():
    # base_data = pd.read_excel(r"/Users/zhuxinquan/Desktop/step2_data/loans_result.xlsx", keep_default_na=False)
    # mark_list = base_data.columns.values.tolist()
    output_base_path = r"/Users/zhuxinquan/Desktop/step3_data_1"

    mark_order_list = ['id', 'words_result', 'words_result_origin', 'tag_name', 'tag_type', 'keywords', 'full_words',
                       'all', 'industry', 'scene']
    all_path = glob.glob(r"/Users/zhuxinquan/Desktop/step3_data/*.xlsx")
    for one_path in all_path:
        one_titile = one_path.split("/")[-1]
        print(one_path, one_titile)
        one_pd = pd.read_excel(one_path, keep_default_na=False)
        try:
            one_pd = one_pd[mark_order_list]
            one_pd = one_pd.sort_values(by='id', ascending=True)
            print(len(one_pd))
            one_pd.drop_duplicates(subset=mark_order_list, keep='first', inplace=True)
            print(len(one_pd))
        except:
            print("error:{}".format(one_titile))
            continue
        one_pd.to_excel(os.path.join(output_base_path, one_titile), index=False)


def statistics_data():
    industry_scene_dict = {'教育行业': '少儿教育/学科类课外辅导', '商品推广': '好评返现/商场活动/游戏推广', '金融行业': '金融行业/互联网金融/银行金融', '房产行业': '房产销售',
                           '运输行业': '快递/外卖', '市政单位': '冒充公检法/落户'}

    kind_name_list = []
    kind_count_list = []
    scene_list = []
    ali_scene_list = []

    output_base_path = r"/Users/zhuxinquan/Desktop/step4_data/*.xlsx"
    all_path = glob.glob(output_base_path)
    for one_path in all_path:
        print(one_path)
        one_kind = one_path.split("/")[-1].replace(".xlsx", "")
        one_pd = pd.read_excel(one_path, keep_default_na=False)

        one_scene_list = list(one_pd["scene"])
        one_scene_list = list(set(one_scene_list))
        one_scene_str = "/".join(one_scene_list)

        one_count = len(one_pd)
        kind_name_list.append(one_kind)
        kind_count_list.append(one_count)
        scene_list.append(industry_scene_dict[one_kind])
        ali_scene_list.append(one_scene_str)

    result_pd = pd.DataFrame(
        {"industry": kind_name_list, 'kind_count': kind_count_list, 'scene': scene_list, 'ali_scene': ali_scene_list})
    result_pd.to_excel("高频数据统计.xlsx", index=False)


# step5->file:step3_data
def func_adjust_chat(chat_list):
    result_str = ""
    role_dict = {0: "A", 1: "B"}
    for one_chat_info in chat_list:
        one_role = role_dict[one_chat_info["channel_id"]]
        one_txt = one_chat_info["text"]
        format_txt = "{0}:{1}\n".format(one_role, one_txt)
        result_str += format_txt
    return result_str


def adjust_chat():
    one_pd = pd.read_excel(r'/Users/zhuxinquan/Desktop/project_witsky/data_make/其他.xlsx', keep_default_na=False)

    full_words_list = list(one_pd['full_words'])
    result_list = []
    for one_full_words in full_words_list:
        print(type(one_full_words), one_full_words)
        try:
            one_full_words = json.loads(one_full_words)
        except:
            one_full_words = ""
        # one_full_words = one_full_words
        one_full_words = func_adjust_chat(one_full_words)
        result_list.append(one_full_words)

    one_pd["chat_adj"] = result_list
    one_pd.to_excel(r'/Users/zhuxinquan/Desktop/已完成数据/迭代/其他.xlsx', index=False)


def get_sample():
    mydata = pd.read_excel(r'/Users/zhuxinquan/Desktop/已完成数据/迭代/其他_all.xlsx', keep_default_na=False)
    print(len(mydata))
    # mydata = mydata[(mydata["scene"] == "外语培训") | (mydata["scene"] == "课外辅导培优") | (mydata["scene"] == "学校教育")]
    # print(len(mydata))
    mydata_sample = mydata.sample(n=10000, random_state=1)
    print(len(mydata_sample))
    mydata_sample.to_excel(r'/Users/zhuxinquan/Desktop/已完成数据/迭代/其他_sample.xlsx', index=False)


def get_data_othors():
    all_path_list = glob.glob("/Users/zhuxinquan/Desktop/step3_data/*.xlsx")
    use_industry_list = ['房产行业', '教育行业', '金融行业', '商品推广', '市政单位', '外卖配送', '运输行业']
    print(len(all_path_list))
    all_path_list = list(filter(lambda x: x.split("/")[-1].replace(".xlsx", "") not in use_industry_list, all_path_list))

    result_pd_list = []
    for one_path in all_path_list:
        print(one_path)
        one_pd = pd.read_excel(one_path, keep_default_na=False)
        one_pd = one_pd[['words_result', "words_result_origin", "full_words", "industry", 'scene']]
        result_pd_list.append(one_pd)
    result_pd = pd.concat(result_pd_list)
    result_pd.to_excel("其他.xlsx", index=False)




if __name__ == '__main__':
    # collect_tg_muli()
    # collect_loans_filled()
    # merge_create_tee_industry()
    # make_file()
    # merge_scene()
    # collect_loans_filled()
    # adjust_mark()
    # statistics_data()
    # adjust_chat()
    get_sample()
    # get_data_othors()
