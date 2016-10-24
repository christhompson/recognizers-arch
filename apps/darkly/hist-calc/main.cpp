// hist-calc: adapted from
// http://www.aishack.in/2010/07/drawing-histograms-in-opencv/
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./HistCalc
// Alternatively, use the script ./run.sh

#include <stdio.h>
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include <iostream>

#include "../logging.h"
const char *TAG = "hist-calc";

using namespace std;
using namespace cv;

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

  namedWindow("hist-calc", CV_WINDOW_AUTOSIZE);

  Mat b_hist, g_hist, r_hist;
  int histSize = 256;
  bool uniform = true;
  bool accumulate = false;
  float range[] = {0, 256};
  const float* histRange = {range};
  
  Mat frame;
  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");

    // Split the image into separate B,G,R images
    vector<Mat> bgr;
    split(frame, bgr);

    calcHist(&bgr[0], 1, 0, Mat(), b_hist, 1, &histSize, &histRange, uniform, accumulate);
    calcHist(&bgr[1], 1, 0, Mat(), g_hist, 1, &histSize, &histRange, uniform, accumulate);
    calcHist(&bgr[2], 1, 0, Mat(), r_hist, 1, &histSize, &histRange, uniform, accumulate);

    // Draw the histograms for B, G and R
    int hist_w = 512; int hist_h = 400;
    int bin_w = cvRound((double) hist_w/histSize);

    Mat histImage(hist_h, hist_w, CV_8UC3, Scalar(0, 0, 0));

    // Normalize the result to [ 0, histImage.rows ]
    normalize(b_hist, b_hist, 0, histImage.rows, NORM_MINMAX, -1, Mat());
    normalize(g_hist, g_hist, 0, histImage.rows, NORM_MINMAX, -1, Mat());
    normalize(r_hist, r_hist, 0, histImage.rows, NORM_MINMAX, -1, Mat());

    // Draw for each channel
    for(int i = 1; i < histSize; i++) {
      line(histImage, Point( bin_w*(i-1), hist_h - cvRound(b_hist.at<float>(i-1)) ) ,
                      Point( bin_w*(i), hist_h - cvRound(b_hist.at<float>(i)) ),
                      Scalar( 255, 0, 0), 2, 8, 0);
      line(histImage, Point( bin_w*(i-1), hist_h - cvRound(g_hist.at<float>(i-1)) ) ,
                      Point( bin_w*(i), hist_h - cvRound(g_hist.at<float>(i)) ),
                      Scalar( 0, 255, 0), 2, 8, 0);
      line(histImage, Point( bin_w*(i-1), hist_h - cvRound(r_hist.at<float>(i-1)) ) ,
                      Point( bin_w*(i), hist_h - cvRound(r_hist.at<float>(i)) ),
                      Scalar( 0, 0, 255), 2, 8, 0);
    }

    // Display
    imshow("hist-calc", histImage);
    DEBUG("displayed image");

    if (waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
  }
}
