
// Based on code by Kostas
// Code from: http://theembeddedsystems.blogspot.com/2011/05/background-subtraction-using-opencv.html
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./CornerFinder
// Alternatively, use the script ./run.sh


#include "cv.h"
#include "highgui.h"
#include "../logging.h"
#include <stdio.h>
#include <ctype.h>

#include <stdio.h>
#include "../logging.h"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <iostream>

using namespace cv;
using namespace std;

const char *TAG = "priv-video";

int main(int argc, char** argv) {
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

  namedWindow("frameForeground", 1); 

  Mat frame;
  Mat currentFrame;
  Mat previousFrame;
  Mat foreground;
  Mat kernel = Mat::ones(Size(5, 5), CV_8UC1);

  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");

    cvtColor(frame, currentFrame, CV_BGR2GRAY);

    if (previousFrame.empty()) currentFrame.copyTo(previousFrame);

    absdiff(currentFrame, previousFrame, foreground);
    threshold(foreground, foreground, 10, 255, CV_THRESH_BINARY);              
    erode(foreground, foreground, kernel);
    dilate(foreground, foreground, kernel);
    dilate(foreground, foreground, kernel);
    erode(foreground, foreground, kernel);

    imshow("frameForeground", foreground);

    DEBUG("displayed image");

    currentFrame.copyTo(previousFrame);

    if (waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}

