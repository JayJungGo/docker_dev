FROM ai-stack-base:cuda12.5.1-py311-devel

RUN python3 -m pip install --no-cache-dir \
    "pennylane>=0.37" "pennylane-lightning[gpu]" pennylane-cirq \
    numpy scipy networkx matplotlib
# 필요 시 cuQuantum과 연동하려면 이 이미지에도 custatevec/cutensornet을 추가

# 개인용 3개 Dockerfile patch
RUN apt-get update && apt-get install -y --no-install-recommends \
    git openssh-client ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade jupyterlab jupyterlab-git && \
    jupyter server extension enable --sys-prefix --py jupyterlab_git

# FastAPI 앱 ASGI 서버(Uvicorn)로 실행
RUN python3 -m pip install --no-cache-dir fastapi "uvicorn[standard]"

