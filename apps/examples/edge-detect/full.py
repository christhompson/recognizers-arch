
# Python recognizer edge-detect module

import cv2
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "edge-detect-full:"


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

        edges = cv2.cvtColor(frame, cv2.cv.CV_RGB2GRAY)
        edges = cv2.GaussianBlur(edges, (7, 7), 1.5, edges, 1.5)
        edges = cv2.Canny(edges, 0, 30, edges, 3)
        cv2.imshow("edges", edges)
        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break


logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
