#from webServer import StreamingOutput, StreamingServer, StreamingHandler, initServer
from webServer import initServer
from cameraController import CameraController
from trigger import MotionDetector
from videoBroadcast import VideoBroadcast, BroadcastOutput
import io
import os

def rareBirdAlert():
    stillsPath = "/home/pi/stills"
    cameraController = CameraController(resolution='4056x3040', framerate=24, path=stillsPath) # max '4056x3040'  '1600x1200'
    # high resolution and framerate required increasing pi GPU memory
    #webOutput = StreamingOutput()
    #cameraController.startRecording(webOutput, (800, 600), 'mjpeg')
    broadcastOutput = BroadcastOutput(cameraController)
    cameraController.startRecording(broadcastOutput, (960, 640), 'yuv')
    detector = MotionDetector(cameraController.getCamera(), size=(640, 480))
    detector.start(cameraController)
    cameraController.startRecording(os.devnull, (640, 480), 'h264', splitter_port=2, motion_output=detector)
    broadcast = VideoBroadcast(broadcastOutput)
    try:
        broadcast.start()
        initServer(cameraController)
        while True:
            cameraController.camera.wait_recording(0)
    finally:
        cameraController.getCamera().close()
        broadcast.stop()
    #    cameraController.stopRecording()
    #    cameraController.stopRecording(splitter_port=2)

if __name__ == "__main__":
    rareBirdAlert()
    