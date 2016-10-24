import cv2
import numpy as np
import logging
import zmq

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ellipse-fitter-app:"

def main(data_recv, options_send):
    logging.debug(TAG + "inside main")

    height = 720
    width = 1280

    # Default options
    options = {'Threshold': 70}
    
    def option_change(int_option):
        options['Threshold'] = int_option
        logging.debug(TAG + "sending options " + str(options))
        options_send.send_json(options)


    cv2.namedWindow("Result", 1)
    cv2.createTrackbar("Threshold", "Result", 70, 255, option_change)

    # Create a poller object so we can async poll the socket
    poller = zmq.Poller()
    poller.register(data_recv, zmq.POLLIN)

    # Code for using video
    while True:
        # Check if we have an object on our recv socket
        # if so, read the object in and process and display
        # the resulting frame
        socks = dict(poller.poll(1000))
        if socks.get(data_recv) == zmq.POLLIN:
            frame_num, contours = data_recv.recv_pyobj()
            logging.debug(TAG + "received and decoded obj:num %d" % frame_num)

            # Creates the image to draw the contours and ellipses on
            output = np.zeros((height, width, 3), np.uint8)
            if contours != None:
                # This cycle draws all contours and approximate it by ellipses.
                for contour in contours:
                    # Number of points must be more than or equal to 6 (for cvFitEllipse_32f).
                    if len(contour) < 6:
                        continue

                    # Fits ellipse to current contour.
                    box = cv2.fitEllipse(contour)

                    # Draw current contour.
                    cv2.drawContours(output, contour, -1, (255, 255, 255))

                    # Draw ellipse.
                    cv2.ellipse(output, box, (255, 255, 255))
            cv2.imshow("Result", output)
            logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:  # exit on escape
            logging.debug(TAG + "received escape key")
            break

    return True

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()
