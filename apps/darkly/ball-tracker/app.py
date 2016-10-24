import cv2
import numpy as np
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ball-tracker-app:"

def main(data_recv, results_send):
    logging.debug(TAG + "inside main")
    frameCounter = 0
    while True:
        data_recv.poll()
        frame_num, (posX, posY, lastX, lastY) = data_recv.recv_pyobj()
        
        logging.debug(TAG + "received and decoded obj:num %d" % frame_num)
        # visualize on black image of same size
        height = 720
        width = 1280
        if frameCounter == 0:
            img = np.ones((height, width, 3), np.uint8)

        cv2.line(img, (int(posX), int(posY)),
                      (int(lastX), int(lastY)), (255, 255, 255), 5, 8)

        cv2.imshow("ball", img)
        logging.debug(TAG + "displayed image")

        frameCounter = frameCounter + 1
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break