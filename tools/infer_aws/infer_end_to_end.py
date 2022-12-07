#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time        : 2022/11/25 22:07
# @Author      : Luyao.zhang
# @File        : infer_end_to_end.py
# @Description : aws video processing任务的脚本，输入为视频，输入为不带音频的视频

import os
import sys
import subprocess

__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../..')))

os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

import cv2
import copy
import numpy as np
import json
import time
import logging
from PIL import Image
import tools.infer.utility as utility
import tools.infer.predict_rec as predict_rec
import tools.infer.predict_det as predict_det
import tools.infer.predict_cls as predict_cls
from ppocr.utils.utility import get_image_file_list, check_and_read
from ppocr.utils.logging import get_logger
from tools.infer.utility import draw_ocr_box_txt, get_rotate_crop_image, draw_mosaic
logger = get_logger()


class TextSystem(object):
    def __init__(self, args):
        if not args.show_log:
            logger.setLevel(logging.INFO)

        self.text_detector = predict_det.TextDetector(args)
        self.text_recognizer = predict_rec.TextRecognizer(args)
        self.use_angle_cls = args.use_angle_cls
        self.drop_score = args.drop_score
        if self.use_angle_cls:
            self.text_classifier = predict_cls.TextClassifier(args)

        self.args = args
        self.crop_image_res_index = 0

    def draw_crop_rec_res(self, output_dir, img_crop_list, rec_res):
        os.makedirs(output_dir, exist_ok=True)
        bbox_num = len(img_crop_list)
        for bno in range(bbox_num):
            cv2.imwrite(
                os.path.join(output_dir,
                             f"mg_crop_{bno+self.crop_image_res_index}.jpg"),
                img_crop_list[bno])
            logger.debug(f"{bno}, {rec_res[bno]}")
        self.crop_image_res_index += bbox_num

    def __call__(self, img, cls=True):
        time_dict = {'det': 0, 'rec': 0, 'csl': 0, 'all': 0}
        start = time.time()
        ori_im = img.copy()
        dt_boxes, elapse = self.text_detector(img) # 执行文本检测，返回检测到的bboxes及总的消耗时间elapse
        time_dict['det'] = elapse
        logger.debug("dt_boxes num : {}, elapse : {}".format(
            len(dt_boxes), elapse))
        if dt_boxes is None:
            return None, None
        img_crop_list = []

        dt_boxes = sorted_boxes(dt_boxes)

        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)
        if self.use_angle_cls and cls:
            img_crop_list, angle_list, elapse = self.text_classifier(
                img_crop_list)
            time_dict['cls'] = elapse
            logger.debug("cls num  : {}, elapse : {}".format(
                len(img_crop_list), elapse))

        rec_res, elapse = self.text_recognizer(img_crop_list) # 执行文字识别，返回识别的结果rec_res及总的消耗时间elapse
        time_dict['rec'] = elapse
        logger.debug("rec_res num  : {}, elapse : {}".format(
            len(rec_res), elapse))
        if self.args.save_crop_res:
            self.draw_crop_rec_res(self.args.crop_res_save_dir, img_crop_list,
                                   rec_res)
        filter_boxes, filter_rec_res = [], []
        for box, rec_result in zip(dt_boxes, rec_res):
            text, score = rec_result
            if score >= self.drop_score:
                filter_boxes.append(box)
                filter_rec_res.append(rec_result)
        end = time.time()
        time_dict['all'] = end - start
        # 返回大于设定score阈值的边界框filter_boxes，每个边界框对应的识别结果列表filter_rec_res，单张图片文本检测和文字识别的总时间time_dict
        return filter_boxes, filter_rec_res, time_dict


def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        for j in range(i, 0, -1):
            if abs(_boxes[j + 1][0][1] - _boxes[j][0][1]) < 10 and \
                    (_boxes[j + 1][0][0] < _boxes[j][0][0]):
                tmp = _boxes[j]
                _boxes[j] = _boxes[j + 1]
                _boxes[j + 1] = tmp
            else:
                break
    return _boxes


