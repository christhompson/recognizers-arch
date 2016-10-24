#
# VERSION: HAND DETECTION 1.0
# AUTHOR: ANDOL LI
# PROJECT: HAND DETECTION PROTOTYPE
# SOURCE: https://code.google.com/p/wpi-rbe595-2011-machineshop/source/browse/trunk/handdetection.cpp
#
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#

import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "hand-detector-full:"

def main():
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

    hsv_min = (100, 50, 80)
    hsv_max = (150, 150, 255)

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        # converts the image to HSV
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # gets the images value in range
        hsv_mask = cv2.inRange(hsv_image, hsv_min, hsv_max)

        # shows all the images
        cv2.namedWindow("hsv-mask", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("hsv-mask", hsv_mask)
          
        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:
            logging.debug(TAG + "received escape key")
            break

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
