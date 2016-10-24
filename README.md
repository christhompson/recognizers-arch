# Sandboxing for Python OpenCV Recognizers

```python supervisor.py recognizer_module app_module```

This starts the supervisor proxy, which uses Python's *multiprocessing*
library to spawn two subprocesses, one for the recognizer and one for
the app. The recognizer module is loaded through a sandbox function,
which first warms up then process, and then initializes the OS X sandbox
API (through our ctypes wrapper).

## Requirements

We have built and tested this software using:

- Mac OS X 10.9 (adding support for Linux's seccomp-bpf should be feasible)
- Python 2.7.6
- OpenCV 2.4.7, with Python enabled
- pyzmq 14.0.1

Other versions may also work, but have not been tested.

A `requirements.txt` file is included to simplify installing the required
Python modules into a virtualenv:

    virtualenv venv/
    pip install -r requirements.txt


## Analysis Pipeline

- `analysis/multi-run.sh`  (edited to run whichever app corpus is desired)
- `analysis/multi-analyze.sh`  (edited to loop over app corpus apps)

These work on `analysis.py`, which takes in a glob of logfiles (`logs/something/something-*`) for a single application
over all variations of it, and saves it into a data pickle (a combined `pandas.DataFrame` for that application).

Then, `barplots.py` can combine this data for all applications, and pull out interesting stats and make pretty pictures.


## License

Copyright 2016 Christopher Thompson <cthompson@cs.berkeley.edu>

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

A copy of the Apache License, Version 2.0 is included in `LICENSE`.

Included datasets are under their own stated license, and are included
here for convenience.
