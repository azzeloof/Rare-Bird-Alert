import os
import picamera
import time

class CameraController():
    def __init__(self, resolution, framerate, path):
        self.resolution = resolution
        self.framerate = framerate
        self.camera = picamera.PiCamera(resolution=self.resolution, framerate=self.framerate)
        self.path = path
        self.triggering = True

    def getCamera(self):
        return self.camera

    def setResolution(self, resolution):
        self.resolution = resolution

    def getResolution(self):
        return self.resolution

    def setFramerate (self, framerate):
        self.framerate = framerate

    def getFramerate(self):
        return self.framerate

    def setPath(self, path):
        self.path = path

    def snapPhoto(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.camera.capture(self.path + os.sep + timestr + "-bird.jpg", use_video_port=False)

    def startRecording(self, output, resolution, encoding, splitter_port=1, motion_output=None):
        self.camera.start_recording(output, resize=resolution, format=encoding, splitter_port=splitter_port, motion_output=motion_output)

    def stopRecording(self, splitter_port=1):
        self.camera.stop_recording(splitter_port=splitter_port)

    def getStillsDir(self):
        return self.path

    def setTriggering(self, triggering):
        self.triggering = triggering
    
    def getTriggering(self):
        return self.triggering
