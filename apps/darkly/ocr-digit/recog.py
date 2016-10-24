#
# Based on code by Utkarsh Sinha
# Converted to Python by Eric Shen <ericshen@berkeley.edu>
#
# Brought in code from https://github.com/liquidmetal/AI-Shack--Tracking-with-OpenCV/blob/master/TrackColour.cpp
#

import cv2
import numpy as np
import os
import argparse
import logging
import time

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ocr-digit-recog:"

#method that trains a KNearest object, and returns it
#also tests it with sample data.
def preprocess_train_test():
    img = cv2.imread('apps/darkly/ocr-digit/digits.png')

    thresholdArray = cv2.threshold(img, 10, 255, cv2.THRESH_BINARY)
    thresholded = thresholdArray[1]
    gray = cv2.cvtColor(thresholded,cv2.COLOR_BGR2GRAY)

    # Now we split the image to 5000 cells, each 20x20 size
    cells = [np.hsplit(row,100) for row in np.vsplit(gray,50)]

    # Make it into a Numpy array. It size will be (50,100,20,20)
    x = np.array(cells)

    # Now we prepare train_data and test_data.
    train = x[:,:].reshape(-1,400).astype(np.float32) # Size = (2500,400)
    # test = x[:,50:100].reshape(-1,400).astype(np.float32) # Size = (2500,400)

    # Create labels for train and test data
    k = np.arange(10)
    train_labels = np.repeat(k,500)[:,np.newaxis]
    # test_labels = train_labels.copy()

    # Initiate kNN, train the data, then test it with test data for k=1
    knn = cv2.KNearest()
    knn.train(train, train_labels)
    # ret, result, neighbours, dist = knn.find_nearest(test, k=5)

    # Now we check the accuracy of classification
    # For that, compare the result with test_labels and check which are wrong
    # matches = result==test_labels
    # correct = np.count_nonzero(matches)
    # accuracy = correct*100.0/result.size
    # print 'Accuracy of OCR on test data: ' + str(accuracy)
    return knn


def classifyImage(knn, img):
    img = cv2.resize(img, (20,20))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    x = np.array(gray)
    test = x.reshape(-1, 400).astype(np.float32)
    ret, result, neighbours, dist = knn.find_nearest(test, k=5)
    return int(ret)


def main(capture, sandbox_send, sandbox_recv, files):
    logging.debug(TAG + "inside main")

    knn = preprocess_train_test()

    frame_num = 0
    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        frame_num += 1

        classifiedDigit = classifyImage(knn, frame)
        logging.debug(TAG + "sending obj:num %d" % frame_num)
        sandbox_send.send_pyobj((frame_num, [classifiedDigit]))
