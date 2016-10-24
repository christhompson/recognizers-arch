#
#  This program is demonstration for ellipse fitting. Program finds
#  contours and approximate it by ellipses.
#
#  Trackbar specify threshold parametr.
#
#  White lines is contours. Red lines is fitting ellipses.
#
#
#  Author:  Denis Burenkov.
#  Source Code: https://code.ros.org/trac/opencv/browser/trunk/opencv/samples/c/fitellipse.c?rev=1429
#  Converted to Python by Eric Shen <ericshen@berkeley.edu>
#


import cv2
import numpy as np
import os
import argparse
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ellipse-fitter-recog:"


def main(capture, sandbox_send, sandbox_recv, files):
    logging.debug(TAG + "inside main")

    # Default options
    options = {'Threshold': 70}

    # Set up poller to async check our recv socket
    poller = zmq.Poller()
    poller.register(sandbox_recv, zmq.POLLIN)

    frame_num = 0
    while True:
        socks = dict(poller.poll(100))
        if socks.get(sandbox_recv) == zmq.POLLIN:
            options = sandbox_recv.recv_json()
            logging.debug(TAG + "received options update from proxy")

        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        # Threshold and find contours
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        retval, thresholded = cv2.threshold(gray, options['Threshold'], 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, contours))

    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
