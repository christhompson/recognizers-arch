
// Code from: https://code.ros.org/trac/opencv/browser/trunk/opencv/samples/c/laplace.c?rev=27
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./CornerFinder
// Alternatively, use the script ./run.sh

#include <stdio.h>
#include <iostream>

#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

using namespace cv;
using namespace std;

#include "../logging.h"

const char *TAG = "laplace";

int main(int argc, char** argv) {
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

  namedWindow("Laplacian", 0);

  Mat frame;
  Mat gray;
  Mat laplace;
  Mat colorlaplace;
  Mat planes[3];
  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");

    if(gray.empty()) {
      for (int i = 0; i < 3; i++)
        planes[i].create(frame.size(), CV_8UC1);
      laplace.create(frame.size(), IPL_DEPTH_16S);
      colorlaplace.create(frame.size(), CV_8UC3);
    }
    
    // cvCvtPixToPlane(frame, planes[0], planes[1], planes[2], 0);
    split(frame, planes);
    for (int i = 0; i < 3; i++) {
      Laplacian(planes[i], laplace, 10, 3);
      convertScaleAbs(laplace, planes[i]);
    }
    merge(planes, 3, colorlaplace);

    imshow("Laplacian", colorlaplace);
    DEBUG("displayed image");

    if (waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}
