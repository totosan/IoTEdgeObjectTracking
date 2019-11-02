class YoloDetection(object):
    def __init__(self, box, classType, confidence):
        self.box = box
        self.classType = classType
        self.confidence = confidence