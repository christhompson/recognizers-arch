# Based off code from code.ros
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#
# https://code.ros.org/trac/opencv/browser/trunk/opencv/samples/c/demhist.c?rev=1429 (link may be broken)
#

import cv2
import cv
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "intensity-changer-full:"

# variables
hist_size = 64

# method which draws a histogram for the image, given the image
# taken from https://raw.github.com/Itseez/opencv/master/samples/python2/hist.py
# Abid Rahman 3/14/12 debug Gary Bradski
def hist_lines(im):
    h = np.zeros((300, 256, 3))
    hist_item = cv2.calcHist([im], [0], None, [256], [0, 256])
    cv2.normalize(hist_item,hist_item, 0, 255, cv2.NORM_MINMAX)
    hist = np.int32(np.around(hist_item))
    for x, y in enumerate(hist):
        cv2.line(h, (x, 0), (x, y), (255, 255, 255))
    y = np.flipud(h)
    return y

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
    hist = hist_lines(dst_image)
    cv2.imshow('histogram', hist)

# Callback that trackbars will call
def nothing(arg):
    pass

def main():
    # Load the source image. HighGUI use.
    logging.debug(TAG + "inside main")

    #used for capturing from a video file
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", help="capture from video file instead of from camera")
    args = parser.parse_args()

    logging.debug(TAG + "done parsing arguments")
    capture = cv2.VideoCapture()
    if args.video:
        capture.open(args.video)
    else:
        capture.open(0)
    if not capture.isOpened():
        # Failed to open camera
        return False

    logging.debug(TAG + "camera opened")
    cv2.namedWindow('histogram')

    # Creates the trackbars
    cv2.createTrackbar('Brightness', 'histogram', 100, 200, nothing)
    cv2.createTrackbar('Contrast', 'histogram', 100, 200, nothing)

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
    
        # Keeps track of brightness and contrast values, and continually updates them
        brightness = cv2.getTrackbarPos('Brightness', 'histogram')
        contrast = cv2.getTrackbarPos('Contrast', 'histogram')

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        update_brightcont(brightness, contrast, gray)
        logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:
            logging.debug(TAG + "received escape key")
            break

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()