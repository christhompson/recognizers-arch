#
# Based on code by Kostas
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#
# Code from: http://theembeddedsystems.blogspot.com/2011/05/background-subtraction-using-opencv.html

import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "priv-video-full:"


def main():
    logging.debug(TAG + "inside main")

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

    # variables so that methods have scope
    previousFrame = None
    currentFrame = None
    foreground = None

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        currentFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if previousFrame is None:
            previousFrame = currentFrame

        foreground = cv2.absdiff(currentFrame, previousFrame)

        # thresholds the image (note, threshold returns an array, the first item is an array)
        foregroundArray = cv2.threshold(foreground, 10, 255, cv2.THRESH_BINARY)
        foreground = foregroundArray[1]

        # creates a kernel
        kernel = np.ones((5, 5), np.uint8)

        # erode, then two dilates, then erode
        foreground = cv2.erode(foreground, kernel)
        foreground = cv2.dilate(foreground, kernel)
        foreground = cv2.dilate(foreground, kernel)
        foreground = cv2.erode(foreground, kernel)

        #show images
        cv2.imshow('Foreground', foreground)
        logging.debug(TAG + "displayed image")

        previousFrame = currentFrame

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
