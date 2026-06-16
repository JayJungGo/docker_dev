FROM nvidia/cuda:12.5.1-devel-ubuntu22.04

# Python 3.11 + 빌드 도구
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.11 python3.11-dev python3.11-venv python3-pip \
    build-essential git cmake curl \
 && python3.11 -m pip install --upgrade pip wheel \
 && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 20 \
 && update-alternatives --set python3 /usr/bin/python3.11 \
 && rm -rf /var/lib/apt/lists/*

# 품질-of-life
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    CUDA_HOME=/usr/local/cuda \
    CUPY_CACHE_DIR=/root/.cupy/kernel_cache

# 공통 툴 (필요하다면 jupyterlab도 여기에)
RUN python3 -m pip install --no-cache-dir jupyterlab

WORKDIR /workspace

