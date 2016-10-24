Notes on structure of this directory:

ball_tracker_cmake
===================
This represents the code, which can be compiled using CMake.
To compile this code, cd into the build directory in ball_tracker_cmake

Then, run cmake ../ball_tracker
Then, run make
And run ./BallTracker

If ./BallTracker is run with no arguments, then it'll capture directly from the webcam
Otherwise, run ./BallTracker "video name", and it'll load the video
For instance, run ./BallTracker ../../testvideos/moving.mov

ball_tracker_xcode
===================
This holds the XCode project for ball_tracker.

ball_tracker_python
===================
This is the python code, so there is the app and the sandboxed version all in there.