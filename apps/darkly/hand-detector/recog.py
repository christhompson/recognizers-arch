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
TAG = "hand-detector-recog:"

def main(capture, sandbox_send, sandbox_recv, files):
    logging.debug(TAG + "inside main")

    frame_num = 0
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        #converts the image to HSV
        hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        hsv_min = (100, 50, 80)
        hsv_max = (150, 150, 255)

        #gets the images value in range
        hsv_mask = cv2.inRange(hsv_image, hsv_min, hsv_max)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, hsv_mask))
