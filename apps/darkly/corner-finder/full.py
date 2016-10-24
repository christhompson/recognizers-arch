
# Python recognizer corner-finder module

import cv2
import argparse
import logging
import os
import numpy as np

MAX_CORNERS = 20

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "corner-finder-full:"

def main():
    logging.debug(TAG + "inside main")

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", help="capture from video file instead of from camera")
    args = parser.parse_args()

    logging.debug(TAG + "done parsing arguments")

    capture = cv2.VideoCapture()
    if args.video:
        capture.open(args.video)
    else:
        capture.open(0)
    if not capture.isOpened():
        # Failed to open camera
        return False
    logging.debug(TAG + "camera opened")

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        output = np.zeros(frame.shape, np.uint8)

        grayscale = cv2.cvtColor(frame, cv2.cv.CV_RGB2GRAY)
        corners = cv2.goodFeaturesToTrack(grayscale, MAX_CORNERS, .01, 20)
        for corner in corners:
            cv2.circle(output, tuple(corner[0]), 5, (255, 0, 0), -1, 8, 0)

        cv2.imshow("corners", output)
        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break


logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
