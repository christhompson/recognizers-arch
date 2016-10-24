
#include <stdio.h>
#include "../logging.h"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <iostream>
#include <math.h>
#include <string.h>

using namespace cv;
using namespace std;

const char *TAG = "downsampling-edge-detector";

int main(int argc, char* argv[]) {
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

  namedWindow("out", CV_WINDOW_AUTOSIZE);
  Mat frame;
  Mat gray;
  Mat out;

  while (true) {
  	DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
  	DEBUG("after reading frame");

		// Make sure image is divisible by 2
		assert(frame.size[0] % 2 == 0 && frame.size[1] % 2 == 0);

		// Reduce the image by 2
		pyrDown(frame, out);

		// Perform canny edge detection
    cvtColor(out, gray, CV_BGR2GRAY);
		Canny(gray, gray, 10, 100, 3);

		// Show the processed image
    imshow("out", gray);
    DEBUG("displayed image");

		if (waitKey(5) == 27) {
  		DEBUG("received escape key");
      break;
		}
	}
	return 0;
}
