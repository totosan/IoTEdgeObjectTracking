
# iot sdk builder (arm64v8 / amd64)
docker build -f "./Dockerfile.iot-sdk-python-builder.amd64" -t "iotcontainertt.azurecr.io/iot-sdk-python-builder:amd64" .
if($?){docker push iotcontainertt.azurecr.io/iot-sdk-python-builder:amd64}
if($?){docker build -f "./Dockerfile.iot-sdk-python-builder.arm64v8" -t "iotcontainertt.azurecr.io/iot-sdk-python-builder:arm64v8" .}
if($?){docker push iotcontainertt.azurecr.io/iot-sdk-python-builder:arm64v8}

# darknet builder (amd64)
if($?){docker build -f "./Dockerfile.Darknet.amd64" -t "iotcontainertt.azurecr.io/darknet-python:amd64" .}
if($?){docker push iotcontainertt.azurecr.io/darknet-python:amd64}
