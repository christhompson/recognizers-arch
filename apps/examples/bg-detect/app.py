import cv2
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "bg-detect-app:"


def main(data_recv, results_send):
    logging.debug(TAG + "inside main")
    while True:
        data_recv.poll()

        foreground_mask = data_recv.recv_pyobj()
        logging.debug(TAG + "received and decoded obj")

        cv2.imshow("frame", foreground_mask)

        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

        # Send it back to proxy
        # logging.debug(TAG + "sending obj")
        # results_send.send_pyobj(foreground_mask)
