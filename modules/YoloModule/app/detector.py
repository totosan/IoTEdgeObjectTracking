'''
Implement and test car detection (localization)
'''

import numpy as np
from PIL import Image
import os
from matplotlib import pyplot as plt
import time
from glob import glob
from YoloInference import YoloInference
cwd = os.path.dirname(os.path.realpath(__file__))

# Uncomment the following two lines if need to use the Tensorflow visualization_unitls
#os.chdir(cwd+'/models')
#from object_detection.utils import visualization_utils as vis_util

class CarDetector(object):
    def __init__(self, fontScale=1.0):
        self.fontScale = float(fontScale)
        self.car_boxes = []
        self.yoloInference = YoloInference(self.fontScale)
        os.chdir(cwd)
           
    # Helper function to convert image into numpy array    
    def load_image_into_numpy_array(self, image):
         (im_width, im_height) = image.size
         return np.array(image.getdata()).reshape(
            (im_height, im_width, 3)).astype(np.uint8)       
    # Helper function to convert normalized box coordinates to pixels
    def box_normal_to_pixel(self, box, dim):
    
        height, width = dim[0], dim[1]
        box_pixel = [int(box[0]*height), int(box[1]*width), int(box[2]*height), int(box[3]*width)]
        return np.array(box_pixel)       
        
    def get_localization(self, image, imageW, imageH, confidence, visual=False):  
        
        """Determines the locations of the cars in the image

        Args:
            image: camera image

        Returns:
            list of bounding boxes: coordinates [y_up, x_left, y_down, x_right]

        """
        category_index={1: {'id': 1, 'name': u'person'},
                        2: {'id': 2, 'name': u'bicycle'},
                        3: {'id': 3, 'name': u'car'},
                        4: {'id': 4, 'name': u'motorcycle'},
                        5: {'id': 5, 'name': u'airplane'},
                        6: {'id': 6, 'name': u'bus'},
                        7: {'id': 7, 'name': u'train'},
                        8: {'id': 8, 'name': u'truck'},
                        9: {'id': 9, 'name': u'boat'},
                        10: {'id': 10, 'name': u'traffic light'},
                        11: {'id': 11, 'name': u'fire hydrant'},
                        13: {'id': 13, 'name': u'stop sign'},
                        14: {'id': 14, 'name': u'parking meter'}}  
        
  
        boxes, classes, scores = self.yoloInference.runInference(image, imageW,imageH,confidence)

        boxes=np.squeeze(boxes)
        classes =np.squeeze(classes)
        scores = np.squeeze(scores)

        cls = classes.tolist()
        
        # The ID for car in COCO data set is 3 
        idx_vec = [i for i, v in enumerate(cls) if ((v==1) and (scores[i]>0.2))]
        
        if len(idx_vec) ==0:
            print('no detection!')
            self.car_boxes = []  
        else:
            tmp_car_boxes=[]
            for idx in idx_vec:
                dim = image.shape[0:2]
                box = self.box_normal_to_pixel(boxes[idx], dim)
                box_h = box[2] - box[0]
                box_w = box[3] - box[1]
                ratio = box_h/(box_w + 0.01)
                
                if ((ratio < 0.8) and (box_h>20) and (box_w>20)):
                    tmp_car_boxes.append(box)
                    print(box, ', confidence: ', scores[idx], 'ratio:', ratio)
                    
                else:
                    print('wrong ratio or wrong size, ', box, ', confidence: ', scores[idx], 'ratio:', ratio)
                    
                    
            
            self.car_boxes = tmp_car_boxes
             
        return self.car_boxes
        
if __name__ == '__main__':
        # Test the performance of the detector
        det =CarDetector()
        os.chdir(cwd)
        TEST_IMAGE_PATHS= glob(os.path.join('test_images/', '*.jpg'))
        
        for i, image_path in enumerate(TEST_IMAGE_PATHS[0:2]):
            print('')
            print('*************************************************')
            
            img_full = Image.open(image_path)
            img_full_np = det.load_image_into_numpy_array(img_full)
            img_full_np_copy = np.copy(img_full_np)
            start = time.time()
            b = det.get_localization(img_full_np, visual=False)
            end = time.time()
            print('Localization time: ', end-start)
#            
            
