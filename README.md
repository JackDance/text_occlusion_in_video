## 背景介绍
本项目以AWS关键字为例，介绍了如何对aws会议视频中出现的"aws"logo以及视频中出现的"aws"单词进行遮盖，
具体可以使用mask遮盖或者模糊化处理。

## 技术路线
该项目使用mask遮盖的方式进行处理。具体是使用PaddleOCR库对视频每一帧的图像进行
文字识别，如果"识别的字符串".lower() == "aws", 则对该字符串对应的区域进行黑化处理(b, g, r)=(0, 0, 0)。

具体路线图如下：
<center>
    <img src="https://i.postimg.cc/DwDZ3R6t/aws.png" title="Route Map" width="300">
</center>


## 运行步骤
### 1. 环境配置
1.1 新建并激活conda环境
```commandline
conda create -n video_process python=3.8 -y
conda activate video_process
```
1.2 安装依赖

安装paddle框架，这里安装的是cpu版本的paddle，大家根据自己机器的环境选择安装合适版本，参考链接：[paddlepaddle安装](https://www.paddlepaddle.org.cn/)
```commandline
python -m pip install paddlepaddle==2.4.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```
安装项目依赖
```commandline
git clone 该仓库地址
cd 该仓库主目录
pip install -r requirements.txt
```

### 2. 下载预训练的模型
进入主目录，新建并进入pretrained_model文件夹，下面下载两个关于该任务的模型

2.1 下载英文文字检测模型
```commandline
wget https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar
tar xf en_PP-OCRv3_det_infer.tar
```
2.2 下载英文文字识别模型
```commandline
wget https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_rec_infer.tar
tar xf en_PP-OCRv3_rec_infer.tar
```


### 3. 运行命令

3.1执行图像文件夹的end to end推理

输入为待预测的图像文件夹，输出为多张预测后的图像。可视化识别结果默认保存到 ./inference_results 文件夹里面。

```commandline
python3 tools/infer_keyword/infer_end_to_end.py \
--keyword="aws" \
--image_dir=/home/jackdance/Desktop/aws_video/some_frame \
--det_model_dir="./pretrained_model/en_PP-OCRv3_det_infer/" \
--rec_model_dir="./pretrained_model/en_PP-OCRv3_rec_infer/" \
--rec_char_dict_path="ppocr/utils/en_dict.txt" \
--use_mp=True \
--total_process_num=8
```

参数解释：
- keyword 需要替换或遮挡的关键字 (这里只能指定英文关键字，若指定中文，需下载中文文字检测和识别模型以及修改文字识别字符集路径)
- image_dir 输入的图像文件夹
- video 输入的视频
- det_model_dir 文字检测模型的路径
- rec_model_dir 文字识别模型的路径
- rec_char_dict_path 文字识别字符集的路径
- use_mp 是否开启多进程
- total_process_num 使用多进程时的进程数

3.2 执行视频的end to end推理

输入为单个视频，输出为处理过的单个视频（该视频没有音频）

PS: [输入视频样例](https://pan.baidu.com/s/16AxRp0IVYF7AJ67L2GoZBA) 提取码: f93p

```commandline
python3 tools/infer_keyword/infer_end_to_end.py \
--keyword="aws" \
--video=/home/jackdance/Desktop/aws_video/aws_first_2mins.mp4 \
--det_model_dir="./pretrained_model/en_PP-OCRv3_det_infer/" \
--rec_model_dir="./pretrained_model/en_PP-OCRv3_rec_infer/" \
--rec_char_dict_path="ppocr/utils/en_dict.txt" \
--use_mp=True \
--total_process_num=8
```


## 结果示例
第一张图为原始视频中的带有aws字符的某帧图片，第二张图为对应的处理过的图片
<center class="half">
    <img src="https://i.postimg.cc/xds6LqB5/origin-aws.png" title="origin" width="300"/>
    <img src="https://i.postimg.cc/pXq5W8js/processed-aws.png" title="processed" width="300"/>
</center>


## 后续计划
- 增加文字替换功能
- 增加logo遮盖功能
- Docker镜像


如果该仓库有帮助到你，欢迎给个star。有任何疑问都可以提issue～