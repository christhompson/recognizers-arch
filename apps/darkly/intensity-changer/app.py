import cv2
import numpy as np
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "intensity-changer-app:"

# method which draws a histogram for the image, given the image
# taken from https://raw.github.com/Itseez/opencv/master/samples/python2/hist.py
# Abid Rahman 3/14/12 debug Gary Bradski
def draw_hist(hist):
    h = np.zeros((300,256,3))
    for x,y in enumerate(hist):
        cv2.line(h,(x,0),(x,y),(255,255,255))
    y = np.flipud(h)
    return y

def main(data_recv, options_send):
    logging.debug(TAG + "inside main")

    # Default options
    options = {'Brightness': 100, 'Contrast': 100}
    
    def brightness_change(int_option):
        options['Brightness'] = int_option
        logging.debug(TAG + "sending options " + str(options))
        options_send.send_json(options)

    def contrast_change(int_option):
        options['Contrast'] = int_option
        logging.debug(TAG + "sending options " + str(options))
        options_send.send_json(options)

    # Create a poller object so we can async poll the socket
    poller = zmq.Poller()
    poller.register(data_recv, zmq.POLLIN)

    cv2.namedWindow("histogram")
    cv2.createTrackbar("Brightness", "histogram", 100, 200, brightness_change)
    cv2.createTrackbar("Contrast", "histogram", 100, 200, contrast_change)

    while True:
        # Check if we have an object on our recv socket
        # if so, read the object in and process and display
        # the resulting frame
        socks = dict(poller.poll(1000))
        if socks.get(data_recv) == zmq.POLLIN:
            frame_num, hist_arr = data_recv.recv_pyobj()
            logging.debug(TAG + "received and decoded obj:num %d" % frame_num)
            # draws the histogram object
            hist = draw_hist(hist_arr)

            #show the image
            cv2.imshow("histogram", hist)
            logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break