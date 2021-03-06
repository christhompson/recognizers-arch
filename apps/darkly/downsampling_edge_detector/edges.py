
import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "edge-detector-full:"


def detectEdges(img):
    height, width, depth = img.shape
    # pyr = np.zeros((height/2, width/2, depth), np.uint8)
    # cv2.pyrDown(img, pyr)
    timg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(timg, 10, 100, apertureSize=3)
    return edges


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

    # Create window
    cv2.namedWindow('edge_detector')

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        edges = detectEdges(frame)
        out = np.zeros(frame.shape, np.uint8)

        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for i in xrange(len(contours)):
            # has parent, inner (hole) contour of a closed edge
            # print hierarchy[i]
            # print hierarchy[0][i][3]
            if (hierarchy[0][i][3] >= 0):
                cv2.drawContours(out, contours, i, (255, 255, 255), 1, 8)

        cv2.imshow("frame", frame)
        cv2.imshow("edges", out)
        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
