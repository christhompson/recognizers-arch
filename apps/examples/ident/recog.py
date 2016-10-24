import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ident-recog:"


def main(capture, sandbox_send, files):
    logging.debug(TAG + "inside main")

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        logging.debug(TAG + "sending obj")
        sandbox_send.send_pyobj(frame)
