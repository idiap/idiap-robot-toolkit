# SPDX-FileCopyrightText: Copyright 2024-2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Olivier Canévet <olivier.canevet@idiap.ch>
# SPDX-License-Identifier: See LICENSE
#
# This file is part of the irt package

ARG PYTHON_MAJOR="3"
ARG PYTHON_MINOR="12"

FROM python:${PYTHON_MAJOR}.${PYTHON_MINOR}-slim

ARG DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

RUN apt update && \
    apt install -y build-essential cmake ffmpeg freeglut3-dev git libegl1-mesa-dev libsm6 libxext6 && \
    rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1

WORKDIR /root

COPY requirements.txt .
RUN pip install -r requirements.txt
