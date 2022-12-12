FROM paddlepaddle/paddle:2.4.1-gpu-cuda10.2-cudnn7.6-trt7.0

COPY ./requirements.txt /requirements.txt

RUN python3 -m pip install -r /requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . /workdir

WORKDIR /workdir

EXPOSE 5002

