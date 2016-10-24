// Based off code from OpenCV website
//@source https://github.com/Itseez/opencv/blob/master/samples/cpp/tutorial_code/Histograms_Matching/MatchTemplate_Demo.cpp

#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include <iostream>
#include <stdio.h>
#include "../logging.h"

using namespace std;
using namespace cv;

const char *TAG = "template-matcher";
const string image_window = "Source Image";
const string result_window = "Result window";

void getMatch(Mat, Mat, int);

int main(int argc, char** argv) {
  Mat templ;

  DEBUG("inside main");
  // Initialize capturing live feed from the camera
  VideoCapture capture;
  if (argc >= 3 && strncmp(argv[1], "-v", 2) == 0) {
    DEBUG("Reading from file");
    capture = VideoCapture(argv[2]);
    templ = imread("apps/darkly/template-matcher/template_video.png", 1);
  } else {
    DEBUG("Capturing from camera");
    capture = VideoCapture(0);
    templ = imread(argv[1], 1);
  }
  DEBUG("done parsing arguments");
  DEBUG("camera opened");
    
  // Create windows
  namedWindow(image_window, CV_WINDOW_AUTOSIZE);
  // namedWindow(result_window, CV_WINDOW_AUTOSIZE);
  
  // Create Trackbar
  int match_method = 0;
  int max_Trackbar = 5;
  string trackbar_label = "Method: \n 0: SQDIFF \n 1: SQDIFF NORMED \n 2: TM CCORR \n 3: TM CCORR NORMED \n 4: TM CCOEFF \n 5: TM CCOEFF NORMED";
  createTrackbar(trackbar_label, image_window, &match_method, max_Trackbar);
  
  Mat frame;

  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");

    getMatch(frame, templ, match_method);
    DEBUG("displayed image");

    if(waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
  }
  return 0;
}

/**
 * @function MatchingMethod
 * @brief Trackbar callback
 */
void getMatch(Mat img, Mat templ, int match_method) {
    Mat result;
    Mat output(img.size(), img.depth());
    output = Scalar(255, 255, 255);
    
    // Create the result matrix
    int result_cols = img.cols - templ.cols + 1;
    int result_rows = img.rows - templ.rows + 1;
    
    result.create(result_cols, result_rows, CV_32FC1);
    
    // Do the Matching and Normalize
    matchTemplate(img, templ, result, match_method);
    normalize(result, result, 0, 1, NORM_MINMAX, -1, Mat());
    
    // Localizing the best match with minMaxLoc
    double minVal; double maxVal; Point minLoc; Point maxLoc;
    Point matchLoc;
    
    minMaxLoc(result, &minVal, &maxVal, &minLoc, &maxLoc, Mat());
    
    // For SQDIFF and SQDIFF_NORMED, the best matches are lower values.
    // For all the other methods, the higher the better
    if (match_method == CV_TM_SQDIFF || match_method == CV_TM_SQDIFF_NORMED)
      matchLoc = minLoc;
    else
      matchLoc = maxLoc;
    
    // Show me what you got
    rectangle(output, matchLoc,
              Point(matchLoc.x + templ.cols, matchLoc.y + templ.rows),
              Scalar::all(0), 2, 8, 0);

    imshow(image_window, output);
    // imshow(result_window, result);
}
