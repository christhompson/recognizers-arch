#
# Original C code: 
# https://code.ros.org/trac/opencv/browser/trunk/opencv/samples/c/laplace.c?rev=27
#
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#
# 

import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "laplace-full:"

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

    cv2.namedWindow("Laplacian", 0)

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        planes = cv2.split(frame)
        for i in range(len(planes)):
            laplace = cv2.Laplacian(planes[i], 10)
            planes[i] = cv2.convertScaleAbs(laplace)
        colorlaplace = cv2.merge(planes)

        #shows image
        cv2.imshow("Laplacian", colorlaplace)
        logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:
            logging.debug(TAG + "received escape key")
            break

    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
