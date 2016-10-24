import cv2
import numpy as np
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "hand-detector-app:"

def main(data_recv, results_send):
    logging.debug(TAG + "inside main")
    while True:
        data_recv.poll()
        frame_num, hsv_mask = data_recv.recv_pyobj()
        
        logging.debug(TAG + "received and decoded obj:num %d" % frame_num)

        #have to convert image back to numpy array before we can show it
        # img = np.array(img).astype(np.uint8)
        cv2.namedWindow("hsv_mask", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("hsv_mask", hsv_mask)
        
        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break