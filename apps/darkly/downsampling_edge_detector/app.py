import cv2
import numpy as np
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "edge-detect-app:"

def main(data_recv, options_send):
    logging.debug(TAG + "inside main")

    # Create window
    cv2.namedWindow('edge_detector')

    while True:
        data_recv.poll()
        frame_num, edges = data_recv.recv_pyobj()
        logging.debug(TAG + "received and decoded obj:num %d" % frame_num)
        cv2.imshow("edge_detector", edges)
        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break
    return True
