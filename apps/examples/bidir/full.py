__author__ = 'cthompson'


#
# Based on code by Philipp Wagner
# Converted to Python by Chris Thompson <cthompson@cs.berkeley.edu>
#
# Brought in code from https://code.ros.org/trac/opencv/browser/trunk/opencv/samples/python2/facedetect.py?rev=6569
#
# /*
#  * Copyright (c) 2011. Philipp Wagner <bytefish[at]gmx[dot]de>.
#  * Released to public domain under terms of the BSD Simplified license.
#  *
#  * Redistribution and use in source and binary forms, with or without
#  * modification, are permitted provided that the following conditions are met:
#  *   * Redistributions of source code must retain the above copyright
#  *     notice, this list of conditions and the following disclaimer.
#  *   * Redistributions in binary form must reproduce the above copyright
#  *     notice, this list of conditions and the following disclaimer in the
#  *     documentation and/or other materials provided with the distribution.
#  *   * Neither the name of the organization nor the names of its contributors
#  *     may be used to endorse or promote products derived from this software
#  *     without specific prior written permission.
#  *
#  *   See <http://www.opensource.org/licenses/bsd-license>
#  */
#

import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "face-detect-full:"


def full_path(rel_path):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, rel_path)


def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:, 2:] += rects[:, :2]
    return rects


def nothing(x):
    pass


def main():
    logging.debug(TAG + "inside main")

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", help="capture from video file instead of from camera")
    args = parser.parse_args()

    logging.debug(TAG + "done parsing arguments")

    cascade_file = "cascades/haarcascade_frontalface_alt.xml"

    cascade = cv2.CascadeClassifier(full_path(cascade_file))
    if cascade.empty():
        print "Error loading cascade files"
        return False

    capture = cv2.VideoCapture()
    if args.video:
        capture.open(args.video)
    else:
        capture.open(0)
    if not capture.isOpened():
        # Failed to open camera
        return False
    logging.debug(TAG + "camera opened")

    # Create window
    cv2.namedWindow('image')

    # Create trackbar, set it's onChange callback to nothing(x) (which we define above)
    cv2.createTrackbar('Face', 'image', 0, 1, nothing)
    # Create switch
    switch = '0 : OFF \n1 : ON'
    cv2.createTrackbar(switch, 'image', 0, 1, nothing)

    while True:
        # Have to always waitKey otherwise UI will freeze
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

        # Check our various parameters
        if not cv2.getTrackbarPos('Face', 'image'):
            # Trackbar is set to 0 (off)
            continue
        if not cv2.getTrackbarPos(switch, 'image'):
            # Switch is off
            continue

        # Trackbar is set to 1 (on)
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        img = frame.copy()
        gray = cv2.cvtColor(img, cv2.cv.CV_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = detect(gray, cascade)

        height = 720
        width = 1280
        blank = np.ones((height, width, 3), np.uint8)
        blank[:, 0:width] = (255, 255, 255)  # convert to white

        draw_rects(blank, faces, (0, 255, 0))
        cv2.imshow("image", blank)
        logging.debug(TAG + "displayed image")

    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
