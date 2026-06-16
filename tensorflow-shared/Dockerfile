FROM nvcr.io/nvidia/tensorflow:25.02-tf2-py3

RUN apt-get update && apt-get install -y --no-install-recommends \
    git openssh-client ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --upgrade jupyterlab jupyterlab-git && \
    jupyter server extension enable --sys-prefix --py jupyterlab_git

RUN mkdir -p /home/user/.jupyter /home/user/.ssh /home/user/.cache /workspace && \
    chown -R 1000:1000 /home/user /workspace

WORKDIR /workspace
