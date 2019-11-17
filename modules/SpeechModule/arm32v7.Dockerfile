FROM balenalib/raspberrypi3:stretch
# The balena base image for building apps on Raspberry Pi 3.

RUN echo "BUILD MODULE: SpeechModule for RASPI"

WORKDIR /app

# Update package index and install dependencies
RUN install_packages \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libopenjp2-7-dev \
    zlib1g-dev \
    libatlas-base-dev \
    wget \
    libboost-python1.62.0 \
    curl \
    libcurl4-openssl-dev \
    alsa-utils \
    espeak \
    # clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

RUN pip3 install --upgrade pip && pip install --upgrade setuptools 
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY /assets/* ./
COPY . .

RUN useradd -ms /bin/bash moduleuser
USER moduleuser

ENTRYPOINT [ "python3", "-u", "./main.py" ]