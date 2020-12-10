from webServer import StreamingOutput, StreamingServer, StreamingHandler, initServer
from camera import Camera

def rareBirdAlert():
    stillsPath = "/home/pi/stills"
    camera = Camera(resolution='1600x1200', framerate=24, path=stillsPath) # max '4056x3040'
    # high resolution and framerate required increasing pi GPU memory
    output = StreamingOutput()
    camera.startRecording(output, (800, 600), 'mjpeg')
    try:
        initServer(output, camera)
    except:
        print("Web server could not be started")
    finally:
        camera.stopRecording()

if __name__ == "__main__":
    rareBirdAlert()
    