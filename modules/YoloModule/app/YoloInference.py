# To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

from darknet import darknet

import cv2
import numpy as np
import time
import os
import json
from datetime import datetime
import YoloDetection
from YoloDetection import YoloDetection
try:
    import ptvsd
    __myDebug__ = True 
    print("Attach debugger for module")
    ptvsd.enable_attach(('0.0.0.0',  5678))   
except ImportError:
    __myDebug__ = False
    
yolocfg = r'yolo/yolov3-tiny.cfg'
yoloweight = r'yolo/yolov3-tiny.weights'
classesFile = r'yolo/coco.names'
dataFile = r'yolo/coco.data'

encoding = 'utf-8'


class YoloInference(object):

    def __init__(
            self,
            fontScale=1.0):

        print("YoloInference::__init__()")
        print("===============================================================")
        print("Initialising Yolo Inference with the following parameters: ")
        print("")

        self.classLabels = None
        self.colors = None
        self.nmsThreshold = 0.35
        self.fontScale = float(fontScale)
        self.fontThickness = 2
        self.net = None
        self.rgb = True
        self.verbose = False
        self.lastMessageSentTime = datetime.now()

        # Read class names from text file
        print("   - Setting Classes")
        with open(classesFile, 'r') as f:
            self.classLabels = [line.strip() for line in f.readlines()]

        # Generate colors for different classes
        print("   - Setting Colors")
        self.colors = np.random.uniform(
            0, 255, size=(len(self.classLabels), 3))

        # Read pre-trained model and config file
        print("   - Loading Model and Config")
        darknet.performDetect(
            configPath=yolocfg, weightPath=yoloweight, metaPath=dataFile, initOnly=True)

    def __get_output_layers(self, net):
        layerNames = net.getLayerNames()
        output_layer = [layerNames[i[0] - 1]
                        for i in net.getUnconnectedOutLayers()]
        return output_layer

    # Malisiewicz et al.
    def __non_max_suppression_fast(self, boxes, overlapThresh):
        # if there are no boxes, return an empty list
        if len(boxes) == 0:
            return []

        # if the bounding boxes integers, convert them to floats --
        # this is important since we'll be doing a bunch of divisions
        if boxes.dtype.kind == "i":
            boxes = boxes.astype("float")

        # initialize the list of picked indexes
        pick = []

        #boxes = np.array([(box[0], box[1], box[0]+ box[2], box[1]+ box[3]) for box in boxes])

        # grab the coordinates of the bounding boxes
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        # compute the area of the bounding boxes and sort the bounding
        # boxes by the bottom-right y-coordinate of the bounding box
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)

        # keep looping while some indexes still remain in the indexes
        # list
        while len(idxs) > 0:
            # grab the last index in the indexes list and add the
            # index value to the list of picked indexes
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            # find the largest (x, y) coordinates for the start of
            # the bounding box and the smallest (x, y) coordinates
            # for the end of the bounding box
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])

            # compute the width and height of the bounding box
            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            # compute the ratio of overlap
            overlap = (w * h) / area[idxs[:last]]

            # delete all indexes from the index list that have
            idxs = np.delete(idxs, np.concatenate(([last],
                                                   np.where(overlap > overlapThresh)[0])))

        # return only the bounding boxes that were picked using the
        # integer data type
        return pick

    def __draw_rect(self, image, class_id, confidence, x, y, x2, y2):

        if self.verbose:
            print("draw_rect x :" + str(x))
            print("draw_rect x :" + str(y))
            print("draw_rect w :" + str(x2))
            print("draw_rect h :" + str(y2))

        label = '%.2f' % confidence
        label = '%s:%s' % (class_id, label)
        color = self.colors[self.classLabels.index(class_id)]

        labelSize, baseLine = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, self.fontScale, self.fontThickness)

        cv2.rectangle(image, (x, y), (x2, y2), color, self.fontThickness)

        # draw text inside the bounding box
        cv2.putText(image, label, (x + self.fontThickness + 2, y +
                                   labelSize[1] + baseLine + self.fontThickness + 2), cv2.FONT_HERSHEY_SIMPLEX, self.fontScale, color, self.fontThickness)

    def runInference(self, frame, frameW, frameH, confidenceLevel):
        try:
            countsByClassId = {}
            boxes = []
            yoloDetections = []

            frame_small = cv2.resize(frame, (416, 416))
            detections = darknet.detect(
                darknet.netMain, darknet.metaMain, frame_small, confidenceLevel)

            boundingBoxes = np.array(list(
                (item[2][0], item[2][1], item[2][0]+item[2][2], item[2][1]+item[2][3]) for item in detections[:]))
            idxs = self.__non_max_suppression_fast(boundingBoxes, 0.3)

            reducedDetections = [detections[idx] for idx in idxs]
            for detection in reducedDetections:
                classID = str(detection[0], encoding)
                confidence = detection[1]

                if confidence > confidenceLevel:

                    if classID not in countsByClassId:
                        countsByClassId[classID] = 1
                    else:
                        countsByClassId[classID] = countsByClassId[classID] + 1

                    bounds = detection[2]* np.array([frameW/416,frameH/416,frameW/416,frameH/416])

                    width = int(bounds[2])
                    height = int(bounds[3])
                    # Coordinates are around the center
                    xCoord = int(bounds[0] - bounds[2]/2)
                    yCoord = int(bounds[1] - bounds[3]/2)
                    # std: obsolete, if working with tracker
                    box = [xCoord, yCoord, xCoord + width, yCoord + height]
                    boxes.append(box)
                    yoloDetections.append(
                        YoloDetection(box, classID, confidence))

                    # draw detection into frame tagged with class id an confidence
                    #self.__draw_rect(frame, classID, confidence, xCoord, yCoord, xCoord + width, yCoord + height)

            if False and __myDebug__:
                if detections is not None and len(detections) > 1:
                    ptvsd.break_into_debugger()
                else:
                    return yoloDetections

            #if len(countsByClassId) > 0 and (datetime.now() - self.lastMessageSentTime).total_seconds() >= 1:
            #    strMessage = json.dumps(countsByClassId)
            #    message = IoTHubMessage(strMessage)
            #    print(strMessage)
            #    AppState.HubManager.send_event_to_output("output1", message, 0)
            #    self.lastMessageSentTime = datetime.now()

        except Exception as e:
            print("Exception during AI Inference")
            print(e)

        return yoloDetections
