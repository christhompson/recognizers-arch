import cv2
import numpy as np
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "morphology-app:"


def main(data_recv, options_send):
    logging.debug(TAG + "inside main")
    
    # Default options
    options = {'Erode': 1, 'Dilate': 1}
    
    def erode_change(int_option):
        options['Erode'] = int_option
        logging.debug(TAG + "sending options " + str(options))
        options_send.send_json(options)

    def dilate_change(int_option):
        options['Dilate'] = int_option
        logging.debug(TAG + "sending options " + str(options))
        options_send.send_json(options)

    # Create window
    cv2.namedWindow('Erosion window')
    cv2.namedWindow('Dilation window')
    # Create trackbar
    cv2.createTrackbar('Erode', 'Erosion window', 1, 10, erode_change)
    cv2.createTrackbar('Dilate', 'Dilation window', 1, 10, dilate_change)

    # Create a poller object so we can async poll the socket
    poller = zmq.Poller()
    poller.register(data_recv, zmq.POLLIN)

    while True:
        # Check if we have an object on our recv socket
        # if so, read the object in and process and display
        # the resulting frame
        socks = dict(poller.poll(1000))
        if socks.get(data_recv) == zmq.POLLIN:
            frame_num, erodedest, dilatedest = data_recv.recv_pyobj()
            logging.debug(TAG + "received and decoded obj:num %d" % frame_num)
            cv2.imshow('Erosion window', erodedest)
            cv2.imshow('Dilation window', dilatedest)
            logging.debug(TAG + "displayed image")
        
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

    return True
