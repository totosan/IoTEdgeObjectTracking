# To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

try:
    import ptvsd
    __myDebug__ = True 
    print("Please attach debugger!")
    ptvsd.enable_attach(('0.0.0.0',  5678))   
    #ptvsd.wait_for_attach()
except ImportError:
    __myDebug__ = False
    
import cv2
import numpy as np
import requests
import time
import json
import os
import signal
import urllib.request as urllib2


# Vision imports
import ImageServer
from ImageServer import ImageServer
import VideoStream
from VideoStream import VideoStream

# ML imports
import YoloInference
from YoloInference import YoloInference

# custom imports
import DetectAndTrack
from DetectAndTrack import DetectAndTrack


class VideoCapture(object):

    def __init__(
            self,
            videoPath="",
            verbose=True,
            videoW=0,
            videoH=0,
            fontScale=1.0,
            inference=True,
            confidenceLevel=0.5,
            detectionSampleRate = 10,
            imageProcessingEndpoint=""):

        self.videoPath = videoPath
        self.verbose = verbose
        self.videoW = videoW
        self.videoH = videoH
        self.inference = inference
        self.confidenceLevel = confidenceLevel
        self.useStream = False
        self.useStreamHttp = False
        self.useMovieFile = False
        self.frameCount = 0
        self.vStream = None
        self.vCapture = None
        self.displayFrame = None
        self.fontScale = float(fontScale)
        self.captureInProgress = False
        self.imageResp = None
        self.url = ""
        self.detectionSampleRate = detectionSampleRate
        self.imageProcessingEndpoint = imageProcessingEndpoint

        print("VideoCapture::__init__()")
        print("OpenCV Version : %s" % (cv2.__version__))
        print("===============================================================")
        print("Initialising Video Capture with the following parameters: ")
        print("   - Video path      : " + self.videoPath)
        print("   - Video width     : " + str(self.videoW))
        print("   - Video height    : " + str(self.videoH))
        print("   - Font Scale      : " + str(self.fontScale))
        print("   - Inference?      : " + str(self.inference))
        print("   - ConficenceLevel : " + str(self.confidenceLevel))
        print("   - Dct smpl rate   : " + str(self.detectionSampleRate))
        print("   - Imageproc.Endpt.: " + str(self.imageProcessingEndpoint))
        print("")

        self.imageServer = ImageServer(80, self)
        self.imageServer.start()

        self.yoloInference = YoloInference(self.fontScale)

    def __IsCaptureDev(self, videoPath):
        try:
            return '/dev/video' in videoPath.lower()
        except ValueError:
            return False

    def __IsHttp(self, videoPath):
        try:
            if "http" in videoPath and ":8080" in videoPath:
                return True
            return False
        except:
            return False

    def __IsRtsp(self, videoPath):
        try:
            if 'rtsp:' in videoPath.lower() or '/api/holographic/stream' in videoPath.lower():
                return True
        except ValueError:
            return False

    def __IsYoutube(self, videoPath):
        try:
            if 'www.youtube.com' in videoPath.lower() or 'youtu.be' in videoPath.lower():
                return True
            else:
                return False
        except ValueError:
            return False

    def __enter__(self):

        if self.verbose:
            print("videoCapture::__enter__()")

        self.setVideoSource(self.videoPath)

        return self

    def setVideoSource(self, newVideoPath):

        if self.captureInProgress:
            self.captureInProgress = False
            time.sleep(1.0)
            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None
            elif self.vStream:
                self.vStream.stop()
                self.vStream = None
            elif self.imageResp:
                self.imageResp.close()
                self.imageResp = None

        if self.__IsRtsp(newVideoPath):
            print("\r\n===> RTSP Video Source")

            self.useStream = True
            self.useStreamHttp = False
            self.useMovieFile = False
            self.videoPath = newVideoPath

            if self.vStream:
                self.vStream.start()
                self.vStream = None

            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None

            self.vStream = VideoStream(newVideoPath).start()
            # Needed to load at least one frame into the VideoStream class
            time.sleep(1.0)
            self.captureInProgress = True

        elif self.__IsHttp(newVideoPath):
            print("IsHttp")
            # Use urllib to get the image and convert into a cv2 usable format
            self.url = newVideoPath
            self.useStreamHttp = True
            self.useStream = False
            self.useMovieFile = False
            self.captureInProgress = True

        elif self.__IsYoutube(newVideoPath):
            print("\r\n===> YouTube Video Source")
            self.useStream = False
            self.useStreamHttp = False
            self.useMovieFile = True
            # This is video file
            self.downloadVideo(newVideoPath)
            self.videoPath = newVideoPath
            if self.vCapture.isOpened():
                self.captureInProgress = True
            else:
                print(
                    "===========================\r\nWARNING : Failed to Open Video Source\r\n===========================\r\n")

        elif self.__IsCaptureDev(newVideoPath):
            print("===> Webcam Video Source")
            if self.vStream:
                self.vStream.start()
                self.vStream = None

            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None

            self.videoPath = newVideoPath
            self.useMovieFile = False
            self.useStream = False
            self.useStreamHttp = False
            self.vCapture = cv2.VideoCapture(newVideoPath)
            if self.vCapture.isOpened():
                self.captureInProgress = True
            else:
                print(
                    "===========================\r\nWARNING : Failed to Open Video Source\r\n===========================\r\n")
        else:
            print(
                "===========================\r\nWARNING : No Video Source\r\n===========================\r\n")
            self.useStream = False
            self.useYouTube = False
            self.vCapture = None
            self.vStream = None
        return self

    def downloadVideo(self, videoUrl):
        if self.captureInProgress:
            bRestartCapture = True
            time.sleep(1.0)
            if self.vCapture:
                print("Relase vCapture")
                self.vCapture.release()
                self.vCapture = None
        else:
            bRestartCapture = False

        if os.path.isfile('/app/video.mp4'):
            os.remove("/app/video.mp4")

        print("Start downloading video")
        os.system("youtube-dl -o /app/video.mp4 -f mp4 " + videoUrl)
        print("Download Complete")
        self.vCapture = cv2.VideoCapture("/app/video.mp4")
        time.sleep(1.0)
        self.frameCount = int(self.vCapture.get(cv2.CAP_PROP_FRAME_COUNT))

        if bRestartCapture:
            self.captureInProgress = True

    def get_display_frame(self):
        return self.displayFrame

    def videoStreamReadTimeoutHandler(signum, frame):
        raise Exception("VideoStream Read Timeout")

    def start(self):
        while True:
            if self.captureInProgress:
                self.__Run__()

            if not self.captureInProgress:
                time.sleep(1.0)

    def __Run__(self):

        print("===============================================================")
        print("videoCapture::__Run__()")
        print("   - Stream          : " + str(self.useStream))
        print("   - useMovieFile    : " + str(self.useMovieFile))

        cameraH = 0
        cameraW = 0
        frameH = 0
        frameW = 0
        
        if self.useStream and self.vStream:
            cameraH = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cameraW = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        elif self.useStream == False and self.vCapture:
            cameraH = int(self.vCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cameraW = int(self.vCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
        elif self.useStreamHttp == True:
            cameraW = 1280
            cameraH = 960
        else:
            print("Error : No Video Source")
            return

        if self.videoW != 0 and self.videoH != 0 and self.videoH != cameraH and self.videoW != cameraW:
            needResizeFrame = True
            frameH = self.videoH
            frameW = self.videoW
        else:
            needResizeFrame = False
            frameH = cameraH
            frameW = cameraW

        if needResizeFrame:
            print("Original frame size  : " +
                  str(cameraW) + "x" + str(cameraH))
            print("     New frame size  : " + str(frameW) + "x" + str(frameH))
            print("             Resize  : " + str(needResizeFrame))
        else:
            print("Camera frame size    : " +
                  str(cameraW) + "x" + str(cameraH))
            print("       frame size    : " + str(frameW) + "x" + str(frameH))

        # Check camera's FPS
        if self.useStream:
            cameraFPS = int(self.vStream.stream.get(cv2.CAP_PROP_FPS))
        elif self.useStreamHttp:
            cameraFPS = 30
        else:
            cameraFPS = int(self.vCapture.get(cv2.CAP_PROP_FPS))

        if cameraFPS == 0:
            print("Error : Could not get FPS")
            raise Exception("Unable to acquire FPS for Video Source")

        print("Frame rate (FPS)     : " + str(cameraFPS))

        currentFPS = cameraFPS
        perFrameTimeInMs = 1000 / cameraFPS

        signal.signal(signal.SIGALRM, self.videoStreamReadTimeoutHandler)

        detectionTracker = DetectAndTrack(self.detectionSampleRate, self.confidenceLevel, self.imageProcessingEndpoint)
        while True:

            # Get current time before we capture a frame
            tFrameStart = time.time()
            detectionTracker.SKIP_FRAMES = self.detectionSampleRate
            if not self.captureInProgress:
                print("broke frame processing for new videosource...")
                break

            if self.useMovieFile:
                currentFrame = int(self.vCapture.get(cv2.CAP_PROP_POS_FRAMES))
                if currentFrame >= self.frameCount:
                    self.vCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)

            try:
                # Read a frame
                if self.useStream:
                    # Timeout after 10s
                    signal.alarm(10)
                    frame = self.vStream.read()
                    signal.alarm(0)
                    
                elif self.useStreamHttp:
                    self.imageResp = urllib2.urlopen(self.url)
                    imgNp = np.array(bytearray(self.imageResp.read()),dtype=np.uint8)
                    frame = cv2.imdecode(imgNp,-1)
                    
                else:
                    frame = self.vCapture.read()[1]
            except Exception as e:
                print("ERROR : Exception during capturing")
                raise(e)

            # Resize frame if flagged
            if needResizeFrame:
                frame = cv2.resize(frame, (self.videoW, self.videoH))

            # Run Object Detection -- GUARD
            if self.inference:
                yoloDetections = self.yoloInference.runInference(frame, frameW, frameH, self.confidenceLevel)
                detectionTracker.doStuff(frame, frameW, frameH, yoloDetections)

            # Calculate FPS
            timeElapsedInMs = (time.time() - tFrameStart) * 1000
            currentFPS = 1000.0 / timeElapsedInMs

            if (currentFPS > cameraFPS):
                # Cannot go faster than Camera's FPS
                currentFPS = cameraFPS

            # Add FPS Text to the frame
            cv2.putText(frame, "FPS " + str(round(currentFPS, 1)), (10, int(30 *
                                                                            self.fontScale)), cv2.FONT_HERSHEY_SIMPLEX, self.fontScale, (0, 0, 255), 2)

            self.displayFrame = cv2.imencode('.jpg', frame)[1].tobytes()

            timeElapsedInMs = (time.time() - tFrameStart) * 1000

            if False and (1000 / cameraFPS) > timeElapsedInMs:
                # This is faster than image source (e.g. camera) can feed.
                waitTimeBetweenFrames = perFrameTimeInMs - timeElapsedInMs
                # if self.verbose:
                print("  Wait time between frames :" + str(int(waitTimeBetweenFrames)))
                time.sleep(waitTimeBetweenFrames/1000.0)

    def __exit__(self, exception_type, exception_value, traceback):

        if self.vCapture:
            self.vCapture.release()

        self.imageServer.close()
        cv2.destroyAllWindows()
