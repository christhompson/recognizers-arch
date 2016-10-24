// back-project: adapted from
// http://docs.opencv.org/doc/tutorials/imgproc/histograms/back_projection/back_projection.html
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./CornerFinder
// Alternatively, use the script ./run.sh

#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "../logging.h"

#include <iostream>
const char *TAG = "back-project";

using namespace cv;
using namespace std;

void HistBackproj(int, void*);

Mat frame; Mat hsv; Mat hue;
int bins = 25;

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
  namedWindow("Back Projection");
  /// Create Trackbar to enter the number of bins
  createTrackbar("* Hue  bins: ", "Back Projection", &bins, 180, HistBackproj);
  
  while (true) {
    DEBUG("before reading frame");
    // Get the next frame
    capture.read(frame);
    if (frame.empty()) {
      break;
    }
    DEBUG("after reading frame");

    /// Transform it to HSV
    cvtColor(frame, hsv, CV_BGR2HSV);

    /// Use only the Hue value
    hue.create(hsv.size(), hsv.depth());
    int ch[] = { 0, 0 };
    mixChannels(&hsv, 1, &hue, 1, ch, 1);

    HistBackproj(0, 0);

    /// Show the image
    DEBUG("displayed image");

    int c = waitKey(5);
    if (c != -1) {
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}


/**
 * @function HistBackproj
 * @brief Callback to Trackbar
 */
void HistBackproj(int, void*)
{
  MatND hist;
  int histSize = MAX(bins, 2);
  float hue_range[] = { 0, 180 };
  const float* ranges = { hue_range };

  /// Get the Histogram and normalize it
  calcHist(&hue, 1, 0, Mat(), hist, 1, &histSize, &ranges, true, false);
  normalize(hist, hist, 0, 255, NORM_MINMAX, -1, Mat());

  /// Get Backprojection
  MatND backproj;
  calcBackProject(&hue, 1, 0, hist, backproj, &ranges, 1, true);

  /// Draw the backproj
  imshow("Back Projection", backproj);

  /// Draw the histogram
  int w = 400; int h = 400;
  int bin_w = cvRound((double) w / histSize);
  Mat histImg = Mat::zeros(w, h, CV_8UC3);

  for(int i = 0; i < bins; i ++) {
    rectangle(histImg,
        Point(i*bin_w, h),
        Point((i+1)*bin_w, h - cvRound(hist.at<float>(i)*h/255.0)),
        Scalar(0, 0, 255),
        -1);
  }

  imshow("HSV Histogram", histImg);
}
