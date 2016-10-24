
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
# 
# @brief Sample code using Sobel and/orScharr OpenCV functions to make a simple Edge Detector
# Tutorial: http://docs.opencv.org/doc/tutorials/imgproc/imgtrans/sobel_derivatives/sobel_derivatives.html
# Code: https://github.com/Itseez/opencv/blob/master/samples/cpp/tutorial_code/ImgTrans/Sobel_Demo.cpp
# @author OpenCV team

import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "sobel-full:"

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

    window_name = "Sobel Demo - Simple Edge Detector";
    scale = 1;
    delta = 0;
    ddepth = cv2.CV_16S

    cv2.namedWindow(window_name, 0)

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        img_blur = cv2.GaussianBlur(frame, (3, 3), 0, sigmaY=0)

        # Converts it to grayscale
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_RGB2GRAY)

        # gradient x
        grad_x = cv2.Sobel(img_gray, ddepth, dx=1, dy=0, ksize=3, scale=scale, delta=delta)
        abs_grad_x = cv2.convertScaleAbs(grad_x)

        # gradient Y
        grad_y = cv2.Sobel(img_gray, ddepth, dx=0, dy=1, ksize=3, scale=scale, delta=delta)
        abs_grad_y = cv2.convertScaleAbs(grad_y)

        # Total Gradient (approximate)
        grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

        # show the sobeled image
        cv2.imshow(window_name, grad)
        logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break
    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
