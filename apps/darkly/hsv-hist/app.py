import cv2
import numpy as np
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "hsv-hist-app:"


def main(data_recv, results_send):
    logging.debug(TAG + "inside main")

    while True:
        data_recv.poll()
        frame_num, hist = data_recv.recv_pyobj()
        logging.debug(TAG + "received and decoded obj:num %d" % frame_num)

        max_val = np.amax(hist)
        scale = 10
        hist_size = [30, 32]
        hranges = [0, 180]
        sranges = [0, 255]
        channels = [0, 1]
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
        # divide by 256 because cv2 is annoying about showing doubles
        cv2.imshow('HSV', big_hist/256)

        logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break
