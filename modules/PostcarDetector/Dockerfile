FROM arm64v8/python:3.6-slim

SHELL ["/bin/bash", "-c"]

RUN pip3 install flask pillow onnxruntime

COPY app /app
# Set the working directory
WORKDIR /app

# Expose the port
EXPOSE 80

# Run the flask server for the endpoints
CMD python3 app.py
