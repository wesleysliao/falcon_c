#!/usr/bin/env python3

import ctypes

ctypes.cdll.LoadLibrary("./lib/libnifalcon_c.so")

falcon_py = ctypes.CDLL("./lib/libnifalcon_c.so")

falcon_ref = ctypes.c_void_p()
falcon_ref = falcon_py.falcon_init(0)

error = falcon_py.falcon_load_firmware(falcon_ref, "firmware/test_firmware.bin")

print(error)

get_pos_x = falcon_py.falcon_get_pos_x
get_pos_x.restype = ctypes.c_double

for i in range(10000):
    falcon_py.falcon_run_io_loop(falcon_ref)
    x = get_pos_x(falcon_ref)
    print(x)


falcon_py.falcon_exit(falcon_ref)
