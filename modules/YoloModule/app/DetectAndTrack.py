# USAGE - has to be fit
# To read and write back out to video:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#	--model mobilenet_ssd/MobileNetSSD_deploy.caffemodel --input videos/example_01.mp4 \
#	--output output/output_01.avi
#
# To read from webcam and write back out to disk:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#	--model mobilenet_ssd/MobileNetSSD_deploy.caffemodel \
#	--output output/webcam_output.avi

# import the necessary packages
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from pyimagesearch.trackerExt import TrackerExt
from imutils.video import VideoStream
from imutils.video import FPS
import urllib.request as urllib2
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

import ptvsd

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

    def doStuff(self, frame, W, H, yoloDetections ):

        # resize the frame to have a maximum width of 500 pixels (the
        # less data we have, the faster we can process it), then convert
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
                # extract the confidence (i.e., probability) associated
                # with the prediction
                confidence = detection.confidence
                class_type = "unknown"

                # filter out weak detections by requiring a minimum
                # confidence
                if confidence > self.CONFIDENCE_LIMIT:
                   
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

                    ptvsd.break_into_debugger()
        
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
        extractedRects = [
            trackerContainer for trackerContainer in self.trackers]

        objects = self.ct.update(extractedRects)

        # loop over the tracked objects
        for (objectID, centroidTupel) in objects.items():
            # check to see if a trackable object exists for the current
            # object ID
            to = self.trackableObjects.get(objectID, None)

            centroid = centroidTupel[0]
            className = centroidTupel[1]

            # if there is no existing trackable object, create one
            if to is None:
                to = TrackableObject(objectID, className, centroid)

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

        # construct a tuple of information we will be displaying on the
        # frame
        info = [
            ("Status", status),
        ]

        # loop over the info tuples and draw them on our frame
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # show the output frame
        #cv2.imshow("Frame", frame)
        #key = cv2.waitKey(1) & 0xFF

        # increment the total number of frames processed thus far and
        # then update the FPS counter
        self.totalFrames += 1
        self.fps.update()
