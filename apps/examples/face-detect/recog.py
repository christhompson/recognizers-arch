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

import os
import cv2
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "face-detect-recog:"


def full_path(rel_path):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, rel_path)


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:, 2:] += rects[:, :2]
    return rects


def main(capture, sandbox_send, recv=None, files=None):
    logging.debug(TAG + "inside main")
    cascade_file = "cascades/haarcascade_frontalface_alt.xml"

    cascade = cv2.CascadeClassifier(full_path(cascade_file))
    if cascade.empty():
        # Failed to load cascades
        return False

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        original = frame.copy()
        gray = cv2.cvtColor(original, cv2.cv.CV_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = detect(gray, cascade)

        logging.debug(TAG + "sending obj")
        sandbox_send.send_pyobj(faces)

