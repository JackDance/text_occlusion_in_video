## 背景介绍
对aws会议视频中出现的"aws"logo以及ppt中出现的"aws"单词进行遮盖，
具体可以使用mask遮盖或者模糊化处理。

## 技术路线
该项目使用mask遮盖的方式进行处理。具体是使用PaddleOCR库对视频每一帧的图像进行
文字识别，如果"识别的字符串".lower() == "aws", 则对该字符串对应的区域进行黑化处理(b, g, r)=(0, 0, 0)。
同时，为了提高速度，需要进行并行的操作。具体是先将单个时间长的视频（about 2h）等分成若干个时间较短的视频。然后同时对多个短视频进行处理。

具体路线图如下：
<center>
    <img src="https://i.postimg.cc/V6bvck8R/Technology-Roadmap.jpg" title="Route Map" width="350">
</center>


## 运行步骤
### 1. 下载预训练的模型
进入主目录，新建并进入pretrained_model文件夹，下面下载两个关于该任务的模型
1.1 下载英文文字检测模型
```commandline
wget https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar
tar xf en_PP-OCRv3_det_infer.tar
```
1.2 下载英文文字识别模型
```commandline
wget https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_rec_infer.tar
tar xf en_PP-OCRv3_rec_infer.tar
```


### 2. 运行命令
2.1执行图像文件夹的end to end推理

输入为待预测的图像文件夹，输出为多张预测后的图像

```commandline
python3 tools/infer_aws/predict_system.py \
--image_dir=/home/jackdance/Desktop/aws_video/some_frame \
--det_model_dir="./pretrained_model/en_PP-OCRv3_det_infer/" \
--rec_model_dir="./pretrained_model/en_PP-OCRv3_rec_infer/" \
--rec_char_dict_path="ppocr/utils/en_dict.txt"
```

2.2 执行视频的end to end推理

输入为单个视频，输出为处理过的单个视频（该视频没有音频）

```commandline
python3 tools/infer_aws/infer_end_to_end.py \
--video=/home/jackdance/Desktop/aws_video/aws_first_2mins.mp4 \
--det_model_dir="./pretrained_model/en_PP-OCRv3_det_infer/" \
--rec_model_dir="./pretrained_model/en_PP-OCRv3_rec_infer/" \
--rec_char_dict_path="ppocr/utils/en_dict.txt"
```

## 结果示例
<center class="half">
    <img src="https://i.postimg.cc/xds6LqB5/origin-aws.png" title="origin" width="300"/>
    <img src="https://i.postimg.cc/pXq5W8js/processed-aws.png" title="processed" width="300"/>
</center>
