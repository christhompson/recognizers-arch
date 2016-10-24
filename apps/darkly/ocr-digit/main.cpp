// Based off code from the OpenCV python OCR tutorial
// http://docs.opencv.org/trunk/doc/py_tutorials/py_ml/py_knn/py_knn_opencv/py_knn_opencv.html#knn-opencv
// Converted from python to C++ by Eric Shen, ericshen@berkeley.edu
//
// To use:
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./CornerFinder
// Alternatively, use the script ./run.sh

#include <stdio.h>
#include "../logging.h"
#include <opencv2/opencv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

// The standard OpenCV headers
using namespace cv;
using namespace std;

// global variables and constants
const char *TAG = "ocr-digit";
CvKNearest *knn;
Mat digits;
const int K = 32;
const int train_sample_count = 2500;

// given an image, resizes it and tries to classify what digit it is
void classifyImage(Mat img) {
  Mat resized, gray;

  // resizes the image and converts it to grayscale
  resize(img, resized, Size(20, 20), 0, 0, INTER_CUBIC);
  cvtColor(resized, gray, COLOR_BGR2GRAY);

  // shows the resized image
  // imshow("frame", gray);

  // converts the image into a 1x400 floating point array
  Mat reshaped = gray.clone();
  Mat floating;
  reshaped = reshaped.reshape(0, 1);
  reshaped.convertTo(floating, CV_32FC1, 0.0039215);

  // calls k nearest neighbors to find a match
  float ret = knn->find_nearest(floating, 5);

  // logs which digit got recognized
  char result[32];
  sprintf(result, "recognized Digit: %d", (int)ret); 
  DEBUG(result);
}

// method that trains a KNearest object, and assigns it to the variable knn
// also tests it with sample data.
void preprocess_train_test(const char *digits_image) {
  digits = imread(digits_image, 0);

  int i, j;

  // initializes Mat's to store the training data, and the classes that correspond to the image
  Mat trainData(train_sample_count, 400, CV_32FC1);
  Mat trainClasses(train_sample_count, 1, CV_32FC1);

  // iterates through all 20 x 20 portions of the image
  for(i = 0; i < 50; i++) {
    for(j = 0; j < 50; j++) {
      // grabs the current 20 x 20 region, and extracts it from the digit image
      Rect digitRegion(Point(i * 20, j * 20), Size(20, 20));
      Mat croppedDigit = digits(digitRegion).clone();

      // reshapes and converts the image to a 1 x 400 floating point array
      Mat reshaped = croppedDigit.clone();
      Mat floating;
      reshaped = reshaped.reshape(0, 1);
      reshaped.convertTo(floating, CV_32FC1, 0.0039215);

      // copies the image data into trainData
      floating.row(0).copyTo(trainData.row(i * 50 + j));

      // copies the class data (which digit corresponds to the image) into trainClass
      // j / 5 corresponds to which digit we are at (each digit has 5 rows corresponding to it)
      // 0 has rows 0-4, 1 has rows 5 - 9,..... and 9 has rows 45-49
      Mat digitHolder(1, 1, CV_32FC1, j/5);
      digitHolder.row(0).copyTo(trainClasses.row(i * 50 + j));
    }
  }

  //initializes the KNearest object
  knn = new CvKNearest(trainData, trainClasses, Mat(), false, K );
}

// The main function
int main(int argc, char **argv) {
  DEBUG("inside main");
  // Initialize capturing live feed from the camera
  VideoCapture capture;
  if (argc >= 3 && strncmp(argv[1], "-v", 2) == 0) {
    DEBUG("Reading from file");
    capture = VideoCapture(argv[2]);
  } else {
    DEBUG("Capturing from camera");
    capture = VideoCapture(0);
  }
  DEBUG("done parsing arguments");

  // Couldn't get a device? Throw an error and quit
  if(!capture.isOpened()) {
    cout << "Could not initialize capturing\n";
    return -1;
  }
  DEBUG("camera opened");

  preprocess_train_test("apps/darkly/ocr-digit/digits.png");

  Mat frame;
  // namedWindow("digits", WINDOW_AUTOSIZE);

  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");
    
    //classifies the image
    classifyImage(frame);
    DEBUG("displayed image");

    if(waitKey(5) == 27) {
      // If pressed, break out of the loop
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}
