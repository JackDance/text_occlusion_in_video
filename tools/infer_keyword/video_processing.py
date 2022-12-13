#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time        : 2022/11/25 10:58
# @Author      : Luyao.zhang
# @File        : split_video_audio.py
# @Description :

import os
import cv2
import numpy as np
from natsort import natsorted
from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips

def extract_offline_audio_from_video(video_file, audio_save_path):
    """
    将音频从原始的视频中提取出来并保存，参考链接：https://blog.csdn.net/qq_34769162/article/details/107910036
    注意：提取后，原视频维持不变，即视频中的音频还在
    :param video_file: 待提取的原视频路径
    :param audio_save_path: 音频保存路径
    :return: 音频
    """
    audio_file = os.path.join(audio_save_path, video_file.split("/")[-1].split(".")[-1] + ".mp3")

    my_audio_clip = AudioFileClip(video_file)
    my_audio_clip.write_audiofile(audio_file)

def extract_silent_video(video_file, save_dir):
    """
    将一段视频中的音频删除，保存为无声视频
    :param video_file:
    :param save_path:
    :return:
    """
    os.makedirs(save_dir, exist_ok=True)
    video_name = os.path.basename(video_file)
    save_video_path = os.path.join(save_dir, video_name)

    # 读取视频文件
    video = VideoFileClip(video_file)
    # 删除视频中的音频
    video = video.without_audio()
    # 保存无声的视频
    video.write_videofile(save_video_path)


def merge_online_video_to_audio(src_video_file, generated_video_file, save_path):
    """
    将在线音频合并到没有音频的视频中。
    具体做法：提取原视频src_video_file中的音频audio，然后将audio合并到第二个视频generated_video_file中，最后将合并后的带有音频的视频保存
    :param video_file:
    :param save_path:
    :return:
    """
    os.makedirs(save_dir, exist_ok=True) # 参数exist_ok默认是False，即如果要创建的目录存在就报错，若设为True，则创建目录的时候如果已经存在则不报错
    # 读取src_video_file文件和generated_video_file文件
    src_video_clip = VideoFileClip(src_video_file)
    gen_video_clip = VideoFileClip(generated_video_file)
    # 获得src_video_file文件的音频
    audio = src_video_clip.audio
    # 将音频与生成的视频文件进行合成
    video_clip_audio = gen_video_clip.set_audio(audio)
    # 输出新的视频文件
    video_clip_audio.write_videofile(save_path, audio_codec="aac")

def merge_offline_audio_to_video(video_file, audio_file, save_dir):
    """
    将离线音频合并到没有音频的视频中。
    具体做法：将离线audio合并到视频generated_video_file中，最后将合并后的带有音频的视频保存
    :param video_file:
    :param audio_file:
    :param save_dir:
    :return:
    """
    os.makedirs(save_dir, exist_ok=True)
    # 读取视频文件
    video = VideoFileClip(video_file)
    # 读取音频文件
    audio = AudioFileClip(audio_file)
    # 将音频合并到视频中
    video = video.set_audio(audio)
    # 保存带有音频的视频
    video.write_videofile(os.path.join(save_dir, os.path.basename(video_file)))


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
    v_fps = capture.get(5)  # 这里约等于30
    v_width = capture.get(3)  # 这里1920.0
    v_height = capture.get(4)  # 这里1080.0

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
    将连续的多个帧组成一个视频并保存
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



