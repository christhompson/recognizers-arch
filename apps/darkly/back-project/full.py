import cv2
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "back-project-full:"

def calc_hist(hsv):
    scale = 3
    hist_size = cv2.getTrackbarPos("Bins", "Back Projection")
    hranges = [0, 180]
    hist = cv2.calcHist([hsv], [0], None, [hist_size], hranges)
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    max_val = 255
    width = 400
    height = 400
    bin_width = width / hist_size
    big_hist = np.zeros((height, width, 3))
    for h in range(hist_size):
        bin_val = hist[h]
        intensity = int(round(bin_val*height/max_val))
        cv2.rectangle(
                big_hist,
                (h * bin_width, height - intensity),
                ((h + 1) * bin_width - 1, height),
                (0, 0, 255),
                -1)
    return hist, big_hist

def calc_backproj(hsv, hist):
    hranges = [0, 180]
    channels = [0]
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    backproj = cv2.calcBackProject([hsv], channels, hist, hranges, 1)
    return backproj

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

    def nothing(*args):
        pass

    logging.debug(TAG + "camera opened")
    cv2.namedWindow("HSV Histogram")
    cv2.namedWindow("Back Projection")
    cv2.createTrackbar("Bins", "Back Projection", 20, 180, nothing)

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        hsv = cv2.cvtColor(frame, cv2.cv.CV_BGR2HSV)
        hist, hist_drawing = calc_hist(hsv)
        back = calc_backproj(hsv, hist)

        # divide by 256 because cv2 is annoying about showing doubles
        cv2.imshow("HSV Histogram", hist_drawing/256)
        cv2.imshow("Back Projection", back)

        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) != -1:  # exit on escape
            logging.debug(TAG + "received escape key")
            break
    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
