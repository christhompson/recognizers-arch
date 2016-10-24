# Based off code from OpenCV website
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#@source https://github.com/Itseez/opencv/blob/master/samples/cpp/tutorial_code/Histograms_Matching/MatchTemplate_Demo.cpp

import cv2
import numpy as np
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "template-matcher-app:"

image_window = "Source Image"

def draw_rects(img, rects, color):
    #for x1, y1, x2, y2 in rects:
    (x1, y1), (x2, y2) = rects
    # x1 = int(rects[0][0])
    # y1 = int(rects[0])
    # x2 = int(rects[2])
    # y2 = int(rects[3])
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2, 8, 0)

    # cv2.rectangle(img, matchLoc, (matchLoc[0] + template_img.shape[1],
    #     matchLoc[1] + template_img.shape[0]), color, 2, 8, 0)


def main(data_recv, options_send):
    logging.debug(TAG + "inside main")

    cv2.namedWindow(image_window, cv2.CV_WINDOW_AUTOSIZE)

    options = {'Method': 0}
        
    def option_change(int_option):
        options['Method'] = int_option
        logging.debug(TAG + "sending options " + str(options))
        options_send.send_json(options)

    match_method = 0;
    max_Trackbar = 5;
    trackbar_label = "Method: \n 0: SQDIFF \n 1: SQDIFF NORMED \n 2: TM CCORR \n 3: TM CCORR NORMED \n 4: TM CCOEFF \n 5: TM CCOEFF NORMED";
    cv2.createTrackbar(trackbar_label, image_window, match_method, max_Trackbar, option_change);

    # Create a poller object so we can async poll the socket
    poller = zmq.Poller()
    poller.register(data_recv, zmq.POLLIN)

    while True:
        # Check if we have an object on our recv socket
        # if so, read the object in and process and display
        # the resulting frame
        socks = dict(poller.poll(1000))
        if socks.get(data_recv) == zmq.POLLIN:
            frame_num, rects = data_recv.recv_pyobj()
            logging.debug(TAG + "received and decoded obj:num %d" % frame_num)

            # visualize on black image of same size
            height = 720
            width = 1280

            output = np.zeros([height, width, 3], np.uint8)
            output[:, 0:width] = (255, 255, 255)  # convert to white

            draw_rects(output, rects, (0, 255, 0))
            # draw_rects(img, subrects, (255, 0, 0))
            cv2.imshow(image_window, output)
            logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break