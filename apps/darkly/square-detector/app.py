import cv2
import numpy as np
import os
import argparse
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "square-detector-app:"


def drawSquares(img, squares):
    for square in squares:
        pt1, pt2 = square
        # Gross conversions to tuples to get past awful "getargs" error
        cv2.rectangle(img, tuple(pt1[0]), tuple(pt2[0]), [0, 255, 0], 3, 8)


def main(data_recv, options_send):
    logging.debug(TAG + "inside main")

    cv2.namedWindow("square_detector")
    
    # Create a poller object so we can async poll the socket
    poller = zmq.Poller()
    poller.register(data_recv, zmq.POLLIN)
    options = {'Threshold': 50}
        
    def option_change(int_option):
        options['Threshold'] = int_option
        logging.debug(TAG + "sending options " + str(options))
        options_send.send_json(options)

    cv2.createTrackbar("Threshold", "square_detector", 50, 1000, option_change)

    while True:
#        threshold = cv2.getTrackbarPos('Threshold', 'square_detector')
#        if threshold != options['Threshold']:
#            logging.debug(TAG + "sending options " + str(options))
#            options_send.send_json(options)

        # Check if we have an object on our recv socket
        # if so, read the object in and process and display
        # the resulting frame
        socks = dict(poller.poll(100))
        if socks.get(data_recv) == zmq.POLLIN:
            frame_num, squares = data_recv.recv_pyobj()
            logging.debug(TAG + "received and decoded obj:num %d" % frame_num)

            height = 720
            width = 1280
            blank = np.ones((height, width, 3), np.uint8)
            blank[:, 0:width] = (255, 255, 255)  # convert to white

            drawSquares(blank, squares)
            cv2.imshow("square_detector", blank)
            logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break