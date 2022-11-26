#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time        : 2022/11/26 11:53
# @Author      : Luyao.zhang
# @File        : model_matching.py
# @Description : 模版匹配

import cv2
import numpy as np
from matplotlib import pyplot as plt

def temple_matching_single_target(template_img, target_img):
    """

    :param template_img:
    :param target_img:
    :return:
    """
    # 读取模版图片
    template = cv2.imread(template_img)
    # 读取目标图片
    target = cv2.imread(target_img)
    # 获得模版的高和宽 (h, w, c)
    (theight, twidth) = template.shape[:2]
    # 执行模板匹配，采用的匹配方式cv2.TM_SQDIFF_NORMED
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    # 归一化处理
    cv2.normalize(result, result, 0, 1, cv2.NORM_MINMAX, -1)
    # 寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print("min_val: ", min_val)
    print("max_val: ", max_val)
    print("min_loc: ", min_loc)
    print("max_loc: ", max_loc)
    # 匹配值转换为字符串
    # 对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
    # 对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc
    strmin_val = str(min_val)
    # 绘制矩形边框，将匹配区域标注出来
    # min_loc：矩形定点
    # (min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
    # (0,0,225)：矩形的边框颜色；2：矩形边框宽度
    cv2.rectangle(target, min_loc, (min_loc[0] + twidth, min_loc[1] + theight), (0, 0, 225), 2)
    # # 显示结果,并将匹配值显示在标题栏上
    # cv2.imshow("MatchResult----MatchingValue=" + strmin_val, target)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # 保存图片结果
    cv2.imwrite("matching_img.png", target)


def flann_matching(template_img, target_img):

    MIN_MATCH_COUNT = 10 #设置最低特征点匹配数量为10
    template = cv2.imread(template_img,0) # queryImage
    target = cv2.imread(target_img,0) # trainImage
    # Initiate SIFT detector创建sift检测器
    sift = cv2.xfeatures2d.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(template,None)
    kp2, des2 = sift.detectAndCompute(target,None)
    #创建设置FLANN匹配
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    #舍弃大于0.7的匹配
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)
    if len(good)>MIN_MATCH_COUNT:
        # 获取关键点的坐标
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        #计算变换矩阵和MASK
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        h,w = template.shape
        # 使用得到的变换矩阵对原图像的四个角进行变换，获得在目标图像上对应的坐标
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts,M)
        cv2.polylines(target,[np.int32(dst)],True,0,2, cv2.LINE_AA)
    else:
        print( "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
        matchesMask = None
    draw_params = dict(matchColor=(0,255,0),
                       singlePointColor=None,
                       matchesMask=matchesMask,
                       flags=2)
    result = cv2.drawMatches(template,kp1,target,kp2,good,None,**draw_params)
    plt.imshow(result, 'gray')
    plt.show()





if __name__ == '__main__':
    template_img = r"/Users/jack/Desktop/jack_code/aws-video-process/tools/jack/aws_logo.png"
    target_img = r"/Users/jack/Downloads/AWS_video/some_frame/frame7.png"
    # --------执行temple_matching_single_target------
    # temple_matching_single_target(template_img, target_img)
    # --------执行flann_matching------
    flann_matching(template_img, target_img)


