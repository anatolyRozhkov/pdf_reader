FROM python:3.7-slim

MAINTAINER Anatoly Rozhkov <anatoly.rozhkov1998@gmail.com>

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt

COPY . /app

WORKDIR /app

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apt-get update && \
    apt-get install -y ffmpeg libsm6 libxext6 zbar-tools poppler-utils && \
    /py/bin/pip install -r /tmp/requirements.txt

ENV PATH="/py/bin:$PATH"
