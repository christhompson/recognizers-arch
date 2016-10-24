# Based off code from OpenCV website
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#@source https://github.com/Itseez/opencv/blob/master/samples/cpp/tutorial_code/Histograms_Matching/MatchTemplate_Demo.cpp

import cv2
import cv
import numpy as np
import os
import argparse
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "template-matcher-full:"

# constants
template_file_name = "template_video.png"
image_window = "Source Image"


def full_path(rel_path):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, rel_path)


def get_match(match_method, input_img, template_img):
    height, width, depth = input_img.shape
    output = np.zeros([height, width, depth], np.uint8)
    output[:, 0:width] = (255, 255, 255)  # convert to white


    # Do the Matching and Normalize
    result = cv2.matchTemplate(input_img, template_img, match_method)
    result = cv2.normalize(result, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=-1)

    # Localizing the best match with minMaxLoc
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)

    # For SQDIFF and SQDIFF_NORMED, the best matches are lower values. For all the other methods, the higher the better
    if match_method  == cv2.TM_SQDIFF or match_method == cv2.TM_SQDIFF_NORMED:
        matchLoc = minLoc
    else:
        matchLoc = maxLoc

    #draws the rectangle around the template
    cv2.rectangle(output, matchLoc, (matchLoc[0] + template_img.shape[1],
        matchLoc[1] + template_img.shape[0]), (0, 0, 0), 2, 8, 0)
    # cv2.rectangle(result, matchLoc, (matchLoc[0] + template_img.shape[1],
    #     matchLoc[1] + template_img.shape[0]), (0, 0, 0), 2, 8, 0)

    #shows the images
    cv2.imshow(image_window, output)
    # cv2.imshow( "result" , result )

def main():
    logging.debug(TAG + "inside main")
    
    # Load the template image.
    template_image = cv2.imread(full_path(template_file_name), 1)

    #used for capturing from a video file
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", help="capture from video file instead of from camera")
    args = parser.parse_args()

    logging.debug(TAG + "done parsing arguments")
    capture = cv2.VideoCapture()
    if args.video:
        capture.open(args.video)
    else:
        capture.open(0)
    if not capture.isOpened():
        # Failed to open camera
        return False

    logging.debug(TAG + "camera opened")
    cv2.namedWindow(image_window, cv2.CV_WINDOW_AUTOSIZE)
    def nothing(*args):
        pass

    match_method = 0;
    max_Trackbar = 5;
    trackbar_label = "Method: \n 0: SQDIFF \n 1: SQDIFF NORMED \n 2: TM CCORR \n 3: TM CCORR NORMED \n 4: TM CCOEFF \n 5: TM CCOEFF NORMED";
    cv2.createTrackbar(trackbar_label, image_window, match_method, max_Trackbar, nothing);

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")
        
        #tries to find the matching template
        match_method = cv2.getTrackbarPos(trackbar_label, image_window)
        get_match(match_method, frame, template_image)
        logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27: # exit on escape
            logging.debug(TAG + "received escape key")
            break

logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()