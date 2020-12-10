import os
import picamera

class Camera():
    def __init__(self, resolution, framerate, path):
        self.resolution = resolution
        self.framerate = framerate
        self.camera = picamera.PiCamera(resolution=self.resolution, framerate=self.framerate)
        self.path = path

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
        self.camera.capture(self.path + os.sep + "img.jpg")

    def startRecording(self, output, encoding):
        self.camera.start_recording(output, format=encoding)

    def stopRecording(self):
        self.camera.stop_recording()
