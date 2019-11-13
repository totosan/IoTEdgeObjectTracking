#!/bin/bash

# YoloModule
set -euo pipefail
docker pull iotcontainertt.azurecr.io/yolomodule:iot-sdk-python-builder || true
docker pull iotcontainertt.azurecr.io/yolomodule:latest-arm64v8 || true

docker build --target=iot-sdk-python-builder -f "../modules/YoloModule/Dockerfile.arm64v8" -t iotcontainertt.azurecr.io/yolomodule:iot-sdk-python-builder "../modules/YoloModule"
docker push iotcontainertt.azurecr.io/yolomodule:iot-sdk-python-builder

docker build --target=cuda-opencv-darknet -f "../modules/YoloModule/Dockerfile.arm64v8" -t iotcontainertt.azurecr.io/yolomodule:latest-arm64v8 "../modules/YoloModule"
docker push iotcontainertt.azurecr.io/yolomodule:latest-arm64v8

# PostcarModule
docker pull iotcontainertt.azurecr.io/postcardetector:compile-image || true
docker pull iotcontainertt.azurecr.io/postcardetector:latest-arm64v8 || true

docker build --target=compile-image -f "../modules/PostcarDetector/Dockerfile.arm64" -t iotcontainertt.azurecr.io/postcardetector:compile-image "../modules/PostcarDetector"
docker push iotcontainertt.azurecr.io/postcardetector:compile-image

docker build --target=build-image -f "../modules/PostcarDetector/Dockerfile.arm64" -t iotcontainertt.azurecr.io/postcardetector:latest-arm64v8 "../modules/PostcarDetector"
docker push iotcontainertt.azurecr.io/postcardetector:latest-arm64v8
