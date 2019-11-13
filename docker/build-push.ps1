# YoloModule
docker pull iotcontainertt.azurecr.io/yolomodule:iot-sdk-python-builder 
docker pull iotcontainertt.azurecr.io/yolomodule:latest-arm64v8 
if($?){
docker build --target=iot-sdk-python-builder --cache-from=iotcontainertt.azurecr.io/yolomodule:iot-sdk-python-builder -f "..\modules\YoloModule\Dockerfile.arm64v8" -t iotcontainertt.azurecr.io/yolomodule:iot-sdk-python-builder "..\modules\YoloModule"
docker push iotcontainertt.azurecr.io/yolomodule:iot-sdk-python-builder
}
if($?){
docker build --target=cuda-opencv-darknet --cache-from=iotcontainertt.azurecr.io/yolomodule:iot-sdk-python-builder --cache-from=iotcontainertt.azurecr.io/yolomodule:latest-arm64v8 -f "..\modules\YoloModule\Dockerfile.arm64v8" -t iotcontainertt.azurecr.io/yolomodule:latest-arm64v8 "..\modules\YoloModule"
docker push iotcontainertt.azurecr.io/yolomodule:latest-arm64v8 
}

# Postcar Module
docker pull iotcontainertt.azurecr.io/postcardetector:compile-image 
docker pull iotcontainertt.azurecr.io/postcardetector:latest-arm64v8 

docker build --target=compile-image --cache-from=iotcontainertt.azurecr.io/postcardetector:compile-image -f "..\modules\PostcarDetector\Dockerfile.arm64" -t iotcontainertt.azurecr.io/postcardetector:compile-image "..\modules\PostcarDetector"
docker push iotcontainertt.azurecr.io/postcardetector:compile-image 

docker build --target=build-image --cache-from=iotcontainertt.azurecr.io/postcardetector:compile-image --cache-from=iotcontainertt.azurecr.io/postcardetector:latest-arm64v8 -f "..\modules\PostcarDetector\Dockerfile.arm64" -t iotcontainertt.azurecr.io/postcardetector:latest-arm64v8 "..\modules\PostcarDetector"
docker push iotcontainertt.azurecr.io/postcardetector:latest-arm64v8 