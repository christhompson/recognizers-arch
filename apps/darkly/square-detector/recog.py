
import cv2
import numpy as np
import os
import argparse
import logging
import zmq
from math import sqrt


log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "square-detector-recog:"


def angle(pt1, pt2, pt0):
    dx1 = pt1[0] - pt0[0]
    dy1 = pt1[1] - pt0[1]
    dx2 = pt2[0] - pt0[0]
    dy2 = pt2[1] - pt0[1]
    tmp = (dx1*dx1 + dy1*dy1)*(dx2*dx2 + dy2*dy2) + 1e-10
    return (dx1*dx2 + dy1*dy2) / sqrt(tmp);


def detect(img, threshold):
    height, width, depth = img.shape
    timg = img.copy()
    pyr = np.zeros((height/2, width/2, depth), np.uint8)

    cv2.pyrDown(timg, pyr)
    cv2.pyrUp(pyr, timg)

    squares = []
    N = 11
    # creates a kernel
    kernel = np.ones((5, 5), np.uint8)

    for channel in cv2.split(timg):
        for level in range(N):
            gray = None
            if level == 0:
                gray = cv2.Canny(channel, 0, threshold, apertureSize=5)
                gray = cv2.dilate(gray, kernel)
            else:
                ret, gray = cv2.threshold(channel, (level+1)*255/N, 255, cv2.THRESH_BINARY)

            contours, h = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                epsilon = cv2.arcLength(contour, True)*0.02
                poly = cv2.approxPolyDP(contour, epsilon, closed=True)
                area = cv2.contourArea(poly)
                poly_double = poly.astype(np.float64)
                if len(poly) == 4 and abs(area) > 1000 and cv2.isContourConvex(poly):
                    s = 0
                    for i in range(2, 4):
                        t = abs(angle(poly_double[i][0], poly_double[i-2][0], poly_double[i-1][0]))
                        s = s if s > t else t

                    if s < 0.3:
                        squares.append((poly[0], poly[2]))

    return squares


def main(capture, sandbox_send, sandbox_recv, files=None):
    logging.debug(TAG + "inside main")
    
    # Default options
    options = {'Threshold': 50}

    # Set up poller to async check our recv socket
    poller = zmq.Poller()
    poller.register(sandbox_recv, zmq.POLLIN)

    frame_num = 0
    while True:
        # Read in from recv socket (might not have anything)
        socks = dict(poller.poll(1))
        if socks.get(sandbox_recv) == zmq.POLLIN:
            options = sandbox_recv.recv_json()
            logging.debug(TAG + "received options update from proxy")

        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        squares = detect(frame, options['Threshold'])

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, squares))

    return True