def main(args):
    # image_file_list = get_image_file_list(args.image_dir)
    # image_file_list = image_file_list[args.process_id::args.total_process_num]
    text_sys = TextSystem(args)
    is_visualize = True
    font_path = args.vis_font_path
    keyword = args.keyword
    drop_score = args.drop_score
    video = args.video
    video_save_dir = args.video_save_path
    video_name = os.path.basename(video).split(".")[0] + ".mp4"
    os.makedirs(video_save_dir, exist_ok=True)
    save_results = []

    logger.info(
        "In PP-OCRv3, rec_image_shape parameter defaults to '3, 48, 320', "
        "if you are using recognition model with PP-OCRv2 or an older version, please set --rec_image_shape='3,32,320"
    )

    # warm up 10 times
    if args.warmup:
        img = np.random.uniform(0, 255, [640, 640, 3]).astype(np.uint8)
        for i in range(10):
            res = text_sys(img)

    total_time = 0
    cpu_mem, gpu_mem, gpu_util = 0, 0, 0
    _st = time.time()

    # the following is to realize the function of video processing
    # 读取视频
    capture = cv2.VideoCapture(args.video)
    # 视频  fps  width  height
    v_fps = capture.get(5)  # 约等于30
    v_width = capture.get(3)  # 1920.0
    v_height = capture.get(4)  # 1080.0
    frame_size = (int(v_width), int(v_height))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # opencv版本是3
    out_path = os.path.join(video_save_dir, video_name)
    videoWriter = cv2.VideoWriter(out_path, fourcc, v_fps, frame_size)

    count = 0
    while True:
        count += 1
        res, image = capture.read()
        if not res:
            logger.info('not res , not image')
            break
        logger.info("-----------"*5)
        logger.info("Processing frame: {}".format(count))

        starttime = time.time()
        dt_boxes, rec_res, time_dict = text_sys(image)
        elapse = time.time() - starttime
        total_time += elapse

        logger.debug(
            str(count) + "  Predict time : %.3fs" %  elapse)
        for text, score in rec_res:
            logger.debug("{}, {:.3f}".format(text, score))

        # 生成识别结果list，示例：
        # res = [{"transcription": "Modernize your data", "points": [[101, 733], [1597, 740], [1597, 855], [101, 848]]}...]
        res = [{
            "transcription": rec_res[idx][0],
            "points": np.array(dt_boxes[idx]).astype(np.int32).tolist(),
        } for idx in range(len(dt_boxes))]
        save_pred = os.path.basename("frame_{}.png".format(count)) + "\t" + json.dumps(
            res, ensure_ascii=False) + "\n"
        save_results.append(save_pred)

        # 检测框boxes
        # boxes = dt_boxes
        boxes = [np.array(dt_boxes[idx]).astype(np.int32).tolist() for idx in range(len(dt_boxes))]
        # 识别的文字txts
        txts = [rec_res[i][0] for i in range(len(rec_res))]
        # txts对应的置信度scores
        scores = [rec_res[i][1] for i in range(len(rec_res))]
        # 对检测到的"aws"打上马赛克
        draw_img = draw_mosaic(
            image,
            boxes,
            txts,
            scores,
            keyword,
            drop_score=drop_score
        )

        videoWriter.write(draw_img)

    videoWriter.release()
    logger.info("The processed video has been saved in: {}".format(out_path))
    logger.info("The predict total time is {}".format(time.time() - _st))

    if args.benchmark:
        text_sys.text_detector.autolog.report()
        text_sys.text_recognizer.autolog.report()

    with open(
            os.path.join(video_save_dir, "system_results.txt"),
            'w',
            encoding='utf-8') as f:
        f.writelines(save_results)


if __name__ == "__main__":
    args = utility.parse_args()
    if args.use_mp:
        p_list = []
        total_process_num = args.total_process_num
        for process_id in range(total_process_num):
            cmd = [sys.executable, "-u"] + sys.argv + [
                "--process_id={}".format(process_id),
                "--use_mp={}".format(False)
            ]
            p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stdout)
            p_list.append(p)
        for p in p_list:
            p.wait()
    else:
        main(args)


