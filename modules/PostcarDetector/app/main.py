# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""label_image for tflite."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import numpy as np

from PIL import Image
import cv2

import tensorflow as tf  # TF2


class Predictor(object):
    def __init__(self):
        self.interpreter = None
        self.input_mean = 127.5
        self.input_std = 127.5

        self.model_file = './model/model.tflite'
        self.label_file = './model/labels.txt'

        self.height = 0
        self.width = 0

        self.floating_model = None
        self.input_details = []
        self.output_details = []

        print("Loading/Initializing model...", end='')
        self.interpreter = tf.lite.Interpreter(model_path=self.model_file)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # check the type of the input tensor
        self.floating_model = self.input_details[0]['dtype'] == np.float32

        # NxHxWxC, H:1, W:2
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]
        print("Done.")

    def load_labels(self):
        with open(self.label_file, 'r') as f:
            return [line.strip() for line in f.readlines()]

    def predict_image_file(self, image):
        img = Image.open(image).resize((self.width, self.height))
        cv2.imshow('img',np.array(img))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # add N dim
        input_data = np.expand_dims(img, axis=0)

        if self.floating_model:
            input_data = (np.float32(input_data) -
                          self.input_mean) / self.input_std

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        self.interpreter.invoke()

        output_data = self.interpreter.get_tensor(
            self.output_details[0]['index'])
        results = np.squeeze(output_data)

        top_k = results.argsort()[-5:][::-1]
        labels = self.load_labels()
        for i in top_k:
            if self.floating_model:
                print('{:08.6f}: {}'.format(float(results[i]), labels[i]))
            else:
                print('{:08.6f}: {}'.format(
                    float(results[i] / 255.0), labels[i]))

    def predict_image(self, image):
        img = image.resize((self.width, self.height))

        # add N dim
        input_data = np.expand_dims(img, axis=0)

        if self.floating_model:
            input_data = (np.float32(input_data) -
                          self.input_mean) / self.input_std

        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        self.interpreter.invoke()

        output_data = self.interpreter.get_tensor(
            self.output_details[0]['index'])
        results = np.squeeze(output_data)

        top_k = results.argsort()[-5:][::-1]
        labels = self.load_labels()
        for i in top_k:
            if self.floating_model:
                print('{:08.6f}: {}'.format(float(results[i]), labels[i]))
            else:
                print('{:08.6f}: {}'.format(
                    float(results[i] / 255.0), labels[i]))


if __name__ == "__main__":
    predict = Predictor()
    predict.predict_image_file('./ASSETS/volvo.jpg')
