import cv2
import numpy as np
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "priv-video-app:"

def main(data_recv, results_send):
    logging.debug(TAG + "inside main")
    while True:
        data_recv.poll()
        frame_num, foreground = data_recv.recv_pyobj()
        
        logging.debug(TAG + "received and decoded obj:num %d" % frame_num)

        #have to convert image back to numpy array before we can show it
        foreground = np.array(foreground).astype(np.uint8)
        cv2.imshow("Foreground", foreground)
        logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break