"""Sample prediction script for ONNX Runtime"""
import argparse
import onnxruntime
import numpy as np
import PIL.Image
from datetime import datetime

MODEL_FILENAME = 'model.onnx'
LABELS_FILENAME = 'labels.txt'

od_model = None

class ObjectDetection:
    INPUT_TENSOR_NAME = 'data'
    OUTPUT_TENSOR_NAMES = ['detected_boxes', 'detected_scores', 'detected_classes']
    def __init__(self, model_filename):
        self.session = onnxruntime.InferenceSession(model_filename)
        self.input_shape = self.session.get_inputs()[0].shape[2:]
        self.is_fp16 = self.session.get_inputs()[0].type == 'tensor(float16)'

    def predict_image(self, image):
        image = image.convert('RGB') if image.mode != 'RGB' else image
        image = image.resize(self.input_shape)

        inputs = np.array(image, dtype=np.float32)[np.newaxis, :, :, :]
        inputs = inputs.transpose((0, 3, 1, 2))

        if self.is_fp16:
            inputs = inputs.astype(np.float16)

        outputs = self.session.run(self.OUTPUT_TENSOR_NAMES, {self.INPUT_TENSOR_NAME: inputs})
        return (outputs[0][0], outputs[1][0], outputs[2][0])

def initialize(model_filename):
    global od_model
    od_model = ObjectDetection(model_filename)

def predict(image):
    return od_model.predict_image(image)


def main():
    parser = argparse.ArgumentParser('Object Detection for Custom Vision TensorFlow model')
    parser.add_argument('image_filename', type=str, help='Filename for the input image')
    parser.add_argument('--model_filename', type=str, default=MODEL_FILENAME, help='Filename for the ONNX model')
    parser.add_argument('--labels_filename', type=str, default=LABELS_FILENAME, help='Filename for the labels file')
    args = parser.parse_args()

    predictions = predict(args.model_filename, args.image_filename)

    with open(args.labels_filename) as f:
        labels = [l.strip() for l in f.readlines()]

    for pred in zip(*predictions):
        print(f"Class: {labels[pred[2]]}, Probability: {pred[1]}, Bounding box: {pred[0]}")


if __name__ == '__main__':
    main()
