#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time        : 2022/9/5 14:19
# @Author      : Luyao.zhang
# @File        : predict_layout_jack.py
# @Description :

import os
import cv2
from paddleocr import PPStructure,save_structure_res

table_engine = PPStructure(table=False, ocr=False, show_log=True)

save_folder = './output'
img_path = '/Users/jack/Desktop/jack_code/PaddleOCR-2.5/data/test_imgs/5.TIF'
img = cv2.imread(img_path)
result = table_engine(img)
save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])

for line in result:
    line.pop('img')
    print(line)