def split_video(video_file, save_dir, time_interval=2):
    """
    对长视频按照相同的时间间隔分割成多个小视频并保存，示例：
        原视频: aws_part.mp4
        分割后：
            aws_part_1.mp4 # 该视频时长为time_interval
            aws_part_2.mp4 # 该视频时长为time_interval
            ...
            aws_part_n.mp4 # 该视频时长大于0，小于time_interval

    :param video_file: 待切割的视频路径
    :param save_dir: 视频保存的目录
    :param time_interval: 保存视频的时间间隔，默认是2分钟
    :return:
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 读取视频
    capture = cv2.VideoCapture(video_file)
    # 获得视频的参数  fps  width  height
    v_fps = capture.get(5)  # 约等于30
    v_width = capture.get(3)  # 1920.0
    v_height = capture.get(4)  # 1080.0
    frame_count = int(capture.get(7)) # 视频总帧数
    frame_size = (int(v_width), int(v_height))

    interval_frame = needTime= time_interval * 60 * v_fps # 每一段视频的帧数

    name = 1
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # opencv版本是3
    video_name = os.path.basename(video_file).split(".")[0] + "_{}.mp4".format(name)
    video_save_path = os.path.join(save_dir, video_name)
    videoWriter = cv2.VideoWriter(video_save_path, fourcc, v_fps, frame_size)  # 保存文件名、编码器、帧率、视频宽高

    count = 0

    while capture.isOpened(): # 当成功打开视频时cap.isOpened()返回True,否则返回False
        print("\r", "正在截取第{}个视频...".format(name), end="", flush=True)
        count += 1
        success, frame = capture.read()
        if not success:
            print('not res , not image')
            break
        if (count % interval_frame < needTime-1):
            videoWriter.write(frame)
        else:
            name += 1
            video_name = os.path.basename(video_file).split(".")[0] + "_{}.mp4".format(name)
            video_save_path = os.path.join(save_dir, video_name)
            videoWriter = cv2.VideoWriter(video_save_path, fourcc, v_fps, frame_size)

    print("--------Completed!--------")
    capture.release()


def cut_video(video_path):
    """
    使用moviepy库对视频进行截取
    :param video_path: 视频路径
    :return:
    """
    video = VideoFileClip(video_path)

    # 剪辑视频，截取视频的前20秒
    video = video.subclip(0, 20)

    # 剪辑视频，从10秒开始到视频结尾前20秒
    video = video.subclip(10, video.duration - 12)

def merge_video(video_dir, merged_video_save_dir):
    """
    将多个短视频按照顺序组合成一个大的视频。参考链接：https://blog.51cto.com/aiyc/2886210
    :param video_dir:
    :param merged_video_save_dir:
    :return:
    """
    os.makedirs(merged_video_save_dir, exist_ok=True)

    video_list = os.listdir(video_dir)
    # delete '.DS_Store' file
    for file in video_list:
        if file == '.DS_Store':
            os.remove(os.path.join(video_dir, file))

    video_list = natsorted(video_list)
    # video_list.sort(key=lambda x: int(x.replace("aws_part1_", "").split('.')[0]))  # sort()函数直接原地修改img_list
    print("merge视频的顺序为: {}".format(video_list)) # double check video sequence

    for video_name in video_list:
        abs_video_path =os.path.join(video_dir, video_name)
        break
    # 获得视频参数信息
    capture = cv2.VideoCapture(abs_video_path)
    v_fps = capture.get(5) # 获得一个小视频的帧率

    L = list() # 定义一个列表
    for video_name in video_list:
        abs_video_path = os.path.join(video_dir, video_name)
        # 载入视频
        video = VideoFileClip(abs_video_path) # <moviepy.video.io.VideoFileClip.VideoFileClip object at 0x7f8c7001d940>
        # 添加到数组
        L.append(video)
    # 拼接视频
    final_clip = concatenate_videoclips(L)
    # 生成目标视频文件
    generated_video_name = "merged_video.mp4"
    final_clip.to_videofile(os.path.join(merged_video_save_dir, generated_video_name), v_fps, remove_temp=False)





if __name__ == '__main__':
    # ----------执行extract_offline_audio_from_video函数------------
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

    # ------执行split_video函数----------
    # video_file = r"/Users/jack/Downloads/AWS_video/origin_video/aws_part1.mp4"
    # save_dir = r"/Users/jack/Downloads/AWS_video/generated_video/new"
    # split_video(video_file, save_dir, time_interval=2)

    # -----执行merge_video函数----------
    # video_dir = r"/Users/jack/Downloads/AWS_video/generated_video/new"
    # merged_video_save_dir = r"/Users/jack/Downloads/AWS_video/generated_video/merged_video"
    # merge_video(video_dir, merged_video_save_dir)

    # -----执行merge_video函数----------
    # video_dir = r"/Users/jack/Downloads/AWS_video/generated_video/new"
    # merged_video_save_dir = r"/Users/jack/Downloads/AWS_video/generated_video/merged_video"
    # merge_video(video_dir, merged_video_save_dir)

    #------执行merge_online_video_to_audio函数--------
    src_video_file = r"/Users/jack/Desktop/video/original_video.mp4"
    generated_video_file = r"/Users/jack/Desktop/video/video_without_audio.mp4"
    save_dir = r"/Users/jack/Desktop/video"
    merge_online_video_to_audio(src_video_file, generated_video_file, save_dir)

    # -----执行extract_silent_video函数-------
    # video_file = r"/Users/jack/Downloads/AWS_video/origin_video/aws.mp4"
    # save_dir = r"/Users/jack/Downloads/AWS_video/generated_video"
    # extract_silent_video(video_file, save_dir)

    # -----执行merge_offline_audio_to_video函数-----------
    # video_file = r"/Users/jack/Downloads/AWS_video/generated_video/aws.mp4"
    # audio_file = r"/Users/jack/Downloads/AWS_video/audio/mp4.mp3"
    # save_dir = "/Users/jack/Downloads/AWS_video/generated_video/final"
    # merge_offline_audio_to_video(video_file, audio_file, save_dir)




