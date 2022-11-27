FROM python:3.10-slim

WORKDIR /app

COPY stable_diffusion/requirements.txt /app/requirements.txt

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install gcc -y \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH /app
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256

COPY stable_diffusion ./stable_diffusion
COPY core ./stable_diffusion/core
