# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import picamera
from webServer import StreamingOutput, StreamingServer, StreamingHandler, initServer


def rareBirdAlert():
    camera = picamera.PiCamera(resolution='1280x720', framerate=24)
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        initServer(output)
    finally:
        camera.stop_recording()

if __name__ == "__main__":
    rareBirdAlert()