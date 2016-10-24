# Changes made to DARKLY corpus apps

- back-project
    - Bidir, matches native behavior in full and sandboxed
- ball-tracker
    - Original outputed full image, changed to only output ball tracking line
- corner-finder
    - Original outputed full image with corners overlaid, changed to only output corner dots
- downsampling_edge_detector
    - Only updated to C++ API, cleaned up some code, no change to output
- ellipse-fitter
    - Major cleanup to use C++ API
    - Change to only show output, not source frame as well
    - Had to add bidir comm to sandboxed version
- face-detect
    - Already used C++ API
    - No changes needed
- hand-detector
    - Changed to only output mask (previously outputed original and HSV of original)
    - Doesn't actually detect hands (doesn't finish using the mask to do the separation..)
    - Cleaned up C++ code a bunch, minor changes to make it use C++ API
- hist-calc
    - Major updates to use C++ API, clean up code
    - Change to only output histograms (remove display of original image)
- hsv-hist
    - No changes needed to use C++ API (C++ code was good)
    - Had to update full and sandbox so it was matching the C++
    - Moved all output drawing to app.py out of recog.py
- intensity-changer
    - Change to C++ API (ick)
    - Change to not output changed original image
    - Only output the histogram
    - Add trackbars and bidir comm to sandboxed and full python versions
- laplace
    - Change to C++ API, not too bad
    - Remove "shortcuts" and bring full and sandboxed to feature parity with C++
- morphology
    - Already using C++ API. Just had to update VideoCapture usage.
    - Morphology is very high BW. It is modifying original frame and sending it, twice.
- ocr-digit
    - We had to completely rewrite the C++ version, but it uses similar ideas.
    - Takes in a frame from a video of digits (instead of letting user draw a digit
    to be recognized)
    - "Output" is after the frame tested (resized down and resampled) and the prediction are outputed
    - Output is *only* the digit, not the downsamples frame (no imshow)
- priv-video
    - Updated to use C++ API
    - Changed to not output original frame, and only the foreground extracted
    - Fixed some broken/incredibly messy initialization code
- sobel
    - Already uses C++ API!
    - Updated VideoCapture code, minor style fixes
    - Minor fixes to Python versions
- square-detector
    - Convert to C++ API. Major refactor effort. Vectors, Mats, etc. instead of old C code.
    - Convert Python versions to *actually* do the same stuff as the C++ (was completely different).
    - Add trackbar to Python versions.
- template-matcher
    - Cleaned up code somewhat, but already in C++ API.
    - Changed to only output squares of detected region, instead of full frame.
    - Added trackbars to Python versions

## Implementation/re-implementation notes

We updated all the C++ versions to use the modern OpenCV C++ API instead of the now very old C API.

We had to be exceptionally careful when implementing the Python and sandboxed Python versions to not make them *more* efficient by only doing what was actually necessary for the recognizer. Raw, unsandboxed C++ OpenCV code tends to be messy, inefficient, and doesn't focus on what it really needs out of the image.

We also modified all C++ versions to take video input (to whatever degree was reasonable).
