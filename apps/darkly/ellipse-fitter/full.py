#
#  This program is demonstration for ellipse fitting. Program finds
#  contours and approximate it by ellipses.
#
#  Trackbar specify threshold parametr.
#
#  White lines is contours. Red lines is fitting ellipses.
#
#
#  Author:  Denis Burenkov.
#  Source Code: https://code.ros.org/trac/opencv/browser/trunk/opencv/samples/c/fitellipse.c?rev=1429
#  Converted to Python by Eric Shen <ericshen@berkeley.edu>
#

import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ellipse-fitter-full:"

# callback that trackbars will call
def nothing(arg):
    pass

def main():
    logging.debug(TAG + "inside main")
    # used for capturing from a video file
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
    
    # creates windows
    cv2.namedWindow("Result", 1)
    
    # creates a trackbar
    cv2.createTrackbar('Threshold', 'Result', 70, 255, nothing)
    
    # Code for using video
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        threshold = cv2.getTrackbarPos('Threshold', 'Result')

        # Threshold the source image. This needful for cvFindContours().
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        retval, thresholded = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        # Creates the image to draw the contours and ellipses on
        h, w, _ = frame.shape
        output = np.zeros((h, w, 3), np.uint8)

        # This cycle draws all contours and approximate it by ellipses.
        for contour in contours:
            # Number of points must be more than or equal to 6 (for cvFitEllipse_32f).
            if len(contour) < 6:
                continue

            # Fits ellipse to current contour.
            box = cv2.fitEllipse(contour)

            # Draw current contour.
            cv2.drawContours(output, contour, -1, (255, 255, 255))

            # Draw ellipse.
            cv2.ellipse(output, box, (255, 255, 255))

        # Show image. HighGUI use.
        cv2.imshow("Result", output)
        logging.debug(TAG + "displayed image")
        
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
