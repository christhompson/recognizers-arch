import cv2
import numpy as np
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "back-project-app:"

def draw_hist(hist, bins):
    max_val = 255
    width = 400
    height = 400
    bin_width = width / bins
    big_hist = np.zeros((height, width, 3))
    for h in range(bins):
        bin_val = hist[h]
        intensity = int(round(bin_val*height/max_val))
        cv2.rectangle(
                big_hist,
                (h * bin_width, height - intensity),
                ((h + 1) * bin_width - 1, height),
                (0, 0, 255),
                -1)
    return big_hist

def main(data_recv, options_send):
    # Default options
    options = {'Bins': 50}
    
    def option_change(int_option):
        options['Bins'] = int_option
        logging.debug(TAG + "sending options " + str(options))
        options_send.send_json(options)

    logging.debug(TAG + "inside main")

    cv2.namedWindow("HSV Histogram")
    cv2.namedWindow("Back Projection")
    cv2.createTrackbar("Bins", "Back Projection", 20, 180, option_change)
   
    # Create a poller object so we can async poll the socket
    poller = zmq.Poller()
    poller.register(data_recv, zmq.POLLIN)

    while True:
        # Check if we have an object on our recv socket
        # if so, read the object in and process and display
        # the resulting frame
        socks = dict(poller.poll(1000))
        if socks.get(data_recv) == zmq.POLLIN:
            frame_num, hist, back, hist_bins = data_recv.recv_pyobj()
            logging.debug(TAG + "received and decoded obj:num %d" % frame_num)
            hist_drawing = draw_hist(hist, hist_bins)

            cv2.imshow("HSV Histogram", hist_drawing/256)
            cv2.imshow("Back Projection", back)
            logging.debug(TAG + "displayed image")
        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break
