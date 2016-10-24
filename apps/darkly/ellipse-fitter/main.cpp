/********************************************************************************
 *
 *
 *  This program is demonstration for ellipse fitting. Program finds
 *  contours and approximate it by ellipses.
 *
 *  Trackbar specify threshold parametr.
 *
 *  White lines is contours. Red lines is fitting ellipses.
 *
 *
 *  Autor:  Denis Burenkov.
 *
 *
 *
 ********************************************************************************/


#include <stdio.h>
#include "../logging.h"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <iostream>

const char *TAG = "ellipse-fitter";

using namespace cv;
using namespace std;

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
    
  // Create windows.
  namedWindow("Source", CV_WINDOW_AUTOSIZE);
  namedWindow("Result", CV_WINDOW_AUTOSIZE);
  
  Mat frame;
  Mat thresholded;
  Mat gray;
  Mat output;
  int thresholdValue = 70;
  vector<vector<Point> > contours;
  vector<Vec4i> hierarchy;
  RotatedRect box;

  // Create toolbars.
  createTrackbar("Threshold", "Result", &thresholdValue, 255);

  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");

    output.create(frame.size(), frame.depth());
    output = Scalar(0, 0, 0);

    // Get current threshold value
    // thresholdValue = getTrackbarPos("Threshold", "Result");
  
    // Threshold the source image. This needful for cvFindContours().
    cvtColor(frame, gray, CV_BGR2GRAY);
    threshold(gray, thresholded, thresholdValue, 255, CV_THRESH_BINARY);
    
    // Find all contours.
    findContours(thresholded, contours, hierarchy,
                 CV_RETR_LIST, CV_CHAIN_APPROX_NONE, Point(0, 0));
    
    // Fit ellipses and draw everything
    for (int i = 0; i < contours.size(); i++) {
      // Number point must be more than or equal to 6 (for cvFitEllipse_32f).
      if (contours.at(i).size() < 6) continue;
      
      box = fitEllipse(Mat(contours.at(i)));
      drawContours(output, contours, i, Scalar(255, 255, 255));
      ellipse(output, box, Scalar(255, 255, 255));
    }
    imshow("Result", output);
    DEBUG("displayed image");

    if(waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}
