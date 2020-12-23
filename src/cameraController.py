"""
cameraController.py
Adam Zeloof
12/22/2020

This code is licenced under GNU GPLv3 (see LICENCE for details)
"""

import os
import io
import picamera
import time
import json
from PIL import Image

class CameraController():
    """
    A class that controlls a Raspberry Pi camera
    """
    def __init__(self, resolution: tuple, framerate: int, path: str):
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
        """
        Returns a picamera object
        """
        return self.camera

    def setResolution(self, resolution: tuple):
        """
        Sets the camera capture resolution (given as a tuple)
        """
        self.resolution = resolution

    def getResolution(self):
        """
        Returns the camera capture resolution as a tuple
        """
        return self.resolution

    def setFramerate (self, framerate: int):
        """
        Sets the camera framerate (frames per second)
        """
        self.framerate = framerate

    def getFramerate(self):
        """
        Returns the camera framerate (frames per second)
        """
        return self.framerate

    def snapPhoto(self):
        """
        Captures an image and saves it in the stills directory.
        The filename is constructed from the date and time
        """
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.camera.capture(self.settings['path'] + os.sep + timestr + "-bird.jpg", use_video_port=False)

    def getImage(self, width: int, height: int):
        """
        Retrieves the current frame and returns it as a PIL object
        """
        image = io.BytesIO()
        self.camera.capture(image, format='jpeg', resize=(width, height), use_video_port=True)#, splitter_port=splitter_port)
        image.flush()
        image.seek(0) # set the read head at the start of the buffer
        output = Image.open(image)
        return output

    def startRecording(self, output, resolution: tuple, encoding: str, splitter_port: int=1, motion_output=None):
        """
        Begins a recording on the specified port
        """
        self.camera.start_recording(output, resize=resolution, format=encoding, splitter_port=splitter_port, motion_output=motion_output)

    def stopRecording(self, splitter_port: int=1):
        """
        Stops a recording on the specified port
        """
        self.camera.stop_recording(splitter_port=splitter_port)

    def setSettings(self, setting: str=None, value: str=None):
        """
        Applies a camera or system setting
        """
        # im not sorry for this naming convention
        if setting in self.settings:
            self.settings[setting] = value
        self.camera.exposure_mode = self.settings['exposure']
        self.camera.awb_mode = self.settings['white_balance']
        self.camera.brightness = int(self.settings['brightness'])
        self.camera.exposure_compensation = int(self.settings['exposure_compensation'])

    def getSettings(self, setting: str='all'):
        """
        Returns a camera or system setting
        """
        if setting == 'all':
            return self.settings
        elif setting in self.settings:
            return self.settings[setting]
        else:
            return None

    def saveSettings(self):
        """
        Dumps the current camera and system settings into a JSON file
        """
        jsonData = json.dumps(self.settings)
        f = open("settings.json", "w")
        f.write(jsonData)
        f.close()

    def loadSettings(self):
        """
        Reads the camera and system settings in from a JSON file
        """
        try:
            f = open("settings.json", "r")
            jsonData = json.load(f)
            self.settings.update(jsonData)
            self.setSettings()
        except:
            print("Cannot load JSON data")