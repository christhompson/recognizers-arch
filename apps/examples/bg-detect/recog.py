import cv2
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "bg-detect-recog:"


def main(capture, sandbox_send, sandbox_recv, files=None):
    logging.debug(TAG + "inside main")
    # capture = cv2.VideoCapture()
    # capture.open(0)
    # width = 640
    # height = 480
    # capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)
    # capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
    # if not capture.isOpened():
    #     return False

    bg = cv2.BackgroundSubtractorMOG()

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")

        # img = np.ones((height, width, 3), np.uint8)
        foreground_mask = bg.apply(frame)

        logging.debug(TAG + "sending obj")
        sandbox_send.send_pyobj(foreground_mask)
