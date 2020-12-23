"""
webServer.py
Adam Zeloof
12/22/2020

This code is licenced under GNU GPLv3 (see LICENCE for details)

Initially based on http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
"""

import io
import os
import logging
import socketserver
import threading
from threading import Condition
from http import server
from urllib.parse import urlparse
from PIL import Image

webDir = "web"

def parsePost(post_body):
    """
    Parses the data in a http POST request
    """
    post_body = post_body.decode('UTF-8')
    queries = post_body.split('&')
    request = {}
    for query in queries:
        querySplit = query.split('=')
        request[querySplit[0]] = querySplit[1]
    return request

def getImage(fileName: str, thumb: bool):
    """
    Loads an image and prepares it to be sent via the server
    Also resizes to a thumbnail if needed
    """
    path = cameraController.getSettings('path')
    thumbsize = 400, 400
    imageFile = open(path + os.sep + fileName, 'rb')
    image = Image.open(imageFile)
    if thumb:
        image.thumbnail(thumbsize)
    output = io.BytesIO()
    image.save(output, "JPEG")
    return output.getvalue()

def countPics():
    """
    Returns the number of still images saved in the stills directory
    """
    path = cameraController.getSettings('path')
    return len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])

def getPicFilenames(start: int, end: int):
    """
    Returns an array of image filenames for a given range of images
    where 0 corresponds to the most recent image
    """
    path = cameraController.getSettings('path')
    images = sorted(os.listdir(path))
    images.reverse()
    if images != None:
        if start < len(images):
            if end < len(images):
                return images[start:end]
            else:
                print("End out of bounds")
                return images[start:len(images)-1]
        else:
            print("Start out of bounds")
            return None
    else:
        print("No image files to list")
        return None

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
    """
    Handle http requests
    """
    def do_GET(self):
        """
        Handle http GET requests
        """
        parsedPath = urlparse(self.path)
        print(parsedPath)
        if parsedPath.path == '/':
            self.send_response(301)
            self.send_header('Location', '/live')
            self.end_headers()
        elif parsedPath.path.startswith("/image"):
            pathSplit = parsedPath.path.split('/')
            fileName = pathSplit[2]
            print(fileName)
            thumb = parsedPath.query == "thumb"
            try:
                image = getImage(fileName, thumb)
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
            content = str(nPics).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif parsedPath.query.startswith('picFilenames'):
            fileRange = parsedPath.query.split('=')[1]
            start = int(fileRange.split('-')[0])
            end = int(fileRange.split('-')[1])
            content = str(getPicFilenames(start, end)).encode('utf-8')
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
                else: #assume html                    
                    requestedFile = open(filePath + ".html", 'r')
                    requestedData = requestedFile.read()
                    requestedFile.close()
                    content = requestedData.encode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.send_header('Content-Length', len(content))
                    self.end_headers()
                    self.wfile.write(content)
            except:
                self.send_error(404)
                self.end_headers()

    def do_POST(self):
        """
        Handle http POST requests
        """
        content_len = int(self.headers.get('Content-Length', 0)) # 0 is default value
        post_body = self.rfile.read(content_len)
        request = parsePost(post_body)
        print(request)
        if "snap" in request:
            cameraController.snapPhoto()
        elif "saveSettings" in request:
            cameraController.saveSettings()
        elif "loadSettings" in request:
            cameraController.loadSettings()
        else:
            for item in request:
                #try:
                if request[item] == "true":
                    request[item] = True
                elif request[item] == "false":
                    request[item] = False
                cameraController.setSettings(item, request[item])
                #except:
                #    print(request)
                #    print(item)
                #    print(request[item])
                #    pass



class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def runServer(path: str, port: int):
    """
    Starts the server (surprise surprise)
    """
    address = (path, port)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()

def initServer(videoStreamInput, cameraInput):
    """
    Creates and runs the server in a thread so it doesn't block other operations
    """
    global videoStream
    global cameraController
    videoStream = videoStreamInput
    cameraController = cameraInput
    path = ''
    port = 8000
    daemon = threading.Thread(name='daemon_server',
                          target=runServer,
                          args=(path, port))
    daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
    daemon.start()
