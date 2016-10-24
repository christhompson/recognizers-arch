#!/usr/bin/env python2.7

# supervisor.py
# Copyright 2013 Christopher Thompson <cthompson@cs.berkeley.edu>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Supervisor process:
 - Give path to recognizer and main app modules
 - Initializes system calls for camera, file descriptors needed
 - Starts sandbox
 - Spawns children for recognizer and main app, passing socket for
   communicating back to do IPC through it
 - Times frames from camera, kills and restarts recognizer component
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import argparse
import importlib
from collections import deque
import time
import logging
import zmq
from multiprocessing import Process
import sys
from pympler.asizeof import asizeof
import os
import sys
import zlib
import pickle
from filters import faceblur

# Configuration
log_format = '%(created)f:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)
TAG = "supervisor:"
ENABLE_SANDBOX = False


def send_zipped_pickle(self, obj):
    return self.send(zlib.compress(pickle.dumps(obj, protocol=2)))


def recv_zipped_pickle(self):
    return pickle.loads(zlib.decompress(self.recv()))


def add_socket_compression(socket):
    send_type = type(zmq.Socket.send_pyobj)
    recv_type = type(zmq.Socket.recv_pyobj)
    socket.send_pyobj = send_type(send_zipped_pickle, socket, zmq.Socket)
    socket.recv_pyobj = recv_type(recv_zipped_pickle, socket, zmq.Socket)


def recognizer_launcher(recog_module, files_needed=None, compress=False,
                        capture_file=None, face_blur=False, platform=None):
    '''
    recognizer_launcher
    - Loads the video capture
    - Warms up the necessary APIs and file handles (needed for Seatbelt
      support, although a seccomp policy would explicitly enumerate these
      separately)
    - Connects to the zeroMQ socket for communication with the supervisor.
    - Turn on the sandbox, if enabled
    - Imports and runs the recognizer module
    '''
    logging.debug(TAG + "starting recognizer launcher")
    # Warm up CV and libraries.
    import cv2

    if face_blur:
        capture = faceblur.FaceBlurCapture()
    else:
        capture = cv2.VideoCapture()

    if capture_file:
        capture.open(capture_file)  # Capture from video file instead.
    else:
        capture.open(0)  # Get live camera.
    logging.debug(TAG + "camera opened")

    # Warm-up file set.
    files = {}
    if files_needed is None:
        files_needed = []
    for f in files_needed:
        try:
            files[f] = open(f)
        except IOError:
            logging.error(TAG + "Error opening file %s for recognizer" % f)

    # Establish IPC sockets.
    context = zmq.Context()
    sbx_to_prx = context.socket(zmq.PUSH)
    sbx_to_prx.connect("ipc:///tmp/sbx_to_prx")
    prx_to_sbx = context.socket(zmq.PULL)
    prx_to_sbx.connect("ipc:///tmp/prx_to_sbx")

    # If compression is enabled, monkeypatch send_/recv_pyobj on sockets.
    if compress:
        add_socket_compression(sbx_to_prx)
    try:
        m = importlib.import_module(recog_module)
        if ENABLE_SANDBOX:
            if platform == "osx":
                sandbox_init()
            if platform == "linux":
                # TODO: Add real sandbox policy here.
                f = seccomp.SyscallFilter(defaction=seccomp.ALLOW)
                f.load()
        # Execute main() of module.
        return m.main(capture, sbx_to_prx, prx_to_sbx, files=files)
    except ImportError:
        logging.error(TAG + "Error importing recognizer module")
        return False


def app_launcher(app_module, compress=False):
    # Note: we could also sandbox the appModule so that it doesn't
    # get access to the camera (blacklist would be easiest, but hard
    # to pull off; better would be to allow filesystem and network access
    # but don't warm-up the camera for it, so the API breaks).
    context = zmq.Context()
    data_receiver = context.socket(zmq.PULL)
    data_receiver.connect("ipc:///tmp/prx_to_app")
    results_sender = context.socket(zmq.PUSH)
    results_sender.connect("ipc:///tmp/app_to_prx")

    if compress:
        add_socket_compression(data_receiver)
        add_socket_compression(results_sender)

    try:
        m = importlib.import_module(app_module)
        return m.main(data_receiver, results_sender)
    except ImportError:
        logging.error(TAG + "Error importing application module")
        return False


class TokenBucket(object):
    def __init__(self, max_tokens=10, fill_rate=1):
        self.capacity = float(max_tokens)
        self._tokens = float(max_tokens)
        self.fill_rate = float(fill_rate)
        self.timestamp = time.time()

    def consume(self, tokens):
        if tokens <= self.tokens:
            self._tokens -= tokens
            return True
        else:
            return False

    def get_tokens(self):
        if self._tokens < self.capacity:
            now = time.time()
            delta = self.fill_rate * (now - self.timestamp)
            self._tokens = min(self.capacity, self._tokens + delta)
            self.timestamp = now
        return self._tokens
    tokens = property(get_tokens)


