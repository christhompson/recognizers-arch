import cv2
import numpy as np
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "corner-finder-app:"


def main(data_recv, results_send):
    logging.debug(TAG + "inside main")
    while True:
        data_recv.poll()
        frame_num,corners,shape = data_recv.recv_pyobj()
        logging.debug(TAG + "received and decoded obj:num %d" % frame_num)
        canvas = np.zeros(shape, np.uint8)

        for corner in corners:
            cv2.circle(canvas, tuple(corner[0]), 5, (0, 0, 255), -1)

        cv2.imshow("corners", canvas)

        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break
