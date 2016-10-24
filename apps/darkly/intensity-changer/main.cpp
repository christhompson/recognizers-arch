// Based off code from code.ros
// https://code.ros.org/trac/opencv/browser/trunk/opencv/samples/c/demhist.c?rev=1429 (link may be broken)

#include <stdio.h>
#include <iostream>

#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

using namespace cv;
using namespace std;

#include "../logging.h"
int _brightness = 100;
int _contrast = 100;

Mat src_image;
Mat dst_image;
Mat histImg;
MatND hist;
Mat lut_mat;

const char *TAG = "intensity-changer";

int main(int argc, char** argv) {
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
  
  // namedWindow("image", 0);
  namedWindow("histogram", 0);
  
  createTrackbar("brightness", "histogram", &_brightness, 200);
  createTrackbar("contrast", "histogram", &_contrast, 200);

  lut_mat.create(1, 256, CV_8UC1);
  
  Mat frame;
  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");

    cvtColor(frame, src_image, CV_BGR2GRAY, 1);

    // Applies intensity_changer algorithm to image
    // update_brightcont(0);
    int brightness = _brightness - 100;
    int contrast = _contrast - 100;
    int i;
    
    /*
     * The algorithm is by Werner D. Streidt
     * (http://visca.com/ffactory/archives/5-99/msg00021.html)
     */
    uchar *lut = lut_mat.ptr();
    if (contrast > 0) {
      double delta = 127. * contrast / 100;
      double a = 255. / (255. - delta * 2);
      double b = a * (brightness - delta);
      for (i = 0; i < 256; i++) {
          int v = cvRound(a * i + b);
          if( v < 0 )
              v = 0;
          if( v > 255 )
              v = 255;
          lut[i] = (uchar)v;
      }
    } else {
      double delta = -128. * contrast / 100;
      double a = (256. - delta * 2) / 255.;
      double b = a * brightness + delta;
      for (i = 0; i < 256; i++) {
        int v = cvRound(a * i + b);
        if (v < 0) v = 0;
        if(v > 255) v = 255;
        lut[i] = (uchar)v;
      }
    }
    
    LUT(src_image, lut_mat, dst_image);
    // imshow("image", dst_image);
    
    int bins = 256;
    int histSize[] = {bins};
    float lranges[] = {0, 256};
    const float* ranges[] = {lranges};
    int channels[] = {0};
    int const hist_height = 256;
    Mat3b hist_image = Mat3b::zeros(hist_height, bins);
    calcHist(&dst_image, 1, channels, Mat(),
      hist, 1, histSize, ranges, true, false);

    double max_val = 0;
    minMaxLoc(hist, 0, &max_val);
    for (int i = 0; i < bins; i++) {
      float const binVal = hist.at<float>(i);
      int const height = cvRound(binVal * hist_height / max_val);
      line(hist_image,
        Point(i, hist_height - height),
        Point(i, hist_height),
        Scalar::all(255));
    }

    imshow("histogram", hist_image);
    DEBUG("displayed image");

    // Wait for a keypress
    if (waitKey(5) == 27) {
        DEBUG("received escape key");
        break;
    }
  }
  return 0;
}
