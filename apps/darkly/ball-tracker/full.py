#
# Based on code by Utkarsh Sinha
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#
# Brought in code from https://github.com/liquidmetal/AI-Shack--Tracking-with-OpenCV/blob/master/TrackColour.cpp
#

import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ball-tracker-full:"


def main():
    logging.debug(TAG + "inside main")

    #used for capturing from a video file
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

    hsv_min = (50, 100, 100)
    hsv_max = (70, 255, 255)

    posX = 0
    posY = 0

    frameCounter = 0
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        if frameCounter == 0:
            imgScribble = np.zeros(frame.shape, np.uint8)

        # Holds the yellow thresholded image (yellow = white, rest = black)
        imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        imgThresh = cv2.inRange(imgHSV, hsv_min, hsv_max)

        # Calculate the moments to estimate the position of the ball
        moments = cv2.moments(imgThresh)

        # Gets the actual moment values
        moment10 = moments['m10']
        moment01 = moments['m01']
        area = moments['m00']

        lastX = posX
        lastY = posY

        if area != 0:
            posX = moment10 / area
            posY = moment01 / area

        # logging.debug(TAG + "position (" + str(int(posX)) + "," + str(int(posY)) + ")")

        if (lastX > 0 and lastY > 0 and posX > 0 and posY > 0):
            #Draw a yellow line from the previous point to the current point
            cv2.line(imgScribble, (int(posX), int(posY)),
                     (int(lastX), int(lastY)), (255, 255, 255), 5, 8)

        cv2.imshow("ball", imgScribble)
        logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

        frameCounter = frameCounter + 1
    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
