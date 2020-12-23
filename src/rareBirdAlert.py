from webServer import StreamingOutput, StreamingServer, StreamingHandler, initServer
from cameraController import CameraController
from motionTrigger import MotionDetector
from mlTrigger import MLTrigger
import io
import os

def rareBirdAlert():
    stillsPath = "/home/pi/stills"
    cameraController = CameraController(resolution='4056x3040', framerate=24, path=stillsPath) # max '4056x3040'  '1600x1200'
    # high resolution and framerate required increasing pi GPU memory
    webOutput = StreamingOutput()
    cameraController.startRecording(webOutput, (800, 600), 'mjpeg')
    #motionDetector = MotionDetector(cameraController.getCamera(), size=(640, 480))
    #motionDetector.start(cameraController)
    mlDetector = MLTrigger(cameraController, timeout=5)
    #cameraController.startRecording(os.devnull, (640, 480), 'h264', splitter_port=2, motion_output=motionDetector)
    try:
        initServer(webOutput, cameraController)
        mlDetector.start()
        while True:
            cameraController.camera.wait_recording(0)
    finally:
        cameraController.getCamera().close()
    #    cameraController.stopRecording()
    #    cameraController.stopRecording(splitter_port=2)

if __name__ == "__main__":
    rareBirdAlert()
    