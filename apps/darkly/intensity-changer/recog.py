#Converted to python by Eric Shen

import cv2
import numpy as np
import os
import argparse
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "intensity-changer-recog:"


# method which calculates a histogram for an image
# taken from https://raw.github.com/Itseez/opencv/master/samples/python2/hist.py
# Abid Rahman 3/14/12 debug Gary Bradski
def calculate_hist(im):
    hist_item = cv2.calcHist([im],[0],None,[256],[0,256])
    cv2.normalize(hist_item,hist_item,0,255,cv2.NORM_MINMAX)
    hist=np.int32(np.around(hist_item))
    return hist

# brightness/contrast callback function
# takes in a brightness, contrast, and source image, and creates
# a destination image
def update_brightcont(_brightness, _contrast, src_image):
    brightness = _brightness - 100
    contrast = _contrast - 100
    # The algorithm is by Werner D. Streidt
    # (http://visca.com/ffactory/archives/5-99/msg00021.html)

    # Creates a lut array (lookup table)
    lut = np.zeros(256, np.uint8)

    # Initializes lookup table (all 256 entries, based on brightness
    # and contrast values)
    if contrast > 0:
        delta = 127.*contrast/100
        a = 255./(255. - delta*2)
        b = a*(brightness - delta)
        for i in range(0, 256):
            #rounds calculated value to nearest integer
            v = int(round(a*i + b))
            if v < 0:
                v = 0
            if v > 255:
                v = 255
            lut[i] = v
    else:
        delta = -128.*contrast/100
        a = (256.-delta*2)/255.
        #rounds calculated value to nearest integer
        b = a*brightness + delta
        for i in range(0, 256):
            v = int(round(a*i + b))
            if v < 0:
                v = 0
            if v > 255:
                v = 255
            lut[i] = v

    # Changes the type of the lookup table to np.uint8
    lut = lut.astype(np.uint8)

    # Applies filter to destination image
    dst_image = cv2.LUT(src_image, lut)

    # cv2.imshow("image", dst_image)
    
    # Changes destination image type to np.float32 so calcHist can run on it
    dst_image = dst_image.astype(np.float32)
    
    # Generates a histogram image
    hist = calculate_hist(dst_image)
    return hist

def main(capture, sandbox_send, sandbox_recv, files):
    logging.debug(TAG + "inside main")

    # Default options
    options = {'Brightness': 100, 'Contrast': 100}

    # Set up poller to async check our recv socket
    poller = zmq.Poller()
    poller.register(sandbox_recv, zmq.POLLIN)

    frame_num = 0
    while True:
        socks = dict(poller.poll(100))
        if socks.get(sandbox_recv) == zmq.POLLIN:
            options = sandbox_recv.recv_json()
            logging.debug(TAG + "received options update from proxy")

        logging.debug(TAG + "before reading frame")

        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        # converts the image to grayscale (so we can calculate a histogram)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # modify frame's brightness and contrast, get resulting histogram
        hist = update_brightcont(options['Brightness'], options['Contrast'], gray)

        # send histogram object
        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, hist))
