## jack文件夹介绍

执行文件夹的end to end推理
```commandline
python3 tools/jack/predict_system.py \
--image_dir=/home/jackdance/Desktop/aws_video/some_frame \
--det_model_dir="./pretrained_model/en_PP-OCRv3_det_infer/" \
--rec_model_dir="./pretrained_model/en_PP-OCRv3_rec_infer/" \
--rec_char_dict_path="ppocr/utils/en_dict.txt"
```


执行视频的end to end推理
```commandline
python3 tools/jack/infer_end_to_end.py \
--video=/home/jackdance/Desktop/aws_video/aws_first_2mins.mp4 \
--det_model_dir="./pretrained_model/en_PP-OCRv3_det_infer/" \
--rec_model_dir="./pretrained_model/en_PP-OCRv3_rec_infer/" \
--rec_char_dict_path="ppocr/utils/en_dict.txt"
```