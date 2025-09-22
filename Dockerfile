FROM python:3.11.10-slim-bullseye

ARG DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

RUN apt update && \
    apt install -y build-essential cmake ffmpeg freeglut3-dev git libsm6 libxext6 && \
    rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install -r requirements.txt
