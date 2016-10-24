import cv2
import numpy as np
import os
import logging
import argparse

TAG = "hsv-hist-full:"
log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',

def calc_hist(hsv):
    scale = 10
    hist_size = [30, 32]
    hranges = [0, 180]
    sranges = [0, 255]
    channels = [0, 1]
    hist = cv2.calcHist([hsv], [0, 1], None, hist_size, hranges + sranges)
    max_val = np.amax(hist)
    big_hist = np.zeros(tuple(scale*s for s in hist.shape))
    for h in range(hist_size[0]):
        for s in range(hist_size[1]):
            bin_val = hist[h, s]
            intensity = int(round(bin_val*255/max_val))
            cv2.rectangle(
                    big_hist,
                    (h * scale, s * scale),
                    ((h + 1) * scale - 1, (s + 1) * scale - 1),
                    intensity,
                    -1)
    return big_hist
        

def main():
    logging.debug(TAG + "inside main")

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", help="capture from video file instead of from camera")
    parser.add_argument("-i", "--interactive", help="interactive mode -- require keypress between frames",
                        action='store_true')
    args = parser.parse_args()

    logging.debug(TAG + "done parsing arguments")

    capture = cv2.VideoCapture()
    if args.video:
        capture.open(args.video)
    else:
        capture.open(0)
    logging.debug(TAG + "camera opened")
    
    cv2.namedWindow('HSV')

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        hsv = cv2.cvtColor(frame, cv2.cv.CV_BGR2HSV)
        big_hist = calc_hist(hsv)
        # divide by 256 because cv2 is annoying about showing doubles
        cv2.imshow('HSV', big_hist/256)
        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    main()
