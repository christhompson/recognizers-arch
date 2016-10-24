import os
import cv2
import numpy as np
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "hsv-hist-recog:"

def calc_hist(hsv):
    scale = 10
    hist_size = [30, 32]
    hranges = [0, 180]
    sranges = [0, 255]
    channels = [0, 1]
    hist = cv2.calcHist([hsv], [0, 1], None, hist_size, hranges + sranges)
    return hist

def main(capture, sandbox_send, sandbox_recv, files):
    logging.debug(TAG + "inside main")
    MAX_CORNERS = 20

    frame_num = 0
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        hsv = cv2.cvtColor(frame, cv2.cv.CV_BGR2HSV)
        hist = calc_hist(hsv)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, hist))
