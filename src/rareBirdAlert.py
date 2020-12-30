"""
rareBirdAlert.py
Adam Zeloof
12/22/2020

This code is licenced under GNU GPLv3 (see LICENCE for details)
"""

from webServer import StreamingServer, StreamingHandler, initServer
from cameraController import CameraController, StreamingOutput
from motionTrigger import MotionDetector
from mlTrigger import MLTrigger
import io
import os
from func_timeout import func_timeout

def rareBirdAlert():
    stillsPath = "/home/pi/stills" # Where will save captured still images
    cameraController = CameraController(resolution='4056x3040', framerate=24, path=stillsPath) # max '4056x3040'  '1600x1200'
    # high resolution and framerate required increasing pi GPU memory
    webOutput = StreamingOutput()
    cameraController.startRecording(webOutput, (800, 600), 'mjpeg')
    #motionDetector = MotionDetector(cameraController.getCamera(), size=(640, 480))
    #motionDetector.start(cameraController)
    triggerOutput = StreamingOutput()
    mlShape = (224, 224)
    cameraController.startRecording(triggerOutput, mlShape, 'mjpeg', splitter_port=2)
    mlDetector = MLTrigger(cameraController, triggerOutput, imageWidth=mlShape[0], imageHeight=mlShape[1], timeout=5)
    #cameraController.startRecording(os.devnull, (640, 480), 'h264', splitter_port=2, motion_output=motionDetector)
    try:
        initServer(webOutput, cameraController)
        #mlDetector.start()
        while True:
            cameraController.camera.wait_recording(mlDetector.getTimeout())
            mlDetector.checkImage()
    finally:
        #mlDetector.stop()
        cameraController.getCamera().close()
    #    cameraController.stopRecording()
    #    cameraController.stopRecording(splitter_port=2)

if __name__ == "__main__":
    rareBirdAlert()
    
