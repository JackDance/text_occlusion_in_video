#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time        : 2022/11/25 10:58
# @Author      : Luyao.zhang
# @File        : split_video_audio.py
# @Description :

import os
import cv2
import time
import numpy as np
import datetime
import shutil
from moviepy.editor import AudioFileClip

def extract_audio_from_video(video_file, audio_save_path):
    """
    将音频从原始的视频中提取出来，参考链接：https://blog.csdn.net/qq_34769162/article/details/107910036
    :param video_file:
    :param audio_save_path:
    :return:
    """
    audio_file = os.path.join(audio_save_path, video_file.split("/")[-1].split(".")[-1] + ".mp3")

    my_audio_clip = AudioFileClip(video_file)
    my_audio_clip.write_audiofile(audio_file)



def video2frame(video_file, frame_save_dir):
    """
    将视频切成帧并保存
    :param video_file:
    :param frame_save_dir:
    :return:
    """
    if not os.path.exists(frame_save_dir):
        os.makedirs(frame_save_dir)
    # 读取视频
    capture = cv2.VideoCapture(video_file)
    # 视频  fps  width  height
    v_fps = capture.get(5)  # 约等于30
    v_width = capture.get(3)  # 1920.0
    v_height = capture.get(4)  # 1080.0

    count = 0
    while True:
        count += 1
        res, image = capture.read()
        if not res:
            print('not res , not image')
            break
        print("Processing frame: {}".format(count))
        cv2.imwrite(os.path.join(frame_save_dir,  "frame_{}.png".format(count)), image)

    print("处理完毕，该视频总帧数为: {}".format(count))



def frame_to_video(frame_dir, video_save_dir, video_name):
    """
    将连续的多个帧组成一个视频
    :param frame_dir:
    :param video_save_dir:
    :param video_name:
    :return:
    """
    if not os.path.exists(video_save_dir):
        os.makedirs(video_save_dir)

    img_list = os.listdir(frame_dir)
    img_list.sort(key=lambda x: int(x.replace("frame_","").split('.')[0])) # sort()函数直接原地修改img_list
    # print(img_list) # 判断img的顺序是否正确
    #
    fps = int(30)
    frame_size = (1920, 1080) # weight, height
    fourcc = cv2.VideoWriter_fourcc(* "mp4v") #opencv版本是3
    out_path = os.path.join(video_save_dir, video_name)
    videoWriter = cv2.VideoWriter(out_path, fourcc, fps, frame_size)

    for img_name in img_list:
        img_file = os.path.join(frame_dir, img_name)
        frame = cv2.imdecode(np.fromfile(img_file, dtype=np.uint8), -1)
        videoWriter.write(frame)

    videoWriter.release()
    print('finish')


def split_video(video_file, save_dir, time_interval=600):
    """
    #TODO 目前尚未完成

    对长视频进行分割，起始点为原视频开始，终点的视频的总帧数*split_ratio
    :param video_file: 待切割的视频路径
    :param save_dir: 视频保存的目录
    :param time_interval: 单个小视频的时常，默认为600s，即10分钟
    :return:
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    video_name = os.path.basename(video_file).split(".")[0] + ".mp4"
    # 读取视频
    capture = cv2.VideoCapture(video_file)
    # 获得视频的参数  fps  width  height
    v_fps = capture.get(5)  # 约等于30
    v_width = capture.get(3)  # 1920.0
    v_height = capture.get(4)  # 1080.0
    frame_count = int(capture.get(7)) # 视频总帧数
    frame_size = (v_width, v_height)


    count = 0
    while True:
        count += 1
        res, image = capture.read()
        if not res:
            print('not res , not image')
            break
        if not (count % (time_interval*v_fps) == 1): # 这里默认每10分钟保存一个视频
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # opencv版本是3
            video_save_path = os.path.join(save_dir, video_name)
            videoWriter = cv2.VideoWriter(video_save_path, fourcc, v_fps, frame_size)  # 保存文件名、编码器、帧率、视频宽高
            videoWriter.write(image)
        else:
            videoWriter.write(image)

    print("处理完毕，该视频总帧数为: {}".format(count))





if __name__ == '__main__':
    # ----------执行extract_audio_from_video函数------------
    # video_file = r"/Users/jack/Downloads/AWS_video/origin_video/aws.mp4"
    # audio_save_path = r"/Users/jack/Downloads/AWS_video/video_and_audio"
    # extract_audio_from_video(video_file, audio_save_path)

    # ----------执行video2frame函数------------
    # video_file = r"/Users/jack/Downloads/AWS_video/origin_video/aws.mp4"
    # frame_save_path = r"/Users/jack/Downloads/AWS_video/total_frames"
    # st = time.time()
    # video2frame(video_file, frame_save_path)
    # et = time.time()
    # elapse = et - st
    # print("Total elapse time: {}".format(elapse))

    # -------执行frame2video函数----------
    # frame_dir = r"/Users/jack/Downloads/AWS_video/processed_part_frame"
    # video_save_dir = r"/Users/jack/Downloads/AWS_video/generated_video"
    # video_name = r"aws.mp4"
    # frame_to_video(frame_dir, video_save_dir, video_name)

    pass



