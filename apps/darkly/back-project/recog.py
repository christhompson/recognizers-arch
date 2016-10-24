import os
import cv2
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "back-project-recog:"

def calc_hist(hsv, bins):
    scale = 3
    hist_size = bins
    hranges = [0, 180]
    hist = cv2.calcHist([hsv], [0], None, [hist_size], hranges)
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    return hist

def calc_backproj(hsv, hist):
    hranges = [0, 180]
    channels = [0]
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
    backproj = cv2.calcBackProject([hsv], channels, hist, hranges, 1)
    return backproj

def main(capture, sandbox_send, sandbox_recv, files=None):
    logging.debug(TAG + "inside main")
    # Default options
    options = {'Bins': 20}

    # Set up poller to async check our recv socket
    poller = zmq.Poller()
    poller.register(sandbox_recv, zmq.POLLIN)

    frame_num = 0
    while True:
        socks = dict(poller.poll(100))
        if socks.get(sandbox_recv) == zmq.POLLIN:
            options = sandbox_recv.recv_json()
            logging.debug(TAG + "received options update from proxy")

        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        hsv = cv2.cvtColor(frame, cv2.cv.CV_BGR2HSV)
        hist = calc_hist(hsv, options["Bins"])
        back = calc_backproj(hsv, hist)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, hist, back, options["Bins"]))
