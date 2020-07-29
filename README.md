# falcon_c
C interface for libnifalcon (https://github.com/libnifalcon/libnifalcon)

Initially written to use libnifalcon in python through ctypes.

Requires g++, gnu make, and libnifalcon. Requires python3 to run the python test program.
To compile, just enter the repo root directory and:

    make

You can then test the C functionality by running:

    example

You can also test calling the C functions in python with:

    python3 falcon_c_test.py
