// corner-finder: adapted from
// http://docs.opencv.org/modules/imgproc/doc/histograms.html
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./CornerFinder
// Alternatively, use the script ./run.sh
//
// Taking a shot at writing this using the C++ API instead of teh old C API

#include <stdio.h>
#include <iostream>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>
#include "../logging.h"
const char *TAG = "hsv-hist";

using namespace cv;
using namespace std;

// The main function
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

  namedWindow("HSV Histogram");
  Mat frame, hsv;

  // Quantize the hue to 30 levels
  // and the saturation to 32 levels
  int hbins = 30, sbins = 32;
  int histSize[] = {hbins, sbins};

  // hue varies from 0 to 179, see cvtColor
  float hranges[] = { 0, 180 };
  // saturation varies from 0 (black-gray-white) to
  // 255 (pure spectrum color)
  float sranges[] = { 0, 256 };
  const float* ranges[] = { hranges, sranges };
  MatND hist;
  // we compute the histogram from the 0-th and 1-st channels
  int channels[] = {0, 1};

  
  while (true) {
    DEBUG("before reading frame");
    // Get the next frame
    capture.read(frame);
    if (frame.empty()) {
      break;
    }
    DEBUG("after reading frame");

    cvtColor(frame, hsv, CV_BGR2HSV);
    calcHist( &hsv, 1, channels, Mat(), // do not use mask
        hist, 2, histSize, ranges,
        true, // the histogram is uniform
        false );
    
    double maxVal=0;
    minMaxLoc(hist, 0, &maxVal, 0, 0);

    int scale = 10;
    Mat histImg = Mat::zeros(sbins*scale, hbins*10, CV_8UC3);

    for( int h = 0; h < hbins; h++ ) {
      for( int s = 0; s < sbins; s++ ) {
        float binVal = hist.at<float>(h, s);
        int intensity = cvRound(binVal*255/maxVal);
        rectangle( histImg, Point(h*scale, s*scale),
            Point( (h+1)*scale - 1, (s+1)*scale - 1),
            Scalar::all(intensity),
            CV_FILLED );
      }
    }

    imshow("HSV Histogram", histImg);
    DEBUG("displayed image");

    int c = waitKey(5);
    if (c != -1) {
      DEBUG("received escape key");
      break;
    }
  }

  //cvReleaseCapture(&capture);
  return 0;
}
