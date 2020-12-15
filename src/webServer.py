# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import os
import logging
import socketserver
from threading import Condition
from http import server
from urllib.parse import urlparse
from PIL import Image

webDir = "web"

def parsePost(post_body):
    post_body = post_body.decode('UTF-8')
    queries = post_body.split('&')
    request = {}
    for query in queries:
        querySplit = query.split('=')
        request[querySplit[0]] = querySplit[1]
    return request

def getImage(n, thumb):
    path = cameraController.getSettings('path')
    thumbsize = 400, 400
    images = os.listdir(path)
    images = [f.lower() for f in images]
    sortedImages = sorted(images)
    sortedImages.reverse()
    imageFile = open(path + os.sep + sortedImages[n], 'rb')
    image = Image.open(imageFile)
    if thumb:
        image.thumbnail(thumbsize)
    output = io.BytesIO()
    image.save(output, "JPEG")
    return output.getvalue()

def countPics():
    path = cameraController.getSettings('path')
    return len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        #print(urlparse(self.path))
        parsedPath = urlparse(self.path)
        print(parsedPath)
        if parsedPath.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif parsedPath.path.startswith("/images"):
            pathSplit = parsedPath.path.split('/')
            pathSplitLen = len(pathSplit)
            try:
                n = int(pathSplit[pathSplitLen-1])
                image = getImage(n, pathSplit[pathSplitLen-2] == "thumbs")
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpg')
                self.end_headers()
                self.wfile.write(image)
            except:
                print("Cannot access image.")
        elif parsedPath.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with videoStream.condition:
                        videoStream.condition.wait()
                        frame = videoStream.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif parsedPath.query == 'nPics':
            nPics = countPics()
            self.send_response(200)
            content = str(nPics).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif parsedPath.query.startswith("settings"):
            setting = parsedPath.query.split("=")[1]
            val = cameraController.getSettings(setting)
            self.send_response(200)
            content = str(val).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        else:
            filePath = webDir + parsedPath.path
            print(filePath)
            try:
                if parsedPath.path.endswith(".html"):
                    requestedFile = open(filePath, 'r')
                    requestedData = requestedFile.read()
                    requestedFile.close()
                    content = requestedData.encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.send_header('Content-Length', len(content))
                    self.end_headers()
                    self.wfile.write(content)
                elif parsedPath.path.endswith(".css"):
                    requestedFile = open(filePath, 'r')
                    requestedData = requestedFile.read()
                    requestedFile.close()
                    content = requestedData.encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/css')
                    self.send_header('Content-Length', len(content))
                    self.end_headers()
                    self.wfile.write(content)
                elif parsedPath.path.endswith(".jpg"):
                    requestedFile = open(filePath, 'rb')
                    requestedData = requestedFile.read()
                    requestedFile.close()
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/jpg')
                    self.end_headers()
                    self.wfile.write(requestedData)
                elif parsedPath.path.endswith(".png") or parsedPath.path.endswith(".ico"):
                    requestedFile = open(filePath, 'rb')
                    requestedData = requestedFile.read()
                    requestedFile.close()
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/png')
                    self.end_headers()
                    self.wfile.write(requestedData)
                else:
                    self.send_error(404)
                    self.end_headers()
            except:
                self.send_error(404)
                self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0)) # 0 is default value
        post_body = self.rfile.read(content_len)
        request = parsePost(post_body)
        print(request)
        if "snap" in request:
            cameraController.snapPhoto()
        if "toggleMotion" in request:
            if request["toggleMotion"] == "true":
                cameraController.setSettings('triggering', True)
            else:
                cameraController.setSettings('triggering', False)


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def initServer(videoStreamInput, cameraInput):
    global videoStream
    global cameraController
    videoStream = videoStreamInput
    cameraController = cameraInput
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
