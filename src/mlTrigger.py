"""
mlTrigger.py
Adam Zeloof
12/22/2020

This code is licenced under GNU GPLv3 (see LICENCE for details)
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import load_img
from tensorflow.keras.preprocessing.image import img_to_array
import threading
import time
import json
import csv
import os

class MLTrigger():
    """
    A class that handles pulling and classifying frames from the camera.
    The classification loop is run in a thread so it doesn't block other camera functions.
    """
    def __init__(self, cameraController, imageWidth: int=224, imageHeight: int=224, timeout: int=2):
        self.cameraController = cameraController
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.timeout = timeout
        self.t0 = time.time()
        print("loading model...")
        self.model = tf.keras.applications.MobileNet(
            input_shape=None, alpha=1.0, depth_multiplier=1, dropout=0.001,
            include_top=True, weights='imagenet', input_tensor=None, pooling=None,
            classes=1000, classifier_activation='softmax'
        )
        try:
            with open('mobilenet-labels.json') as f:
                self.labels = json.load(f)
        except:
            self.labels = {}
            print("File mobilenet-labels.json not found!")
        self.birdLabels = []
        try:
            with open('bird-labels.csv') as f:
                reader = csv.reader(f)
                for row in reader:
                    self.birdLabels.append(int(row[0]))
        except:
            print("File bird-labels.csv not found!")
        print("model loaded")
    
    def setTimeout(self, timeout: int):
        """
        Sets the timeout between image checks (in seconds)
        """
        self.timeout = timeout

    def getTimeout(self):
        """
        Returns the timeout between image checks (in seconds)
        """
        return self.timeout

    def checkImage(self):
        """
        Pull an image frame from the camera and attempt to classify it
        """
        if time.time() > self.t0 + self.timeout:
            self.t0 = time.time()
            image = self.cameraController.getImage(self.imageWidth, self.imageHeight)
            numpyImage = img_to_array(image)
            imageBatch = np.expand_dims(numpyImage, axis=0)
            processedImage = tf.keras.applications.mobilenet.preprocess_input(imageBatch)

            output = self.model.predict(processedImage)
            group = np.argmax(output)
            confidence = np.max(output)
            label = self.labels[str(group)]
            birdConfidence = 0
            for n in self.birdLabels:
                birdConfidence += output[0,n]
            
            if group in self.birdLabels:
                isBird = True
            else:
                isBird = False

            results = {'label': label, 'confidence': confidence, 'isBird': isBird, 'birdConfidence': birdConfidence}
            print(results)
            return results
        
    def checkForever(self):
        """
        Infinite loop that continually calls checkImage()
        """
        while True:
            self.checkImage()

    def start(self):
        """
        Spawn a thread that runs self.checkForever()
        This continually pulls images from the camera and attempots to classify them
        (with a timeout between each image fetch)
        """
        daemon = threading.Thread(name='daemon_ml_trigger',
                          target=self.checkForever)
        daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()