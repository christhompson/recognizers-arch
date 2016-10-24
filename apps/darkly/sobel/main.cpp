/**
 * @file Sobel_Demo.cpp
 * @brief Sample code using Sobel and/orScharr OpenCV functions to make a simple Edge Detector
 * Tutorial: http://docs.opencv.org/doc/tutorials/imgproc/imgtrans/sobel_derivatives/sobel_derivatives.html
 * Code: https://github.com/Itseez/opencv/blob/master/samples/cpp/tutorial_code/ImgTrans/Sobel_Demo.cpp
 * @author OpenCV team
 * Modified to take in video input by Eric Shen
 */

#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include "../logging.h"

using namespace cv;
using namespace std;

const char *TAG = "sobel";

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

  /// Create window
  const char* window_name = "Sobel Demo - Simple Edge Detector";
  namedWindow(window_name, WINDOW_AUTOSIZE);

  Mat src, src_gray;
  Mat grad;
  int scale = 1;
  int delta = 0;
  int ddepth = CV_16S;

  /// Generate grad_x and grad_y
  Mat grad_x, grad_y;
  Mat abs_grad_x, abs_grad_y;

  while (true) {
    DEBUG("before reading frame");
    capture.read(src);
    if (src.empty()) break;
    DEBUG("after reading frame");

    GaussianBlur(src, src, Size(3,3), 0, 0, BORDER_DEFAULT);

    /// Convert it to gray
    cvtColor(src, src_gray, COLOR_RGB2GRAY);

    /// Gradient X
    //Scharr( src_gray, grad_x, ddepth, 1, 0, scale, delta, BORDER_DEFAULT );
    Sobel(src_gray, grad_x, ddepth, 1, 0, 3, scale, delta, BORDER_DEFAULT);
    convertScaleAbs(grad_x, abs_grad_x);

    /// Gradient Y
    //Scharr( src_gray, grad_y, ddepth, 0, 1, scale, delta, BORDER_DEFAULT );
    Sobel(src_gray, grad_y, ddepth, 0, 1, 3, scale, delta, BORDER_DEFAULT);
    convertScaleAbs(grad_y, abs_grad_y);

    /// Total Gradient (approximate)
    addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0, grad);

    imshow(window_name, grad);
    DEBUG("displayed image");

    if(waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}