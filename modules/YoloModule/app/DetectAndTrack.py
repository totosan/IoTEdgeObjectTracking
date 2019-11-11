import AppState

import iothub_client
# pylint: disable=E0611
# Disabling linting that is not supported by Pylint for C extensions such as iothub_client. See issue https://github.com/PyCQA/pylint/issues/1955
from iothub_client import (IoTHubMessage)
import jsonpickle as jsonP
import jsonpickle.ext.numpy as jsonpickle_numpy

# import the necessary packages
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from pyimagesearch.trackerExt import TrackerExt
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

try:
    import ptvsd
    __myDebug__ = True    
except ImportError:
    __myDebug__ = False


class DetectAndTrack():
    def __init__(self, skipFrame=10, confidence=0.4):
        self.SKIP_FRAMES = skipFrame
        self.CONFIDENCE_LIMIT = confidence

        # initialize the frame dimensions (we'll set them as soon as we read
        # the first frame from the video)
        self.W = None
        self.H = None

        # instantiate our centroid tracker, then initialize a list to store
        # each of our dlib correlation trackers, followed by a dictionary to
        # map each unique object ID to a TrackableObject
        self.ct = CentroidTracker(maxDisappeared=20, maxDistance=50)
        self.trackers = []
        self.trackableObjects = {}

        # initialize the total number of frames processed thus far, along
        # with the total number of objects that have moved either up or down
        self.totalFrames = 0
        self.totalDown = 0
        self.totalUp = 0

        # start the frames per second throughput estimator
        self.fps = FPS().start()
        
        # init other
        jsonpickle_numpy.register_handlers()


    def __sendToHub__(self, trackingObject, rect):
        #strMessage = jsonP.encode(trackingObject, unpicklable=False)                            
        strTemplateFull = "{\"class\":\"%s\",\"Data\":{\"objectNr\":%d,\"centroids\":%s,\"clipregion\":\"%s\"}}"
        strTemplateLight = "{\"class\":\"%s\",\"objectId\":%d}"
        strMessageIoTHub = strTemplateLight % (
            trackingObject.type,
            trackingObject.objectID,
        )
        strMessageModule = strTemplateFull % (
            trackingObject.type,
            trackingObject.objectID,
            np.array(trackingObject.centroids).tolist(),
            rect
        )

        messageIoTHub = IoTHubMessage(strMessageIoTHub)
        messageModule = IoTHubMessage(strMessageModule)
        AppState.HubManager.send_event_to_output("output1", messageIoTHub, 0)
        AppState.HubManager.send_event_to_output("output2", messageModule, 0)

    def doStuff(self, frame, W, H, yoloDetections ):

        # the frame from BGR to RGB for dlib
        #frame = imutils.resize(frame, width=500)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # if the frame dimensions are empty, set them
        if W is None or H is None:
            (H, W) = frame.shape[:2]

        # initialize the current status along with our list of bounding
        # box rectangles returned by either (1) our object detector or
        # (2) the correlation trackers
        status = "Waiting"
        rects = []

        # check to see if we should run a more computationally expensive
        # object detection method to aid our tracker
        if self.totalFrames % self.SKIP_FRAMES == 0:
            # set the status and initialize our new set of object trackers
            status = "Detecting"
            self.trackers = []

            # loop over the detections
            for detection in yoloDetections:
                class_type = detection.classType

                # compute the (x, y)-coordinates of the bounding box
                # for the object
                box = detection.box[0:4] * np.array([1, 1, 1, 1])
                (startX, startY, endX, endY) = box.astype("int")

                # construct a dlib rectangle object from the bounding
                # box coordinates and then start the dlib correlation
                # tracker
                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(startX, startY, endX, endY)

                if __myDebug__:
                    cv2.rectangle(frame, (startX, startY),
                                    (endX, endY), (0, 0, 0), 1)
                    cv2.putText(frame, class_type, (startX, startY),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                tracker.start_track(rgb, rect)

                container = TrackerExt(class_type, tracker, (startX,startY,endX,endY))
    
                # add the tracker to our list of trackers so we can
                # utilize it during skip frames
                self.trackers.append(container)

        # otherwise, we should utilize our object *trackers* rather than
        # object *detectors* to obtain a higher frame processing throughput
        else:
            # loop over the trackers
            for trackerContainer in self.trackers:
                # set the status of our system to be 'tracking' rather
                # than 'waiting' or 'detecting'
                status = "Tracking"
                tracker = trackerContainer.tracker

                # update the tracker and grab the updated position
                tracker.update(rgb)
                pos = tracker.get_position()

                # unpack the position object
                startX = int(pos.left())
                startY = int(pos.top())
                endX = int(pos.right())
                endY = int(pos.bottom())

                trackerContainer.rect = (startX, startY, endX, endY)
                # add the bounding box coordinates to the rectangles list
                rects.append(trackerContainer.rect)

                if __myDebug__:
                    cv2.rectangle(frame, (startX, startY),
                                    (endX, endY), (0, 0, 0), 2)
                    cv2.putText(frame, trackerContainer.class_type, (startX, startY),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # use the centroid tracker to associate the (1) old object
        # centroids with (2) the newly computed object centroids
        extractedRects = [trackerContainer for trackerContainer in self.trackers]

        objects = self.ct.update(extractedRects)

        # loop over the tracked objects
        for (objectID, centroidTrackerData) in objects.items():
            # check to see if a trackable object exists for the current
            # object ID
            to = self.trackableObjects.get(objectID, None)

            centroid = centroidTrackerData[0]
            className = centroidTrackerData[1]
            rect = centroidTrackerData[2]

            # if there is no existing trackable object, create one
            if to is None:
                to = TrackableObject(objectID, className, centroid)
                self.__sendToHub__(to, rect)
                            
            # otherwise, there is a trackable object so we can utilize it
            # to determine direction
            else:
                # the difference between the y-coordinate of the *current*
                # centroid and the mean of *previous* centroids will tell
                # us in which direction the object is moving (negative for
                # 'up' and positive for 'down')
                y = [c[1] for c in to.centroids]

                direction = centroid[1] - np.mean(y)
                to.centroids.append(centroid)

                # check to see if the object has been counted or not
                if not to.counted:
                    # if the direction is negative (indicating the object
                    # is moving up) AND the centroid is above the center
                    # line, count the object
                    if direction < 0 and centroid[1] < H // 2:
                        self.totalUp += 1
                        to.counted = True

                    # if the direction is positive (indicating the object
                    # is moving down) AND the centroid is below the
                    # center line, count the object
                    elif direction > 0 and centroid[1] > H // 2:
                        self.totalDown += 1
                        to.counted = True
                
            # store the trackable object in our dictionary
            self.trackableObjects[objectID] = to

            # draw both the ID of the object and the centroid of the
            # object on the output frame
            text = "ID {}, {}".format(objectID, to.type)
            cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(
                frame, (centroid[0], centroid[1]), 4, (20, 250, 130), -1)


        # increment the total number of frames processed thus far and
        # then update the FPS counter
        self.totalFrames += 1
        self.fps.update()
