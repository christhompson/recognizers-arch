import cv2
import numpy as np
import os
import logging
import argparse

TAG = "hist-calc-full:"
log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
        

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
    
    cv2.namedWindow("hist-calc", cv2.WINDOW_AUTOSIZE)

    hist_size = 256
    hist_range = [0, 255]
    hist_w = 512
    hist_h = 400
    bin_w = int(round(float(hist_w) / hist_size))

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        blue, green, red = cv2.split(frame)
        # parameters:
        # [blue] = list of images
        # [0] = list of channels to calculate for
        # None = mask
        # [256] = number of bins of output histogram
        # [0, 255] = lower, upper bound on histogram bins
        b_hist = cv2.calcHist([blue], [0], None, [hist_size], hist_range)
        g_hist = cv2.calcHist([green], [0], None, [hist_size], hist_range)
        r_hist = cv2.calcHist([red], [0], None, [hist_size], hist_range)

        hist_image = np.zeros([hist_h, hist_w, 3], dtype=np.uint8)

        cv2.normalize(b_hist, b_hist, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(g_hist, g_hist, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(r_hist, r_hist, 0, 255, cv2.NORM_MINMAX)

        for i in range(hist_size):
            cv2.line(hist_image, (bin_w * (i - 1), hist_h - int(round(b_hist[i-1]))),
                                 (bin_w * i, hist_h - int(round(b_hist[i]))),
                                 (255, 0, 0), 2, 8, 0);
            cv2.line(hist_image, (bin_w * (i - 1), hist_h - int(round(g_hist[i-1]))),
                                 (bin_w * i, hist_h - int(round(r_hist[i]))),
                                 (0, 255, 0), 2, 8, 0);
            cv2.line(hist_image, (bin_w * (i - 1), hist_h - int(round(r_hist[i-1]))),
                                 (bin_w * i, hist_h - int(round(r_hist[i]))),
                                 (0, 0, 255), 2, 8, 0);
        cv2.imshow("hist-calc", hist_image);
        logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    main()
