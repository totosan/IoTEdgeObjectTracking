
import json
import os
import io
from datetime import datetime

try:
    import ptvsd
    __myDebug__ = True
    ptvsd.enable_attach(('0.0.0.0',  5679))
except ImportError:
    __myDebug__ = False

# Imports for the REST API
from flask import Flask, request, jsonify

# Imports for image procesing
from PIL import Image
from predict2 import predict, initialize

app = Flask(__name__)

MODEL_FILENAME = 'model.onnx'
LABELS_FILENAME = 'labels.txt'

# 4MB Max image size limit
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024

# Default route just shows simple text


@app.route('/')
def index():
    return 'CustomVision.ai model host harness'

# Like the CustomVision.ai Prediction service /image route handles either
#     - octet-stream image file
#     - a multipart/form-data with files in the imageData parameter

initialize(MODEL_FILENAME)

@app.route('/image', methods=['POST'])
def predict_image_handler(project=None, publishedName=None):
    try:
        imageData = None
        if ('imageData' in request.files):
            imageData = request.files['imageData']
        elif ('imageData' in request.form):
            imageData = request.form['imageData']
        else:
            imageData = io.BytesIO(request.get_data())

        img = Image.open(imageData)
        results = predict(img)
        with open(LABELS_FILENAME) as f:
            labels = [l.strip() for l in f.readlines()]

        predictions = [{'probability': round(float(pred[1]), 8),
                  'tagId': 0,
                  'tagName': labels[pred[2]],
                  'boundingBox': {
                    'left': round(float(pred[0][0]), 8),
                    'top': round(float(pred[0][1]), 8),
                    'width': round(float(pred[0][2]), 8),
                    'height': round(float(pred[0][3]), 8)
                    }
                } for pred in zip(*results)]
        response = {
                'id': '',
                'project': '',
                'iteration': '',
                'created': datetime.utcnow().isoformat(),
                'predictions': predictions }
        return jsonify(response)
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image', 500


if __name__ == '__main__':

    # Run the server
    app.run(host='0.0.0.0', port=80)
