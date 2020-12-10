import os
import picamera
import time

class Camera():
    def __init__(self, resolution, framerate, path):
        self.resolution = resolution
        self.framerate = framerate
        self.camera = picamera.PiCamera(resolution=self.resolution, framerate=self.framerate)
        self.path = path
        self.output = None
        self.encoding = None

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
        # hopefully this runs at full resolution
        # will cause dropped frames while the resoluion switch happens
        # I think we can get rid of the resolution switch by enabling use_video_port=True
        timestr = time.strftime("%Y%m%d-%H%M%S")
        #self.stopRecording()
        #self.camera.framerate = 1
        #self.camera.resolution = (1920, 1080)
        self.camera.capture(self.path + os.sep + timestr + "-bird.jpg", use_video_port=False)
        #self.camera.resolution = self.resolution
        #self.camera.framerate = self.framerate
        #self.startRecording(self.output, self.encoding)

    def startRecording(self, output, resolution, encoding):
        self.output = output
        self.encoding = encoding
        self.camera.start_recording(self.output, resize=resolution, format=self.encoding)

    def stopRecording(self):
        self.camera.stop_recording()

    def getStillsDir(self):
        return self.path
