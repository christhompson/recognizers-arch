
import cv2
import numpy as np
import os
import argparse
import logging
from math import sqrt

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "square-detector-full:"


def angle(pt1, pt2, pt0):
    dx1 = pt1[0] - pt0[0]
    dy1 = pt1[1] - pt0[1]
    dx2 = pt2[0] - pt0[0]
    dy2 = pt2[1] - pt0[1]
    tmp = (dx1*dx1 + dy1*dy1)*(dx2*dx2 + dy2*dy2) + 1e-10
    return (dx1*dx2 + dy1*dy2) / sqrt(tmp);


def detect(img, threshold):
    height, width, depth = img.shape
    timg = img.copy()
    pyr = np.zeros((height/2, width/2, depth), np.uint8)

    cv2.pyrDown(timg, pyr)
    cv2.pyrUp(pyr, timg)

    squares = []
    N = 11
    # creates a kernel
    kernel = np.ones((5, 5), np.uint8)

    for channel in cv2.split(timg):
        for level in range(N):
            gray = None
            if level == 0:
                gray = cv2.Canny(channel, 0, threshold, apertureSize=5)
                gray = cv2.dilate(gray, kernel)
            else:
                ret, gray = cv2.threshold(channel, (level+1)*255/N, 255, cv2.THRESH_BINARY)

            contours, h = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                epsilon = cv2.arcLength(contour, True)*0.02
                poly = cv2.approxPolyDP(contour, epsilon, closed=True)
                area = cv2.contourArea(poly)
                poly_double = poly.astype(np.float64)
                if len(poly) == 4 and abs(area) > 1000 and cv2.isContourConvex(poly):
                    s = 0
                    for i in range(2, 4):
                        t = abs(angle(poly_double[i][0], poly_double[i-2][0], poly_double[i-1][0]))
                        s = s if s > t else t

                    if s < 0.3:
                        squares.append((poly[0], poly[2]))

    return squares


def drawSquares(img, squares):
    for square in squares:
        pt1, pt2 = square
        # Gross conversions to tuples to get past awful "getargs" error
        cv2.rectangle(img, tuple(pt1[0]), tuple(pt2[0]), [0, 255, 0], 3, 8)


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

    cv2.namedWindow("square_detector")

    def nothing(*args):
        pass

    cv2.createTrackbar("threshold", "square_detector", 50, 1000, nothing)

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        threshold = cv2.getTrackbarPos("threshold", "square_detector")
        squares = detect(frame, threshold)

        height, width, depth = frame.shape
        blank = np.ones((height, width, depth), np.uint8)
        blank[:, 0:width] = (255, 255, 255)  # convert to white

        drawSquares(blank, squares)
        cv2.imshow("square_detector", blank)
        logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
