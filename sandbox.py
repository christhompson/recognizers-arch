#!/usr/bin/env python2.7

import ctypes
from ctypes import c_uint64, c_char_p, byref
from ctypes.util import find_library

# Test that we have sandbox
if not find_library("sandbox"):
    print("sandbox library not found")
    raise ImportError("sandbox library not found")

libsandbox = ctypes.CDLL(find_library("sandbox"), ctypes.RTLD_GLOBAL)


def sandbox_init():
    """
    // /usr/include/sandbox.h
    int sandbox_init(const char *profile, uint64_t flags, char **errorbuf);
    """
    # FIXME Specifying argtypes not working for profile
    # libsandbox.sandbox_init.argtypes = \
    #     [POINTER(c_char), c_uint64, POINTER(POINTER(c_char))]
    libsandbox.sandbox_init.restype = ctypes.c_int

    # Profile types -- note each leaves existing open file descriptors
    profile = libsandbox.kSBXProfileNoWrite
    # PureComputation = libsandbox.kSBXProfilePureComputation
    # NoInternet = libsandbox.kSBXProfileNoInternet
    # NoNetwork = libsandbox.kSBXProfileNoNetwork
    # NoWrite = libsandbox.kSBXProfileNoWrite
    # NoWriteExceptTemporary = libsandbox.kSBXProfileNoWriteExceptTemporary

    errorbuf_p = c_char_p()
    ret = libsandbox.sandbox_init(profile,
                                  c_uint64(0x0001),
                                  byref(errorbuf_p))
    if ret != 0:
        # Check errorbuf and free it
        try:
            print(errorbuf_p.value)
            libsandbox.sandbox_free_error(errorbuf_p)
        except TypeError:
            # Wasn't allocated
            pass
        return False
    else:
        return True


if __name__ == "__main__":
    from sys import exc_info
    # Simple sandbox test
    sandbox_init()
    try:
        open("edge-detect.file", "w")
    except OSError:
        error_type, value, traceback = exc_info()
        print(error_type, value, traceback)
        print("Test successful. Sandbox enabled.")


