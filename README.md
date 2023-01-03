## Background Introduction
Taking AWS keywords as an example, this project introduces how to cover up the "aws" logo and the word "aws" that appear in the video of the aws meeting.
Specifically, mask covering or blurring can be used.

## Technical route
This item is processed by mask. Specifically, use the PaddleOCR library to perform text recognition on the image of each frame of the video. If "recognized string".lower() == "aws", then blacken the area corresponding to the string (b, g, r)=(0, 0, 0).

The specific roadmap is as follows：
<center>
    <img src="https://i.postimg.cc/G2kjj6z8/tt.png" title="Route Map" width="300">
</center>


## Run Steps
### 1. Environment configuration
1.1 Create and activate conda environment
```commandline
conda create -n video_process python=3.8 -y
conda activate video_process
```
1.2 Install dependencies

Install Paddle framework. 

The cpu version of paddle is installed here. You can choose to install the appropriate version according to your machine environment. Refer to the link：[PaddlePaddle Installation](https://www.paddlepaddle.org.cn/)
```commandline
python -m pip install paddlepaddle==2.4.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```
Clone the repo and install revolved packages.

There are two channels for [Github](https://github.com/JackDance/text_occlusion_in_video) and [Gitee](https://gitee.com/Jack_forever/aws-video-process) to provide downloads, domestic friends can copy this repo through Gitee.

```commandline
git clone "this repo address"
cd "this repo main directory"
pip install -r requirements.txt
```

### 2. Download pretrained models
Enter the main directory, create a new one and enter the `pretrained_model` folder, download two models about this task below

2.1 Download English text detection and character recognition model
```commandline
wget https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar
tar xf en_PP-OCRv3_det_infer.tar

wget https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_rec_infer.tar
tar xf en_PP-OCRv3_rec_infer.tar
```
If you would like to download other language detection and recognition models, please refer to [PP-OCR series model list](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_en/models_list_en.md)

### 3. Perform Inference

3.1 Perform end-to-end inference of image folders

The input is the image folder to be predicted, and the output is multiple predicted images. Visual recognition results are saved to the ./inference_results folder by default.

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

Parameter comment：
- `keyword`: Keywords that need to be replaced or blocked (only English keywords can be specified here, if Chinese is specified, it is necessary to download the Chinese text detection and recognition model and modify the character set path for text recognition)
- `image_dir`: input image folder
- `video`: input video
- `det_model_dir`: the path to text detection model
- `rec_model_dir`: the path to text recognition model
- `rec_char_dict_path`: the path to the text recognition character set, `ppocr/utils/en_dict.txt` is just for English, other language character set can be found in `ppocr/utils`.
- `use_mp`: whether to enable multiprocessing
- `total_process_num`: numbers of processes when using multiprocessing

3.2 Perform end-to-end inference of video

The input is a single video and the output is a processed single video

PS: [input video sample](https://pan.baidu.com/s/16AxRp0IVYF7AJ67L2GoZBA) Extraction code: f93p

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

## Docker deployment
Use `Dockerfile`to build or directly `pull` the Image.

Method 1: use `Dockerfile` to build
```commandline
# build dockerfile
docker build -t video_process:v0.2 .

# run Image
docker run -it \
--gpus "device=0" \
-v the path to host:the path to docker container \
-p 5002:5002 \
--privileged=True \
--name video_process \
video_process:v0.2 \
/bin/bash
```

Method 2: Directly `pull` the Image
```commandline
# pull from dockerhub
docker pull jackdance/video_process:v0.2

# run Image
docker run -it \
--gpus "device=0" \
-v the path to host:the path to docker container \
-p 5002:5002 \
--privileged=True \
--name video_process \
video_process:v0.2 \
/bin/bash
```

## Sample result
The first picture is a frame picture with aws characters in the original video, and the second picture is the corresponding processed picture
<center class="half">
    <img src="https://i.postimg.cc/xds6LqB5/origin-aws.png" title="origin" width="450"/>
    <img src="https://i.postimg.cc/pXq5W8js/processed-aws.png" title="processed" width="450"/>
</center>


## Update record
- December 8, 2022

    Merge image folder inference and video inference into one script.

- December 9, 2022

    Add additional language detection and recognition models.

- December 12, 2022

    💃 Add Docker deployment.

- December 13, 2022

    🕺 Merge audio to video.

If you also like this project, you may wish to give a `star` (^.^)✨ . If any questions, you can raise `issue`~