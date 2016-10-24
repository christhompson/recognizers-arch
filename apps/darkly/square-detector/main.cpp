//
// The full "Square Detector" program.
// It loads several images subsequentally and tries to find squares in
// each image
//

#include "../logging.h"

#include <stdio.h>
#include <math.h>
#include <string.h>

#include <stdio.h>
#include "../logging.h"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include <iostream>

using namespace cv;
using namespace std;

const char *TAG = "square-detector";

// helper function:
// finds a cosine of angle between vectors
// from pt0->pt1 and from pt0->pt2 
double angle(Point &pt1, Point &pt2, Point &pt0) {
    double dx1 = pt1.x - pt0.x;
    double dy1 = pt1.y - pt0.y;
    double dx2 = pt2.x - pt0.x;
    double dy2 = pt2.y - pt0.y;
    return (dx1*dx2 + dy1*dy2)/sqrt((dx1*dx1 + dy1*dy1)*(dx2*dx2 + dy2*dy2) + 1e-10);
}

// returns sequence of squares detected on the image.
// the sequence is stored in the specified memory storage
void findSquares(Mat img, vector<pair<Point, Point> > &squares, int thresh) {
  vector<vector<Point> > contours;
  vector<vector<Point> > polyContours;
  vector<Vec4i> hierarchy;

  int N = 11;

  Size sz = Size(img.rows & -2, img.cols & -2);
  Mat timg = img.clone();
  Mat gray(sz, CV_8UC1);
  Mat downscaled(Size(sz.width/2, sz.height/2), CV_8UC3);
  Mat upscaled(sz, CV_8UC3);
  Mat tgray(sz, CV_8UC1);
  double s, t;
  
  // select the maximum ROI in the image
  // with the width and height divisible by 2
  // cvSetImageROI( timg, cvRect( 0, 0, sz.width, sz.height ));
  
  // down-scale and upscale the image to filter out the noise
  pyrDown(timg, downscaled);
  pyrUp(downscaled, upscaled);

  Mat kernel = Mat::ones(Size(5, 5), CV_8UC1);
  
  // find squares in every color plane of the image
  Mat planes[3];
  split(upscaled, planes);
  for (int c = 0; c < 3; c++) {
    // extract the c-th color plane
    planes[c].copyTo(tgray);
    
    // try several threshold levels
    for (int l = 0; l < N; l++) {
      // hack: use Canny instead of zero threshold level.
      // Canny helps to catch squares with gradient shading   
      if (l == 0) {
        // apply Canny. Take the upper threshold from slider
        // and set the lower to 0 (which forces edges merging) 
        Canny(tgray, gray, 0, thresh, 5);

        // dilate canny output to remove potential
        // holes between edge segments 
        dilate(gray, gray, kernel);
      } else {
        // apply threshold if l!=0:
        //     tgray(x,y) = gray(x,y) < (l+1)*255/N ? 255 : 0
        threshold(tgray, gray, (l+1)*255/N, 255, CV_THRESH_BINARY );
      }
      
      // find contours and store them all as a list
      findContours(gray, contours, hierarchy, CV_RETR_LIST, CV_CHAIN_APPROX_SIMPLE);
      
      // test each contour
      polyContours.resize(contours.size());
      for (int i = 0; i < contours.size(); i++) {
        // approximate contour with accuracy proportional to the contour perimeter
        approxPolyDP(Mat(contours[i]), polyContours[i], arcLength(contours[i], true)*0.02, true);

        // square contours should have 4 vertices after approximation
        // relatively large area (to filter out noisy contours) and be convex.
        // Note: absolute value of an area is used because area may be positive
        // or negative - in accordance with the contour orientation
        if (polyContours[i].size() == 4 &&
          fabs(contourArea(polyContours[i], false)) > 1000 &&
          isContourConvex(polyContours[i])) {
          s = 0;
          
          for (int j = 0; j < 5; j++) {
            // find minimum angle between joint
            // edges (maximum of cosine)
            if(j >= 2) {
                t = fabs(angle(
                  polyContours[i][j],
                  polyContours[i][j-2],
                  polyContours[i][j-1]));
                s = s > t ? s : t;
            }
          }
          
          // if cosines of all angles are small
          // (all angles are ~90 degree) then write quandrange
          // vertices to resultant sequence 
          if (s < 0.3) {
            squares.push_back(pair<Point, Point>(polyContours[i][0], polyContours[i][2]));
          }
        }
      }
    }
  }
}


// the function draws all the squares in the image
void drawSquares(Mat &img, vector<pair<Point, Point> > squares) {
  for (int i = 0; i < squares.size(); i++) {
    Point topLeft = squares[i].first;
    Point bottomRight = squares[i].second;
    rectangle(img, topLeft, bottomRight, Scalar(0, 255, 0), 3, 8, 0);
  }
  imshow("image", img);
}

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

  Mat frame;
  vector<pair<Point, Point> > squares;
  int thresh = 50;

  // create window with name "image"
  cvNamedWindow("image", 1);

  // create trackbar (slider) with parent "image" and set callback
  // (the slider regulates upper threshold, passed to Canny edge detector) 
  createTrackbar("thresh", "image", &thresh, 1000);

  while (true) {
    DEBUG("before reading frame");
    capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");

    squares.clear();
    findSquares(frame, squares, thresh);
    Mat blank = Mat::zeros(frame.size(), frame.depth());
    blank = Scalar(255, 255, 255);
    drawSquares(blank, squares);

    DEBUG("displayed image");

    if (waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
  }

  return 0;
}