def main(platform=None):
    logging.debug(TAG + "inside main")
    fill_rate = 200
    max_tokens = fill_rate * 2

    parser = argparse.ArgumentParser()
    parser.add_argument("recognizer",
                        help="dot-format module name for recognizer")
    parser.add_argument("application",
                        help="dot-format module name for application")
    parser.add_argument("--fill_rate",
                        help="byte-tokens added per second",
                        type=int)
    parser.add_argument("--max_tokens",
                        help="max capacity of token bucket in bytes",
                        type=int)
    parser.add_argument("-c", "--compress",
                        help="enable zlib compression of pickles",
                        action='store_true')
    parser.add_argument("-v", "--video",
                        help="capture from video file instead of from camera")
    parser.add_argument("--faceblur",
                        help="activate ingress face blur filter",
                        action='store_true')

    args = parser.parse_args()
    recog_module = args.recognizer
    app_module = args.application

    logging.info(TAG + "recognizer = %s" % recog_module)
    logging.info(TAG + "app = %s" % app_module)

    # Get flags for MAX_TOKENS and FILL_RATE override.
    if args.fill_rate:
        fill_rate = args.fill_rate
    if args.max_tokens:
        max_tokens = args.max_tokens

    # Setup zmq IPC over named domain socket.
    context = zmq.Context()
    sbx_to_prx = context.socket(zmq.PULL)
    sbx_to_prx.bind("ipc:///tmp/sbx_to_prx")

    prx_to_sbx = context.socket(zmq.PUSH)
    prx_to_sbx.setsockopt(zmq.LINGER, 30)
    prx_to_sbx.bind("ipc:///tmp/prx_to_sbx")
    prx_to_sbx.SNDTIMEO = 30  # Prevents blocking on send if recog is dead.

    prx_to_app = context.socket(zmq.PUSH)
    prx_to_app.setsockopt(zmq.LINGER, 30)
    prx_to_app.bind("ipc:///tmp/prx_to_app")
    prx_to_app.SNDTIMEO = 30  # Prevents blocking on send if app is dead.

    app_to_prx = context.socket(zmq.PULL)
    app_to_prx.bind("ipc:///tmp/app_to_prx")

    if args.compress:
        add_socket_compression(sbx_to_prx)
        add_socket_compression(prx_to_sbx)
        add_socket_compression(prx_to_app)
        add_socket_compression(app_to_prx)

    # Start processes.
    recognizer_process = Process(target=recognizer_launcher,
                                 args=(recog_module,),
                                 kwargs={'compress': args.compress,
                                         'capture_file': args.video,
                                         'face_blur': args.faceblur,
                                         'platform': platform})
    app_process = Process(target=app_launcher, args=(app_module,),
                          kwargs={'compress': args.compress})
    recognizer_process.start()
    app_process.start()

    # Setup rate limiting and polling.
    q = deque(maxlen=4)  # Keep at most two in-flight objects.
    bucket = TokenBucket(max_tokens=max_tokens, fill_rate=fill_rate)

    in_poller = zmq.Poller()
    in_poller.register(sbx_to_prx, zmq.POLLIN)
    in_poller.register(app_to_prx, zmq.POLLIN)

    while True:
        logging.debug(TAG + "tokens before read = %f" % bucket.get_tokens())

        # Poll on our incoming sockets.
        # We also want to run if there's something queued and waiting.
        in_socks = dict(in_poller.poll(1000))

        if in_socks.get(sbx_to_prx) == zmq.POLLIN:
            # New entries kick out old ones from the deque.
            # We use a short maxlen so we don't have queue explosion.
            obj = sbx_to_prx.recv()
            p_size = asizeof(obj)
            logging.info(TAG + "sandbox sent obj of size = %d" % p_size)

            # Log if we drop an item.
            if len(q) == q.maxlen:
                logging.info(TAG + "pushing item out of buffer")
            q.append((p_size, obj))

            # If we have enough tokens, try to send the first item.
            if bucket.consume(q[0][0]):
                try:
                    prx_to_app.send(q.popleft()[1])
                    logging.debug(TAG + "sent object to app")
                except zmq.error.Again:
                    logging.error(TAG + "send to app timed out")
            else:
                logging.debug(TAG + "not enough tokens")

        if in_socks.get(app_to_prx) == zmq.POLLIN:
            # Messages from app should be settings dicts (JSON).
            obj = app_to_prx.recv_json()
            logging.info(TAG + "data from app of size = %d" % asizeof(obj))
            try:
                prx_to_sbx.send_json(obj)
            except zmq.error.Again:
                logging.error(TAG + "send to recog timed out")

        recognizer_is_done = not recognizer_process.is_alive()
        app_is_done = not app_process.is_alive()
        if recognizer_is_done or app_is_done:
            logging.error(TAG + "a child process died (%s%s)" %
                          (" recognizer " if recognizer_is_done else "",
                           " app " if app_is_done else ""))
            app_process.terminate()
            recognizer_process.terminate()
            app_process.join()
            recognizer_process.join()
            break

    logging.info(TAG + "Quitting...")
    logging.info(TAG + "token count = %d" % bucket.get_tokens())
    # Use _exit because sys.exit() hangs with multiprocessing.
    os._exit(os.EX_OK)


def get_platform():
    platform = None
    if "linux" in os.sys.platform:
        platform = "linux"
    elif "darwin" in os.sys.platform:
        platform = "osx"
    return platform


logging.debug(TAG + "starting module")
if __name__ == "__main__":
    logging.debug(TAG + "starting main")

    platform_name = get_platform()
    if ENABLE_SANDBOX:
        if platform_name == "linux":
            import seccomp
        elif platform_name == "osx":
            from sandbox import sandbox_init
        else:
            print("ERROR: Must run on Linux or OS X to use the sandbox")
            sys.exit(-1)

    try:
        main(platform=platform_name)
    except KeyboardInterrupt:
        logging.exception("Keyboard interrupt.")
        # Multiprocessing automatically cleans up children here.
