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
TAG = "laplace-recog:"


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

        planes = cv2.split(frame)
        for i in range(len(planes)):
            laplace = cv2.Laplacian(planes[i], 10)
            planes[i] = cv2.convertScaleAbs(laplace)
        colorlaplace = cv2.merge(planes)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, colorlaplace))
