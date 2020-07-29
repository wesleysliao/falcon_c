#!/usr/bin/env python3

import ctypes

ctypes.cdll.LoadLibrary("./lib/falcon_c.so")

falcon_c = ctypes.CDLL("./lib/falcon_c.so")

falcon_ref = falcon_c.falcon_init(0)

error = falcon_c.falcon_load_firmware(falcon_ref, "firmware/test_firmware.bin")

print(error)


get_pos_x = falcon_c.falcon_get_pos_x
# Must set the return type of the position functions to double or they will be cast to int
get_pos_x.restype = ctypes.c_double

for i in range(10000):
    falcon_c.falcon_run_io_loop(falcon_ref)
    x = get_pos_x(falcon_ref)
    print(x)


falcon_c.falcon_exit(falcon_ref)
