
# Python recognizer edge-detect module

import cv2
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "edge-detect-recog:"


def main(capture, sandbox_send, files):
    logging.debug(TAG + "inside main")
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")

        edges = cv2.cvtColor(frame, cv2.cv.CV_RGB2GRAY)
        edges = cv2.GaussianBlur(edges, (7, 7), 1.5, edges, 1.5)
        edges = cv2.Canny(edges, 0, 30, edges, 3)

        logging.debug(TAG + "sending obj")
        sandbox_send.send_pyobj(edges)
