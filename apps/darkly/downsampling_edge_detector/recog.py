import cv2
import os
import logging
import zmq
import numpy as np

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "edge-detect-recog:"


def detectEdges(img):
    height, width, depth = img.shape
    pyr = np.zeros((height/2, width/2, depth), np.uint8)
    cv2.pyrDown(img, pyr)
    timg = cv2.cvtColor(pyr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(timg, 10, 100, apertureSize=3)
    return edges


def main(capture, sandbox_send, sandbox_recv, files=None):
    logging.debug(TAG + "inside main")
    frame_num = 0
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        edges = detectEdges(frame)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, edges))

    return True
