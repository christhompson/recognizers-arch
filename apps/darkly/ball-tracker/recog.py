#
# Based on code by Utkarsh Sinha
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#
# Brought in code from https://github.com/liquidmetal/AI-Shack--Tracking-with-OpenCV/blob/master/TrackColour.cpp
#

import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ball-tracker-recog:"


def get_thresholded_image(img):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #threshold/range values for a green ball
    lowerYellow = (50, 100, 100)
    upperYellow = (70, 255, 255)

    imgThreshed = cv2.inRange(imgHSV, lowerYellow, upperYellow)
    #imgThreshed = cv2.inRange(imgHSV, (112, 100, 100), (124, 255, 255))
    return imgThreshed


def main(capture, sandbox_send, sandbox_recv, files=None):
    logging.debug(TAG + "inside main")

    hsv_min = (50, 100, 100)
    hsv_max = (70, 255, 255)

    posX = 0
    posY = 0

    frame_num = 0
    while True:
        logging.debug(TAG + "before reading frame")

        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        # Holds the yellow thresholded image (yellow = white, rest = black)
        imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        imgThresh = cv2.inRange(imgHSV, hsv_min, hsv_max)

        # Calculate the moments to estimate the position of the ball
        moments = cv2.moments(imgThresh)

        # Gets the actual moment values
        moment10 = moments['m10']
        moment01 = moments['m01']
        area = moments['m00']

        lastX = posX
        lastY = posY

        if area != 0:
            posX = moment10 / area
            posY = moment01 / area

        # logging.debug(TAG + "position (" + str(int(posX)) + "," + str(int(posY)) + ")")
        if (lastX > 0 and lastY > 0 and posX > 0 and posY > 0):
            line = (int(posX), int(posY), int(lastX), int(lastY))
            logging.debug(TAG + "sending obj:num %d" % frame_num)
            sandbox_send.send_pyobj((frame_num, line))
