// face-detect: adapted from
// http://docs.opencv.org/doc/tutorials/objdetect/cascade_classifier/cascade_classifier.html
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./FaceDetect
// Alternatively, use the script run.sh

#include "opencv2/objdetect/objdetect.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

#include <iostream>
#include <stdio.h>
#include "../logging.h"
const char *TAG = "face-detect";

using namespace std;
using namespace cv;

/** Function Headers */
void detectAndDisplay(Mat frame);

/** Global variables */
String face_cascade_name = "apps/darkly/face-detect/cascades/haarcascade_frontalface_alt.xml";
CascadeClassifier face_cascade;
string window_name = "face_detector";

/** @function main */
int main(int argc, const char** argv) {
  DEBUG("inside main");
  Mat frame, gray, eq;
  std::vector<Rect> faces;

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

  //-- 1. Load the cascades
  if(!face_cascade.load(face_cascade_name)) {
    printf("--(!)Error loading\n");
    return -1;
  }

  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) {
      break;
    }
    DEBUG("after reading frame");
    cvtColor(frame, gray, CV_BGR2GRAY);
    equalizeHist(gray, gray);
    face_cascade.detectMultiScale(
        gray, faces, 1.3, 4, CV_HAAR_SCALE_IMAGE, Size(30, 30));
    Mat canvas(720, 1280, CV_8UC3, Scalar(255, 255, 255));
    for (int i = 0; i < faces.size(); i++) {
      rectangle(canvas, faces[i], Scalar(0, 255, 0), 4);
    }
    imshow(window_name, canvas);
    DEBUG("displayed image");

    int c = waitKey(5);
    if (c != -1) {
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}
