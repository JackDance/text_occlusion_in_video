#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time        : 2022/9/5 14:24
# @Author      : Luyao.zhang
# @File        : predict_layout_jack1.py
# @Description :
import cv2
import layoutparser as lp
image = cv2.imread("/Users/jack/Desktop/jack_code/PaddleOCR-2.5/data/test_imgs/5.TIF")
image = image[..., ::-1]

# 加载模型
model = lp.PaddleDetectionLayoutModel(config_path="lp://PubLayNet/ppyolov2_r50vd_dcn_365e_publaynet/config",
                                threshold=0.5,
                                label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"},
                                enforce_cpu=False,
                                enable_mkldnn=True)
# 检测
layout = model.detect(image)

# 显示结果
show_img = lp.draw_box(image, layout, box_width=3, show_element_type=True)
show_img.show()