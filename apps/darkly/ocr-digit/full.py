#code taken from http://docs.opencv.org/trunk/doc/py_tutorials/py_ml/py_knn/py_knn_opencv/py_knn_opencv.html#knn-opencv

import numpy as np
import cv2
import os
import argparse
import logging
import time

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "ocr-digit-full:"

# method that trains a KNearest object, and returns it
# also tests it with sample data.
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
    img = cv2.resize(img, (20, 20))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    x = np.array(gray)
    test = x.reshape(-1, 400).astype(np.float32)
    ret, result, neighbours, dist = knn.find_nearest(test, k=5)
    logging.debug(TAG + "recognized digit: " + str(int(ret)))


def main():
    logging.debug(TAG + "inside main")

    # used for capturing from a video file
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

    knn = preprocess_train_test()

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break  # end of video
        logging.debug(TAG + "after reading frame")

        classifyImage(knn, frame)
        # shows image
        # cv2.imshow("frame", frame)
        logging.debug(TAG + "displayed image")

        if cv2.waitKey(5) == 27:
            logging.debug(TAG + "received escape key")
            break

    return True


logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")
    main()