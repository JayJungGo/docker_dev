FROM ai-stack-base:cuda12.5.1-py311-devel

# 예시: PyTorch nightly cu128 (이미 성공적으로 쓰셨던 조합)
RUN python3 -m pip install --no-cache-dir --pre \
    --extra-index-url https://download.pytorch.org/whl/nightly/cu128 \
    torch torchvision torchaudio \
 && python3 -m pip install --no-cache-dir tensorboard


# 개인용 3개 Dockerfile patch
RUN apt-get update && apt-get install -y --no-install-recommends \
    git openssh-client ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade jupyterlab jupyterlab-git && \
    jupyter server extension enable --sys-prefix --py jupyterlab_git

# FastAPI 앱 ASGI 서버(Uvicorn)로 실행
RUN python3 -m pip install --no-cache-dir fastapi "uvicorn[standard]"
