import cv2
import numpy as np
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "hist-calc-app:"


def main(data_recv, results_send):
    logging.debug(TAG + "inside main")
    cv2.namedWindow("hist-calc", cv2.WINDOW_AUTOSIZE)

    hist_size = 256
    hist_range = [0, 255]
    hist_w = 512
    hist_h = 400
    bin_w = int(round(float(hist_w) / hist_size))

    while True:
        data_recv.poll()
        frame_num, b_hist, g_hist, r_hist = data_recv.recv_pyobj()
        logging.debug(TAG + "received and decoded obj:num %d" % frame_num)

        hist_image = np.zeros([hist_h, hist_w, 3], dtype=np.uint8)

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
