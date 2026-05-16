FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu22.04

LABEL maintainer="le700"
LABEL description="赛博吵架 e-battle - AI代吵架系统"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/chatlogs /app/data/avatars /app/data/debates /app/data/shares

EXPOSE 3000

ENV HOST=0.0.0.0
ENV PORT=3000

CMD ["python3", "src/web/app.py"]
