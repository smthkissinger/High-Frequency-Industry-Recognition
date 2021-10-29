#!/bin/bash
nohup python -u run.py --model TextCNN >> ./logs/TextCNN.log 2>&1 &
#nohup python -u run.py --model TextRNN >> ./logs/TextRNN.log 2>&1 &
#nohup python -u run.py --model TextRNN_Att >> ./logs/TextRNN_Att.log 2>&1 &
#nohup python -u run.py --model TextRCNN >> ./logs/TextRCNN.log 2>&1 &
#nohup python -u run.py --model FastText --embedding random >> ./logs/FastText.log 2>&1 &
#nohup python -u run.py --model DPCNN >> ./logs/DPCNN.log 2>&1 &
#nohup python -u run.py --model Transformer >> ./logs/Transformer.log 2>&1 &
