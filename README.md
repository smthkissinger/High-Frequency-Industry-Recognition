# High-Frequency-Industry-Recognition

## 介绍

## 环境
python 3.7  
pytorch 1.1  
tqdm  
sklearn  
tensorboardX

## 中文数据集

数据集|数据量
--|--
训练集|18万
验证集|1万
测试集|1万


### 更换自己的数据集
 - 如果用字，按照我数据集的格式来格式化你的数据。  
 - 如果用词，提前分好词，词之间用空格隔开，`python run.py --model TextCNN --word True`  
 - 使用预训练词向量：utils.py的main函数可以提取词表对应的预训练词向量。  


## 效果

