FROM arm64v8/ubuntu:bionic-20191029
# The balena base image for building apps on Jetson Nano/TX2.

RUN echo "BUILD MODULE: SpeechModule for JETSON NANO"

WORKDIR /app

# Update package index and install dependencies
RUN apt update && apt install -y \
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
    # clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

RUN pip3 install --upgrade pip && pip install --upgrade setuptools 
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY /assets/*.mp3 ./
COPY /assets/asound.conf /etc/
COPY . .


ENTRYPOINT [ "python3", "./app.py" ]