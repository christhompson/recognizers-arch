//VERSION: HAND DETECTION 1.0
//AUTHOR: ANDOL LI
//PROJECT: HAND DETECTION PROTOTYPE
//LAST UPDATED: 03/2009

#include <opencv/cv.h>
#include <opencv/cxcore.h>
#include <opencv/highgui.h>
#include <iostream>
#include <stdio.h>
#include <string.h>
#include <sstream>
#include "../logging.h"

#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

using namespace cv;
using namespace std;

const char *TAG = "hand-detector";

int main(int argc, char **argv) {
  DEBUG("inside main");
  VideoCapture capture;
  if (argc >= 3 && strncmp(argv[1], "-v", 2) == 0) {
    DEBUG("Reading from file");
    capture = VideoCapture(argv[2]);
  } else {
    DEBUG("Capturing from camera");
    capture = VideoCapture(0);
  }

  // Couldn't get a device? Throw an error and quit
  if(!capture.isOpened()) {
    cout << "Could not initialize capturing\n";
    return -1;
  }
  DEBUG("camera opened");

	Mat hsv_image;
	Mat hsv_mask;
	Scalar hsv_min = Scalar(100, 50, 80);
	Scalar hsv_max = Scalar(150, 150, 255);
  Mat frame;
  bool success;

	while(true)	{
   	DEBUG("before reading frame");
    success = capture.read(frame);
    if(!success) break;
   	DEBUG("after reading frame");

    // Convert to HSV
    cvtColor(frame, hsv_image, CV_BGR2HSV);
    // Threshold based on HSV range for skin
		inRange(hsv_image, hsv_min, hsv_max, hsv_mask);

    namedWindow("hsv-msk", WINDOW_AUTOSIZE);
    imshow("hsv-msk", hsv_mask);

    // Apply mask back to original image
    // Mat output;
    // frame.copyTo(output, hsv_mask);
    // namedWindow("output", 1);
    // imshow("output", output);

    DEBUG("displayed image");
        
		if (waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
	}
}
