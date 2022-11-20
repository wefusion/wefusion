FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY api/requirements.txt ./
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install gcc -y && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove gcc -y && \
    apt-get autoremove -y && \
    apt-get autoclean -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache/pip

COPY core ./core
COPY api ./api
