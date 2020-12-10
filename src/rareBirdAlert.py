from webServer import StreamingOutput, StreamingServer, StreamingHandler, initServer
from camera import Camera
from trigger import MotionDetector
import io
import os

def rareBirdAlert():
    stillsPath = "/home/pi/stills"
    camera = Camera(resolution='1600x1200', framerate=24, path=stillsPath) # max '4056x3040'
    # high resolution and framerate required increasing pi GPU memory
    webOutput = StreamingOutput()
    camera.startRecording(webOutput, (800, 600), 'mjpeg')
    detector = MotionDetector(camera.camera, size=(640, 480))
    detector.start(camera)
    camera.startRecording(os.devnull, (640, 480), 'h264', splitter_port=2, motion_output=detector)
    try:
        initServer(webOutput, camera)
        while True:
            camera.camera.wait_recording(1)
    finally:
        camera.stopRecording()
        camera.stopRecording(splitter_port=2)

if __name__ == "__main__":
    rareBirdAlert()
    