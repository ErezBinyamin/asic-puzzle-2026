FROM debian:bookworm-slim

LABEL maintainer="ezbin@pm.me"
LABEL description="Lightweight headless ASIC-RE analysis toolkit"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
#ENV LANG en_US.UTF-8

# Install base libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libusb-1.0-0 \
    libftdi1-2 \
    libudev1 \
    libstdc++6 \
    zlib1g \
    libncurses6 \
    libreadline8 \
    libffi8 \
    libssl3 \
    ca-certificates \
    libmagic1 \
    libpcap0.8 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install base tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    less \
    most \
    vim \
    bc \
    curl \
    git \
    tmux \
    unzip \
    locales \
    && rm -rf /var/lib/apt/lists/*
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# --- python ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    pipx \
    && rm -rf /var/lib/apt/lists/* \
    && pipx ensurepath
RUN pipx install --include-deps gdstk

# --- Section: ASIC RE Tools ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    klayout \
    && rm -rf /var/lib/apt/lists/*

# --- Section: compression/decompresion tools for binwalk -e ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    gzip \
    bzip2 \
    tar \
    unrar-free \
    p7zip-full \
    cpio \
    zstd \
    lzop \
    xz-utils \
    squashfs-tools \
    e2tools \
    sleuthkit \
    && rm -rf /var/lib/apt/lists/*

# Configure bash environment
WORKDIR /root
RUN \
	git clone --recursive https://github.com/ErezBinyamin/dotfiles.git; \
	[ -f ~/.bashrc ] && cp ~/.bashrc ~/.bashrc.bak; \
	printf '\n# Dotfiles: https://github.com/ErezBinyamin/dotfiles.git;\nDOTFILES=/root/dotfiles;\n[ -d ${DOTFILES} ] && source ${DOTFILES}/top.sh || echo "[ERROR] DirectoryNotFound: ${DOTFILES}";\n\n' >> ~/.bashrc;

# Clean up APT when done to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /workspace
CMD ["/bin/bash"]

