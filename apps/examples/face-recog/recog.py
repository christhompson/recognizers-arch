#!/usr/bin/env python
#
# Modified by Christopher Thompson <cthompson@cs.berkeley.edu>
#
# Originally licensed under BSD -- original license below:
#
# Software License Agreement (BSD License)
#
# Copyright (c) 2012, Philipp Wagner <bytefish[at]gmx[dot]de>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of the author nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# ------------------------------------------------------------------------------------------------
# Note:
# When using the FaceRecognizer interface in combination with Python, please stick to Python 2.
# Some underlying scripts like create_csv will not work in other versions, like Python 3.
# ------------------------------------------------------------------------------------------------

import os
import sys
import numpy as np
import cv2
import logging

log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)  # log to file filename='example.log',
TAG = "face-recog-recog:"


def normalize(x, low, high, dtype=None):
    """Normalizes a given array in x to a value between low and high."""
    x = np.asarray(x)
    min_x, max_x = np.min(x), np.max(x)
    # normalize to [0...1].
    x -= float(min_x)
    x /= float((max_x - min_x))
    # scale to [low...high].
    x = x * (high-low)
    x += low
    if dtype is None:
        return np.asarray(x)
    return np.asarray(x, dtype=dtype)


def read_images(path, sz=None):
    """Reads the images in a given folder, resizes images on the fly if size is given.

    Args:
        path: Path to a folder with subfolders representing the subjects (persons).
        sz: A tuple with the size Resizes

    Returns:
        A list [X,y]

            X: The images, which is a Python list of numpy arrays.
            y: The corresponding labels (the unique number of the subject, person) in a Python list.
    """
    c = 0
    x, y = [], []
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            subject_path = os.path.join(dirname, subdirname)
            for filename in os.listdir(subject_path):
                try:
                    im = cv2.imread(os.path.join(subject_path, filename), cv2.IMREAD_GRAYSCALE)
                    # resize to given size (if given)
                    if sz is not None:
                        im = cv2.resize(im, sz)
                    x.append(np.asarray(im, dtype=np.uint8))
                    y.append(c)
                except IOError, (errno, strerror):
                    print "I/O error({0}): {1}".format(errno, strerror)
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise
            c += 1
    return [x, y]


def full_path(rel_path):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    return os.path.join(__location__, rel_path)


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4,
                                     minSize=(30, 30), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:, 2:] += rects[:, :2]
    return rects


def main(capture, sandbox_send, files):
    logging.debug(TAG + "inside main")
    # Now read in the image data. This must be a valid path!
    [x, y] = read_images(full_path("att_faces/"))

    # Convert labels to 32bit integers. This is a workaround for 64bit machines,
    # because the labels will truncated else. This will be fixed in code as
    # soon as possible, so Python users don't need to know about this.
    # Thanks to Leo Dirac for reporting:
    y = np.asarray(y, dtype=np.int32)

    # Create the Eigenfaces model. We are going to use the default
    # parameters for this simple example, please read the documentation
    # for thresholding:
    model = cv2.createEigenFaceRecognizer()

    # Read
    # Learn the model. Remember our function returns Python lists,
    # so we use np.asarray to turn them into NumPy lists to make
    # the OpenCV wrapper happy:
    model.train(np.asarray(x), np.asarray(y))

    # Set up the detector
    cascade_file = "cascades/haarcascade_frontalface_alt.xml"
    cascade = cv2.CascadeClassifier(full_path(cascade_file))
    if cascade.empty():
        print "Error loading cascade files"
        return False

    while True:
        logging.debug(TAG + "before reading frame")
        retval, frame = capture.read()
        if not retval:
            break
        logging.debug(TAG + "after reading frame")
        img = frame.copy()
        gray = cv2.cvtColor(img, cv2.cv.CV_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = detect(gray, cascade)

        for x1, y1, x2, y2 in faces:
            roi = gray[y1:y2, x1:x2]
            resized_face = cv2.resize(roi, (92, 112))
            # do recognition on the face
            p_label, p_confidence = model.predict(np.asarray(resized_face))

            # Send to app
            logging.debug(TAG + "sending obj")
            sandbox_send.send_pyobj((roi, p_label, p_confidence))

#
# if __name__ == "__main__":
#     main()