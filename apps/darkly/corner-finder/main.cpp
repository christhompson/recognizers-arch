// corner-finder: adapted from
// http://www.aishack.in/2010/05/corner-detection-in-opencv/
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./CornerFinder
// Alternatively, use the script ./run.sh

#include <stdio.h>
#include "../logging.h"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

#include <iostream>

#define MAX_CORNERS 20
const char *TAG = "corner-finder";

using namespace cv;
using namespace std;

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

  namedWindow("corners", CV_WINDOW_AUTOSIZE);

  Mat frame;
  Mat grayscale;
  Mat imgTemp;
  Mat imgEigen;
  vector<Point2f> corners;
  Mat output;
  
  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");

    output.create(frame.size(), frame.depth());
    output = Scalar(0, 0, 0); // set to black

    cvtColor(frame, grayscale, CV_BGR2GRAY);

    // Find corners
    goodFeaturesToTrack(grayscale, corners, MAX_CORNERS, 0.1, 20);

    // Mark these corners on the original image
    for(int i = 0; i < corners.size(); i++) {
      circle(output, corners.at(i), 4, Scalar(255, 0, 0), -1, 8, 0);
    }

    imshow("corners", output);
    DEBUG("displayed image");

    if (waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}
