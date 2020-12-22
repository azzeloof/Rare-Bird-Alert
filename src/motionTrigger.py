#https://picamera.readthedocs.io/en/release-1.13/api_array.html#pimotionanalysis

import numpy as np
import picamera
from picamera.array import PiMotionAnalysis
import time

class MotionDetector(PiMotionAnalysis):
    def start(self, cameraObj):
        self.t0 = time.time()
        self.cameraObj = cameraObj

    # motion data is in 16 px blocks
    # for 640x480, this means 41x30
    def analyse(self, a):
        threshold = self.cameraObj.getSettings("motion_threshold")
        sensitivity = self.cameraObj.getSettings("motion_sensitivity")
        delay = self.cameraObj.getSettings("motion_delay")
        timeout = self.cameraObj.getSettings("motion_timeout")
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than [sensitivity] vectors with a magnitude greater
        # than [threshold], then say we've detected motion
        t1 = time.time()
        if ((a > threshold).sum() > sensitivity) and (t1 > self.t0 + timeout):
            print('Motion detected!')
            if (self.cameraObj.getSettings('triggering') == True):
                self.cameraObj.snapPhoto()
            self.t0 = t1
            