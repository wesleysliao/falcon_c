#!/usr/bin/env python3
#

import ctypes
ctypes.cdll.LoadLibrary("falcon_c/lib/falcon_c.so")
falcon_c = ctypes.CDLL("falcon_c/lib/falcon_c.so")

falcon_get_x = falcon_c.falcon_get_pos_x
falcon_get_x.restype = ctypes.c_double

falcon_get_y = falcon_c.falcon_get_pos_y
falcon_get_y.restype = ctypes.c_double

falcon_get_z = falcon_c.falcon_get_pos_z
falcon_get_z.restype = ctypes.c_double

import json
import usb
import time


import numpy as np


class NovintFalcon:

    VENDOR_ID = 0x0403
    PRODUCT_ID = 0xcb48

    X = 0
    Y = 1
    Z = 2
    AXIS_COUNT = 3

    POS = 0
    VEL = 1
    ACCEL = 2
    DERIVATIVE_COUNT = 3
   
    def __init__(self, timestep_s, falcon_device_num = 0, reverse_z = False, estimate_window_s=0.1):

        self.timestep_s = timestep_s
        self.history_len = int(estimate_window_s / timestep_s)
        print("history length:", self.history_len)
        self.falcon_ref = falcon_c.falcon_init(falcon_device_num)
        self.reverse_z = reverse_z

        falcon_c.falcon_load_firmware(self.falcon_ref,
                                      "falcon_c/firmware/test_firmware.bin")

        self.calibrating = False

        falcon_devices = list(usb.core.find(idVendor=self.VENDOR_ID,
                                       idProduct=self.PRODUCT_ID,
                                       find_all=True))
        self.serial_number = falcon_devices[falcon_device_num].serial_number

        print("falcon ", falcon_device_num, " serial ", self.serial_number)

        try:
            calibration_file = open("./falcon_calibration.json", 'r')
            calibration_json = json.loads(calibration_file.read())

            calib = calibration_json["default"]
            if self.serial_number in calibration_json:
                calib = calibration_json[self.serial_number]

            self.x_min = calib["x_min"]
            self.x_max = calib["x_max"]
            self.y_min = calib["y_min"]
            self.y_max = calib["y_max"]
            self.z_min = calib["z_min"]
            self.z_max = calib["z_max"]

            self.x_offset = (self.x_min + self.x_max) / 2.0
            self.y_offset = (self.y_min + self.y_max) / 2.0
            self.z_offset = (self.z_min + self.z_max) / 2.0

            self.x_range = self.x_max - self.x_min
            self.y_range = self.y_max - self.y_min
            self.z_range = self.z_max - self.z_min

            self.x_scale = self.x_range / 2.0
            self.y_scale = self.y_range / 2.0
            self.z_scale = self.z_range / 2.0

            print("offset ", self.x_offset, self.y_offset, self.z_offset)
            print("range ", self.x_range, self.y_range, self.z_range)
            print("scale ", self.x_scale, self.y_scale, self.z_scale)

        except FileNotFoundError:
            print("calibration file not found")


        self.pos_history = np.zeros((self.history_len, self.AXIS_COUNT))

        self.A = np.zeros((self.history_len, self.DERIVATIVE_COUNT))

        for y in range(self.history_len):
            self.A[y, self.POS] = 1
            self.A[y, self.VEL] = -1 * y * self.timestep_s
            self.A[y, self.ACCEL] = (1/2) * ((y * self.timestep_s) ** 2)

        self.invA = np.linalg.pinv(self.A)

        print(self.A)


        self.x_pos = 0.0
        self.y_pos = 0.0
        self.z_pos = 0.0

        self.x_vel = 0.0
        self.y_vel = 0.0
        self.z_vel = 0.0

        self.x_force = 0.0
        self.y_force = 0.0
        self.z_force = 0.0

        self.x_bound_pos = 0.01
        self.x_bound_neg = -0.01
        self.x_bound_k = 0.0

        self.y_bound_pos = 0.01
        self.y_bound_neg = -0.01
        self.y_bound_k = -0.0

        self.z_bound_pos = 0.01
        self.z_bound_neg = -0.01
        self.z_bound_k = -0.0

        self.x_damping = -0.0
        self.y_damping = -0.0
        self.z_damping = -0.0



    def update_state(self):
        falcon_c.falcon_run_io_loop(self.falcon_ref)

        x_pos = falcon_get_x(self.falcon_ref)
        y_pos = falcon_get_y(self.falcon_ref)
        z_pos = falcon_get_z(self.falcon_ref)

        x_pos = (x_pos - self.x_offset) / self.x_scale
        y_pos = (y_pos - self.y_offset) / self.y_scale
        z_pos = (z_pos - self.z_offset) / self.z_scale

        if self.reverse_z:
            z_pos *= -1.0


        self.pos_history = np.roll(self.pos_history, 1, axis=0)
        self.pos_history[0, self.X] = x_pos
        self.pos_history[0, self.Y] = y_pos
        self.pos_history[0, self.Z] = z_pos

        estimate_x = np.matmul(self.invA, self.pos_history[:, self.X])
        estimate_y = np.matmul(self.invA, self.pos_history[:, self.Y])
        estimate_z = np.matmul(self.invA, self.pos_history[:, self.Z])

        self.x_pos = estimate_x[self.POS]
        self.y_pos = estimate_y[self.POS]
        self.z_pos = estimate_z[self.POS]

        self.x_vel = estimate_x[self.VEL]
        self.y_vel = estimate_y[self.VEL]
        self.z_vel = estimate_z[self.VEL]



    def get_pos(self):
        return self.x_pos, self.y_pos, self.z_pos

    def get_vel(self):
        return self.x_vel, self.y_vel, self.z_vel



    def add_force(self, force_x, force_y, force_z):
        self.x_force += force_x
        self.y_force += force_y
        self.z_force += force_z


    def output_forces(self):
        self.add_force(self.x_vel * self.x_damping,
                       self.y_vel * self.y_damping,
                       self.z_vel * self.z_damping)

        if(self.x_pos > self.x_bound_pos):
            self.x_force += self.x_bound_k * (self.x_pos - self.x_bound_pos)
        elif(self.x_pos < self.x_bound_neg):
            self.x_force += self.x_bound_k * (self.x_pos - self.x_bound_neg)

        if(self.y_pos > self.y_bound_pos):
            self.y_force += self.y_bound_k * (self.y_pos - self.y_bound_pos)
        elif(self.y_pos < self.y_bound_neg):
            self.y_force += self.y_bound_k * (self.y_pos - self.y_bound_neg)

        if(self.z_pos > self.z_bound_pos):
            self.z_force += self.z_bound_k * (self.z_pos - self.z_bound_pos)
        elif(self.z_pos < self.z_bound_neg):
            self.z_force += self.z_bound_k * (self.z_pos - self.z_bound_neg)

        if(np.sign(self.z_force) == np.sign(self.z_vel)):
            self.z_force *= 0.9

        if self.reverse_z:
            self.z_force*= -1.0
            


        falcon_c.falcon_set_force(self.falcon_ref,
                                  ctypes.c_double(self.x_force),
                                  ctypes.c_double(self.y_force),
                                  ctypes.c_double(self.z_force))

        self.x_force = 0.0
        self.y_force = 0.0
        self.z_force = 0.0


    def set_leds(self, red, green, blue):
        falcon_c.falcon_set_leds(self.falcon_ref,
                                 ctypes.c_bool(red),
                                 ctypes.c_bool(green),
                                 ctypes.c_bool(blue))


    def set_limits_cube(self, center_x, center_y, center_z, radius, k=10):
        self.x_bound_pos = center_x - radius
        self.x_bound_neg = center_x + radius
        self.x_bound_k = -k

        self.y_bound_pos = center_y - radius
        self.y_bound_neg = center_y + radius
        self.y_bound_k = -k

        self.z_bound_pos = center_z - radius
        self.z_bound_neg = center_z + radius
        self.z_bound_k = -k



    def __del__(self):
        falcon_c.falcon_exit(self.falcon_ref)
