#
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
# Sobel edge detector recognizer
#

import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "sobel-recog:"


def main(capture, sandbox_send, sandbox_recv, files):
    logging.debug(TAG + "inside main")

    scale = 1;
    delta = 0;
    ddepth = cv2.CV_64F

    frame_num = 0
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        img_blur = cv2.GaussianBlur(frame, (3, 3), 0, sigmaY=0)

        # Converts it to grayscale
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_RGB2GRAY)

        # gradient x
        grad_x = cv2.Sobel(img_gray, ddepth, dx=1, dy=0, ksize=3, scale=scale, delta=delta)
        abs_grad_x = cv2.convertScaleAbs(grad_x)

        # gradient Y
        grad_y = cv2.Sobel(img_gray, ddepth, dx=0, dy=1, ksize=3, scale=scale, delta=delta)
        abs_grad_y = cv2.convertScaleAbs(grad_y)

        # Total Gradient (approximate)
        grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, grad))
