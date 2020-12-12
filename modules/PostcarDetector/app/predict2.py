"""Sample prediction script for ONNX Runtime"""
import argparse
import onnxruntime
import numpy as np
from PIL import Image

MODEL_FILENAME = 'model.onnx'
LABELS_FILENAME = 'labels.txt'

od_model = None

class ObjectDetection:
    INPUT_TENSOR_NAME = 'data'
    OUTPUT_TENSOR_NAMES = ['classLabel', 'loss']
    def __init__(self, model_filename):
        self.session = onnxruntime.InferenceSession(model_filename)
        self.input_shape = self.session.get_inputs()[0].shape[2:]
        #self.label_name = [output_tensor.name for output_tensor in self.session.get_outputs()]
        self.is_fp16 = self.session.get_inputs()[0].type == 'tensor(float16)'

    def crop_center(self, pil_img, crop_width, crop_height):
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                            (img_height - crop_height) // 2,
                            (img_width + crop_width) // 2,
                            (img_height + crop_height) // 2))
    def crop_max_square(self,pil_img):
        return self.crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    def predict_image(self, image):
        image = image.convert('RGB') if image.mode != 'RGB' else image
        image = self.crop_max_square(image)
        data = np.asarray(image)
        image = Image.fromarray(np.roll(data,1,axis=-1))
        image = image.resize(self.input_shape)

        inputs = np.array(image, dtype=np.float32)[np.newaxis, :, :, :]
        inputs = inputs.transpose((0, 3, 1, 2))

        if self.is_fp16:
            inputs = inputs.astype(np.float16)

        outputs = self.session.run(self.OUTPUT_TENSOR_NAMES, {self.INPUT_TENSOR_NAME: inputs})
        return (outputs)

def initialize(model_filename):
    global od_model
    od_model = ObjectDetection(model_filename)

def predict(image):
    return od_model.predict_image(image)

