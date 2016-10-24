//Based on code by Utkarsh Sinha
//Brought in code from https://github.com/liquidmetal/AI-Shack--Tracking-with-OpenCV/blob/master/TrackColour.cpp
// Assuming in the same directory as this file and CMakeLists.txt, compile/run:
// mkdir build && cd build && cmake .. && make && ./CornerFinder
// Alternatively, use the script ./run.sh

#include <stdio.h>
#include "../logging.h"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

#include <iostream>

const char *TAG = "ball-tracker";

using namespace cv;
using namespace std;

int main(int argc, char**argv) {
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
    
	// The two windows we'll be using
  namedWindow("ball");
  namedWindow("thresh");
    
	// This image holds the "scribble" data...
	// the tracked positions of the ball
	Mat imgScribble;
    
  // Holding the last and current ball positions
  static int posX = 0;
  static int posY = 0;

  Mat frame;
  Mat imgThresh;
  Mat imgHSV;
  Scalar hsv_min(50, 100, 100);
  Scalar hsv_max(70, 255, 255);

  double moment10;
  double moment01;
  double area;

  static int frameCounter = 0;
	while (true) {
    DEBUG("before reading frame");
		capture.read(frame);
    if (frame.empty()) break;
    DEBUG("after reading frame");
        
		// If this is the first frame, we need to initialize it
    if (frameCounter == 0)
			imgScribble.create(frame.size(), frame.depth());

    // Convert the image into an HSV image
    cvtColor(frame, imgHSV, CV_BGR2HSV);
      
    // Values 20,100,100 to 30,255,255 working perfect for yellow at around 6pm
    // cvInRangeS(imgHSV, cvScalar(112, 100, 100), cvScalar(124, 255, 255), imgThreshed);
    // for orange test ball
    inRange(imgHSV, hsv_min, hsv_max, imgThresh);
        
		// Calculate the moments to estimate the position of the ball
    Moments img_moments = moments(imgThresh);
        
		// The actual moment values
		moment10 = img_moments.m10;
		moment01 = img_moments.m01;
		area = img_moments.m00;
    
	  int lastX = posX;
	  int lastY = posY;

    if (area != 0) {
  		posX = moment10 / area;
  		posY = moment01 / area;
    }
        
		// Print it out for debugging purposes
		// printf("position (%d,%d)\n", posX, posY);
        
		// We want to draw a line only if its a valid position
		if (lastX > 0 && lastY > 0 && posX > 0 && posY > 0) {
			// Draw a yellow line from the previous point to the current point
      line(imgScribble, Point((int)posX, (int)posY), Point((int)lastX, (int)lastY),
           Scalar(255, 255, 255), 5, 8);
		}

		// cvShowImage("thresh", imgYellowThresh);
    // imshow("thresh", imgThresh);
		imshow("ball", imgScribble);
    DEBUG("displayed image");

		// Wait for a keypress
    if (waitKey(5) == 27) {
      DEBUG("received escape key");
      break;
    }
    frameCounter++;
  }
}