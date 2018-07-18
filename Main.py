#! /usr/bin/python3

import sys
import cv2 as cv
import numpy as np

import ImageObjects
import Detection
from FaceDisplay import *
import Camera as Cam

import http.server
import socketserver

from threading import Thread
from time import sleep


def main(argv):

    SHOW_FRAME = False
    WRITE_FRAME = True

    start_webserver("0.0.0.0", 5000)

    dt = Detection.Recog()
    
    #cam = Cam.URLCam("http://192.168.188.200:200/cam1/cam_pic.php")
    cam = Cam.WebCam(0)
    if SHOW_FRAME:
        cv.namedWindow("canvas")

    display = [Display((900, 1440))]*10

    renderer = MultiScreenFaceDisplay(display)
    while True:
        frame = cam.read_image()
        if frame is None:
             continue

        frame = cv.resize(frame, (1440, 720))

        faces = dt.detectFaces(frame)
        loaded = load_faces(frame, faces)

        renderer.clear()
        renderer.add_face(loaded)
        images = renderer.render(frame)

        img = images.__next__()
        if SHOW_FRAME:
            cv.imshow("canvas", img)
        if WRITE_FRAME:
            cv.imwrite("img/over.jpg",img) #write overlay to special filename

        i = 1
        if WRITE_FRAME:
            for image in images:
                cv.imwrite("img/{:>05}.jpg".format(i), image) #write images to file
                i += 1
    sleep(10)
        

def load_faces(frame, faces):
    for (x,y,w,h) in faces:
       
        img = frame[y:y+h, x:x+w]
        yield ImageObjects.Face(img, (x,y,w,h))

def start_webserver(host, port): #webserver for making images available
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer((host, port), Handler)
    
    print("serving at port", port)
    t = Thread(target = httpd.serve_forever, daemon=True)
    t.start()

if __name__ == "__main__":
    main(sys.argv)