import os
import cv2
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "corner-finder-recog:"


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
        grayscale = cv2.cvtColor(frame, cv2.cv.CV_RGB2GRAY)
        corners = cv2.goodFeaturesToTrack(grayscale, MAX_CORNERS, .01, 20)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, corners, frame.shape))
