
import json
import os
import io

# Imports for the REST API
from flask import Flask, request, jsonify

# Imports for image procesing
from PIL import Image

# Imports for prediction
from predict import initialize, predict_image, predict_url

app = Flask(__name__)

# 4MB Max image size limit
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 

# Default route just shows simple text
@app.route('/')
def index():
    return 'CustomVision.ai model host harness'

# Like the CustomVision.ai Prediction service /image route handles either
#     - octet-stream image file 
#     - a multipart/form-data with files in the imageData parameter
@app.route('/image', methods=['POST'])
def predict_image_handler():
    try:
        imageData = None
        if ('imageData' in request.files):
            imageData = request.files['imageData']
        elif ('imageData' in request.form):
            imageData = request.form['imageData']
        else:
            imageData = io.BytesIO(request.get_data())

        img = Image.open(imageData)
        results = predict_image(img)
        js = jsonify(results)
        print(f"Detected from PostCar Detector: {js}")
        return js
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image', 500


# Like the CustomVision.ai Prediction service /url route handles url's
# in the body of hte request of the form:
#     { 'Url': '<http url>'}  
@app.route('/url', methods=['POST'])
def predict_url_handler():
    try:
        image_url = json.loads(request.get_data().decode('utf-8'))['url']
        results = predict_url(image_url)
        return jsonify(results)
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image'

if __name__ == '__main__':
    # Load and intialize the model
    initialize()

    # Run the server
    app.run(host='0.0.0.0', port=80)

