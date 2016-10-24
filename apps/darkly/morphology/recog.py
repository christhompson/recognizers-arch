import cv2
import os
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "morphology-recog:"


def main(capture, sandbox_send, sandbox_recv, files=None):
    logging.debug(TAG + "inside main")

    # Default options
    options = {'Erode': 1, 'Dilate': 1}

    # Set up poller to async check our recv socket
    poller = zmq.Poller()
    poller.register(sandbox_recv, zmq.POLLIN)

    frame_num = 0
    while True:
        # Read in from recv socket (might not have anything)
        socks = dict(poller.poll(100))
        if socks.get(sandbox_recv) == zmq.POLLIN:
            options = sandbox_recv.recv_json()
            logging.debug(TAG + "received options update from proxy")

        erodelevel = options['Erode']
        dilatelevel = options['Dilate']

        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        # Erosion
        erodedest = cv2.erode(frame, None, None, (-1, -1), erodelevel)

        # Dilation
        dilatedest = cv2.dilate(frame, None, None, (-1, -1), dilatelevel)

        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, erodedest, dilatedest))

    return True
