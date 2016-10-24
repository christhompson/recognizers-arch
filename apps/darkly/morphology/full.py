import cv2
import numpy as np
import os
import logging
import argparse

TAG = "morphology-full:"
log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',

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
    logging.debug(TAG + "camera opened")

    def nothing(*args):
        pass
    
    cv2.namedWindow('Erosion window')
    cv2.namedWindow('Dilation window')
    cv2.createTrackbar('Erode', 'Erosion window', 1, 10, nothing)
    cv2.createTrackbar('Dilate', 'Dilation window', 1, 10, nothing)

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        erodelevel = cv2.getTrackbarPos('Erode', 'Erosion window')
        dilatelevel = cv2.getTrackbarPos('Dilate', 'Dilation window')

        # Erosion
        erodedest = cv2.erode(frame, None, None, (-1, -1), erodelevel)
        cv2.imshow('Erosion window', erodedest)

        # Dilation
        dilatedest = cv2.dilate(frame, None, None, (-1, -1), dilatelevel)
        cv2.imshow('Dilation window', dilatedest)


        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    main()
