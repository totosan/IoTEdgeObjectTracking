# builds are for (arm64v8 & amd64)
# iot sdk builder
docker build -f "./Dockerfile.iot-sdk-python-builder.amd64" -t "iotcontainertt.azurecr.io/iot-sdk-python-builder:amd64" .
if($?){docker push iotcontainertt.azurecr.io/iot-sdk-python-builder:amd64}
if($?){docker build -f "./Dockerfile.iot-sdk-python-builder.arm64v8" -t "iotcontainertt.azurecr.io/iot-sdk-python-builder:arm64v8" .}
if($?){docker push iotcontainertt.azurecr.io/iot-sdk-python-builder:arm64v8}

# darknet builder
if($?){docker build -f "./Dockerfile.Darknet-cpu.amd64" -t "iotcontainertt.azurecr.io/darknet-python:amd64" .}
if($?){docker push iotcontainertt.azurecr.io/iotcontainertt.azurecr.io/darknet-python:amd64}
if($?){docker build -f "./Dockerfile.Darknet-cpu.arm64v8" -t "iotcontainertt.azurecr.io/darknet-python:arm64v8" .}
if($?){docker push iotcontainertt.azurecr.io/iotcontainertt.azurecr.io/darknet-python:arm64v8}