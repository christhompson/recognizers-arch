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
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "face-detect-app:"


def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)


def nothing(x):
    pass


def main(data_recv, options_send):
    logging.debug(TAG + "inside main")

    # Create window
    cv2.namedWindow('image')
    # Create trackbar
    # cv2.createTrackbar('Face', 'image', 0, 1, nothing)
    # Create switch
    switch = '0 : OFF \n1 : ON'
    cv2.createTrackbar(switch, 'image', 0, 1, nothing)

    # Create a poller object so we can async poll the socket
    poller = zmq.Poller()
    poller.register(data_recv, zmq.POLLIN)

    while True:
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

        # get value of trackbar, put it into an options dictionary
        # (with a single "enable" key), and send it as JSON
        # face_pos = cv2.getTrackbarPos('Face', 'image')
        switch_pos = cv2.getTrackbarPos(switch, 'image')
        options = {'enable': int(switch_pos)}
        logging.debug(TAG + "sending options " + str(options))
        options_send.send_json(options)

        # Check if we have an object on our recv socket
        # if so, read the object in and process and display
        # the resulting frame
        socks = dict(poller.poll(100))
        if socks.get(data_recv) == zmq.POLLIN:
            faces = data_recv.recv_pyobj()
            height = 720
            width = 1280
            blank = np.ones((height, width, 3), np.uint8)
            blank[:, 0:width] = (255, 255, 255)  # convert to white

            draw_rects(blank, faces, (0, 255, 0))
            cv2.imshow("image", blank)
            logging.debug(TAG + "displayed image")

    return True
