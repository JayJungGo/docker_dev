FROM ai-stack-base:cuda12.5.1-py311-devel

# Python 3.11 + pip 정비 (python3 -> 3.11 로 통일)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.11 python3.11-dev python3.11-venv python3-pip git && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    python3 -m pip install --upgrade pip wheel

# cuQuantum + CuPy (+ 과학 스택)
# 관찰된 배포 범위 기준으로 핀(과도한 핀 지양, 메이저 라인만 고정)
RUN python3 -m pip install --no-cache-dir \
    cuquantum-python-cu12 \
    custatevec-cu12 \
    cutensornet-cu12 \
    cupy-cuda12x \
    numpy scipy

# 부팅 시 자가 테스트용 스크립트 추가
COPY check_cuq.py /opt/check_cuq.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /workspace

# NGC 이미지들은 자체 entrypoint 를 쓰는 경우가 있어 CMD를 사용합니다.
CMD ["bash", "-lc", "/usr/local/bin/entrypoint.sh"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    git openssh-client ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 개인용 3개 Dockerfile patch
RUN python3 -m pip install --no-cache-dir --upgrade jupyterlab jupyterlab-git && \
    jupyter server extension enable --sys-prefix --py jupyterlab_git

# FastAPI 앱 ASGI 서버(Uvicorn)로 실행
RUN python3 -m pip install --no-cache-dir fastapi "uvicorn[standard]"
