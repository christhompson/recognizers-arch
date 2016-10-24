import os
import cv2
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "hist-calc-recog:"


def main(capture, sandbox_send, sandbox_recv, files):
    logging.debug(TAG + "inside main")

    hist_size = 256
    hist_range = [0, 255]

    frame_num = 0
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        frame_num += 1
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

        cv2.normalize(b_hist, b_hist, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(g_hist, g_hist, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(r_hist, r_hist, 0, 255, cv2.NORM_MINMAX)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, b_hist, r_hist, g_hist))

