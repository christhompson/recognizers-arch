import cv2
import numpy as np
import logging
import time

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ocr-digit-app:"

def main(data_recv, results_send):
    logging.debug(TAG + "inside main")
    while True:
        data_recv.poll()
        frame_num, line = data_recv.recv_pyobj()
        
        logging.debug(TAG + "received and decoded obj:num %d" % frame_num)
        # logs the digit that we recognized
        logging.debug(TAG + "recognized digit: " + str(line[0]))
        logging.debug(TAG + "displayed image")
        
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break