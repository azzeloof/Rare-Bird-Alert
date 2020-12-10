from webServer import StreamingOutput, StreamingServer, StreamingHandler, initServer
from camera import Camera

def rareBirdAlert():
    stillsPath = "/home/pi/stills"
    camera = Camera(resolution='1280x720', framerate=24, path=stillsPath)
    output = StreamingOutput()
    camera.startRecording(output, 'mjpeg')
    try:
        initServer(output, camera)
    except:
        print("Web server could not be started")
    finally:
        camera.stopRecording()

if __name__ == "__main__":
    rareBirdAlert()
    