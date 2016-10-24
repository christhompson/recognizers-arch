// morphology
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./CornerFinder
// Alternatively, use the script ./run.sh

#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "../logging.h"

#include <iostream>
const char *TAG = "morphology";

using namespace cv;
using namespace std;

Mat frame;
Mat erodedest, dilatedest;

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

  int erodelevel = 1;
  int dilatelevel = 1;

  namedWindow("Erosion window");
  namedWindow("Dilation window");
  createTrackbar("Erode", "Erosion window", &erodelevel, 10);
  createTrackbar("Dilate", "Dilation window", &dilatelevel, 10);

  while (true) {
    DEBUG("before reading frame");
    // Get the next frame
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");

    erode(frame, erodedest, Mat(), Point(-1, -1), erodelevel);
    dilate(frame, dilatedest, Mat(), Point(-1, -1), dilatelevel);

    /// Show the images
    imshow("Erosion window", erodedest);
    imshow("Dilation window", dilatedest);
    DEBUG("displayed image");

    if (waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}
