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
TAG = "priv-video-recog:"


def main(capture, sandbox_send, sandbox_recv, files):
    logging.debug(TAG + "inside main")

    # variables so that methods have scope
    previousFrame = None
    currentFrame = None
    foreground = None

    frame_num = 0
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        frame_num += 1

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

        previousFrame = currentFrame

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, foreground))
