
# Python app module edge-detect
# Simply redirects data back to proxy

import cv2
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "edge-detect-app:"


def main(data_recv, results_send):
    logging.debug(TAG + "inside main")
    while True:
        data_recv.poll()
        # Have data now
        edges = data_recv.recv_pyobj()
        logging.debug(TAG + "received and decoded obj")
        # Obj is edges from image, we'll display in a window
        cv2.imshow("edges", edges)
        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

        # Send it back to proxy
        # logging.debug(TAG + "sending obj")
        # results_send.send_pyobj(edges)
