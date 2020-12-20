import os
import picamera
import time
import json

class CameraController():
    def __init__(self, resolution, framerate, path):
        self.resolution = resolution
        self.framerate = framerate
        self.camera = picamera.PiCamera(resolution=self.resolution, framerate=self.framerate)
        self.settings = {}
        self.settings['triggering'] = True
        self.settings['path'] = path
        self.settings['white_balance'] = 'auto'
        self.settings['exposure'] = 'auto'
        self.settings['brightness'] = 50
        self.settings['motion_threshold'] = 60
        self.settings['motion_sensitivity'] = 20
        self.settings['motion_delay'] = 1
        self.settings['motion_timeout'] = 5
        self.settings['exposure_compensation'] = 0
        self.loadSettings()

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

    def snapPhoto(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.camera.capture(self.settings['path'] + os.sep + timestr + "-bird.jpg", use_video_port=False)

    def startRecording(self, output, resolution, encoding, splitter_port=1, motion_output=None):
        if (encoding == "h264"):
            self.camera.start_recording(output, resize=resolution, format=encoding, splitter_port=splitter_port, motion_output=motion_output)
        else:
            self.camera.start_recording(output, resize=resolution, format=encoding, splitter_port=splitter_port)

    def stopRecording(self, splitter_port=1):
        self.camera.stop_recording(splitter_port=splitter_port)

    def setSettings(self, setting=None, value=None):
        # im not sorry
        if setting in self.settings:
            self.settings[setting] = value
        self.camera.exposure_mode = self.settings['exposure']
        self.camera.awb_mode = self.settings['white_balance']
        self.camera.brightness = int(self.settings['brightness'])
        self.camera.exposure_compensation = int(self.settings['exposure_compensation'])
            #return 1 # success
        #else:
            #return 0 # failure

    def getSettings(self, setting='all'):
        if setting == 'all':
            return self.settings
        elif setting in self.settings:
            return self.settings[setting]
        else:
            return None

    def saveSettings(self):
        jsonData = json.dumps(self.settings)
        f = open("settings.json", "w")
        f.write(jsonData)
        f.close()

    def loadSettings(self):
        try:
            f = open("settings.json", "r")
            jsonData = json.load(f)
            self.settings.update(jsonData)
            self.setSettings()
        except:
            print("Cannot load JSON data")