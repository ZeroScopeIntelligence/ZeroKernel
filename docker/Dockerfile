FROM debian:trixie

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    binutils \
    nasm \
    make \
    grub-pc-bin \
    grub-common \
    xorriso \
    mtools \
    qemu-system-x86 \
    git \
    curl \
    wget \
    bison \
    flex \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    texinfo \
    nano \
    python3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

CMD ["/bin/bash"]
