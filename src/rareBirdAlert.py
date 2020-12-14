from webServer import StreamingOutput, StreamingServer, StreamingHandler, initServer
from cameraController import CameraController
from trigger import MotionDetector
import io
import os

def rareBirdAlert():
    stillsPath = "/home/pi/stills"
    cameraController = CameraController(resolution='1600x1200', framerate=24, path=stillsPath) # max '4056x3040'
    # high resolution and framerate required increasing pi GPU memory
    webOutput = StreamingOutput()
    cameraController.startRecording(webOutput, (800, 600), 'mjpeg')
    detector = MotionDetector(cameraController.getCamera(), size=(640, 480))
    detector.start(cameraController)
    cameraController.startRecording(os.devnull, (640, 480), 'h264', splitter_port=2, motion_output=detector)
    try:
        initServer(webOutput, cameraController)
        while True:
            cameraController.camera.wait_recording(1)
    finally:
        cameraController.stopRecording()
        cameraController.stopRecording(splitter_port=2)

if __name__ == "__main__":
    rareBirdAlert()
    