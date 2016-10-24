# Based off code from OpenCV website
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#@source https://github.com/Itseez/opencv/blob/master/samples/cpp/tutorial_code/Histograms_Matching/MatchTemplate_Demo.cpp

import cv2
import numpy as np
import os
import argparse
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "template-tracker-recog:"

template_file_name = "template_video.png"


def full_path(rel_path):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, rel_path)


def get_match(match_method, input_img, template_img):
    # Do the Matching and Normalize
    result = cv2.matchTemplate(input_img, template_img, match_method)
    result = cv2.normalize(result, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=-1)

    # Localizing the best match with minMaxLoc
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)

    # For SQDIFF and SQDIFF_NORMED, the best matches are lower values. For all the other methods, the higher the better
    if match_method  == cv2.TM_SQDIFF or match_method == cv2.TM_SQDIFF_NORMED:
        matchLoc = minLoc
    else:
        matchLoc = maxLoc

    # Returns two corners of the rextangle, ((x1, y1), (x2, y2))
    rect = ((matchLoc[0], matchLoc[1]),
            (matchLoc[0] + template_img.shape[1], matchLoc[1] + template_img.shape[0]))
    return rect


def main(capture, sandbox_send, sandbox_recv, files):
    logging.debug(TAG + "inside main")

    template_image = cv2.imread(full_path(template_file_name), 1)

    # Default options
    options = {'Method': 0}

    # Set up poller to async check our recv socket
    poller = zmq.Poller()
    poller.register(sandbox_recv, zmq.POLLIN)

    frame_num = 0
    while True:
        # Read in from recv socket (might not have anything)
        socks = dict(poller.poll(100))
        if socks.get(sandbox_recv) == zmq.POLLIN:
            options = sandbox_recv.recv_json()
            logging.debug(TAG + "received options update from proxy")

        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        #calculates the rectangle to draw
        rect = get_match(options['Method'], frame, template_image)
        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, rect))

    return True
