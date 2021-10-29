# -*- coding:utf-8 -*-
"""
@author: xinquan
@file: make_one.py
@time: 2021/8/12 0:34
@desc: 
"""
import os
import warnings

warnings.filterwarnings('ignore')  # 忽略一些警告,可以删除
root_path = os.path.split(os.path.realpath(__file__))[0]  # 获取该脚本的地址,有效避免Linux和Windows文件路径格式不一致等问题,可以删除

import time
import torch
import numpy as np
import pickle as pkl
from tqdm import tqdm
from datetime import timedelta
from sklearn import metrics
import torch.nn.functional as F

MAX_VOCAB_SIZE = 10000  # 词表长度限制
UNK, PAD = '<UNK>', '<PAD>'  # 未知字，padding符号


def get_time_dif(start_time):
    """获取已使用时间"""
    end_time = time.time()
    time_dif = end_time - start_time
    return timedelta(seconds=int(round(time_dif)))


from models import TextCNN


def build_vocab(file_path, tokenizer, max_size, min_freq):
    vocab_dic = {}
    with open(file_path, 'r', encoding='UTF-8') as f:
        for line in tqdm(f):
            lin = line.strip()
            if not lin:
                continue
            content = lin.split('\t')[0]
            for word in tokenizer(content):
                vocab_dic[word] = vocab_dic.get(word, 0) + 1
        vocab_list = sorted([_ for _ in vocab_dic.items() if _[1] >= min_freq], key=lambda x: x[1], reverse=True)[
                     :max_size]
        vocab_dic = {word_count[0]: idx for idx, word_count in enumerate(vocab_list)}
        vocab_dic.update({UNK: len(vocab_dic), PAD: len(vocab_dic) + 1})
    return vocab_dic


vocab_path = r'/Users/zhuxinquan/Desktop/project_witsky/Text-Classification-pytorch/THUCNews/data_witsky/vocab.pkl'
train_path = r'/Users/zhuxinquan/Desktop/project_witsky/Text-Classification-pytorch/THUCNews/data_witsky/train.txt'
pad_size = 32
dev_path = r'/Users/zhuxinquan/Desktop/project_witsky/Text-Classification-pytorch/THUCNews/data_witsky/dev.txt'
test_path = r'/Users/zhuxinquan/Desktop/project_witsky/Text-Classification-pytorch/THUCNews/data_witsky/test.txt'


def build_dataset():
    tokenizer = lambda x: [y for y in x]  # char-level

    if os.path.exists(vocab_path):
        vocab = pkl.load(open(vocab_path, 'rb'))
    else:
        vocab = build_vocab(train_path, tokenizer=tokenizer, max_size=MAX_VOCAB_SIZE, min_freq=1)
        pkl.dump(vocab, open(vocab_path, 'wb'))
    print(f"Vocab size: {len(vocab)}")

    def load_dataset(path, pad_size=32):
        contents = []
        with open(path, 'r', encoding='UTF-8') as f:
            for line in tqdm(f):
                lin = line.strip()
                if not lin:
                    continue
                content, label = lin.split('\t')
                words_line = []
                token = tokenizer(content)
                seq_len = len(token)
                if pad_size:
                    if len(token) < pad_size:
                        token.extend([PAD] * (pad_size - len(token)))
                    else:
                        token = token[:pad_size]
                        seq_len = pad_size
                # word to id
                for word in token:
                    words_line.append(vocab.get(word, vocab.get(UNK)))
                contents.append((words_line, int(label), seq_len))
        return contents  # [([...], 0), ([...], 1), ...]

    train = load_dataset(train_path, pad_size)
    dev = load_dataset(dev_path, pad_size)
    test = load_dataset(test_path, pad_size)
    return vocab, train, dev, test


def test(test_iter):
    # test
    embedding = 'embedding_SougouNews.npz'
    config = TextCNN.Config(dataset='THUCNews', embedding=embedding)
    model = TextCNN.Model(config).to('cpu')
    model.load_state_dict(
        torch.load(
            r'/Users/zhuxinquan/Desktop/project_witsky/Text-Classification-pytorch/THUCNews/saved_dict/TextCNN_witsky.ckpt',
            map_location=lambda storage, loc: storage)
    )
    model.eval()
    start_time = time.time()

    test_acc, test_loss, test_report, test_confusion = evaluate(model, test_iter, test=True)
    msg = 'Test Loss: {0:>5.2},  Test Acc: {1:>6.2%}'
    print(msg.format(test_loss, test_acc))
    print("Precision, Recall and F1-Score...")
    print(test_report)
    print("Confusion Matrix...")
    print(test_confusion)
    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)


def evaluate(model, data_iter, test=False):
    model.eval()
    loss_total = 0
    predict_all = np.array([], dtype=int)
    labels_all = np.array([], dtype=int)
    with torch.no_grad():
        for texts, labels in data_iter:
            outputs = model(texts)
            loss = F.cross_entropy(outputs, labels)
            loss_total += loss
            labels = labels.data.cpu().numpy()
            predic = torch.max(outputs.data, 1)[1].cpu().numpy()
            labels_all = np.append(labels_all, labels)
            predict_all = np.append(predict_all, predic)
    acc = metrics.accuracy_score(labels_all, predict_all)
    if test:
        report = metrics.classification_report(labels_all, predict_all, target_names=
        ['教育', '商业'],
                                               digits=4)
        confusion = metrics.confusion_matrix(labels_all, predict_all)
        return acc, loss_total / len(data_iter), report, confusion
    return acc, loss_total / len(data_iter)


def show_bert():
    from pytorch_pretrained_bert import BertTokenizer, BertModel
    bert_tokenizer = BertTokenizer.from_pretrained(r'/Volumes/zxq/数据/model_bert/chinese_wwm_pytorch')
    a = "我是祝鑫泉"
    a_tokens = bert_tokenizer.tokenize(a)
    print(a_tokens)
    a_seq_ids = bert_tokenizer.convert_tokens_to_ids(a_tokens)
    print(a_seq_ids)

    bert_model = BertModel.from_pretrained(r'/Volumes/zxq/数据/model_bert/chinese_wwm_pytorch').to(
        'cuda')
    batch_data = torch.Tensor(a_seq_ids).cuda(0).long().view((1, -1))
    out, _ = bert_model(batch_data)
    print(out[0])
    print(np.shape(out[0]))


if __name__ == '__main__':
    from utils import DatasetIterater, get_time_dif

    vocab, train_data, dev_data, test_data = build_dataset()
    test_iter = DatasetIterater(test_data, 128, torch.device('cuda' if torch.cuda.is_available() else 'cpu'))
    test(test_iter)
    # show_bert()
