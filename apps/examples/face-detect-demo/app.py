import cv2
import numpy as np
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "face-detect-app:"


def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)


def main(data_recv, results_send):
    logging.debug(TAG + "inside main")
    while True:
        data_recv.poll()
        faces = data_recv.recv_pyobj()
        logging.debug(TAG + "received and decoded obj")
        # visualize on black image of same size
        height = 720
        width = 1280
        img = np.ones((height, width, 3), np.uint8)
        img[:, 0:width] = (255, 255, 255)  # convert to white

        draw_rects(img, faces, (0, 255, 0))
        # draw_rects(img, subrects, (255, 0, 0))
        cv2.imshow("face_detector", img)
        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

        # logging.debug(TAG + "sending obj")
        # results_send.send_pyobj(faces)