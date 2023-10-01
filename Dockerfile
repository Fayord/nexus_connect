# Use an official Python runtime as a base image
FROM python:3.10-slim

WORKDIR /opt/
ENV API_PATH=/opt/

RUN apt-get update && \
    pip --no-cache-dir install --upgrade pip 
RUN  apt install python3-dev -y
RUN  apt-get install build-essential -y

# RUN apt-get update && \
#     apt-get install -y git libsm6 libxrender1 libxext-dev libglib2.0-0 supervisor libgl1-mesa-glx && \
#     apt-get clean &&\
#     pip --no-cache-dir install --upgrade pip 
ADD requirements.txt requirements.txt 
RUN pip install -r requirements.txt
ADD .credential /opt/.credential
COPY ./api /opt/api

# COPY /Users/user/miniconda3/envs/chatgpt/lib/python3.10/site-packages/langchain/output_parsers/json.py /usr/local/lib/python3.10/site-packages/langchain/output_parsers/json.py

# COPY ./db_folder/ /opt/db_folder/
# COPY ./params.yaml /opt/params.yaml

WORKDIR /opt/api

CMD uvicorn main:app --workers 1 --host 0.0.0.0 --port 9300
