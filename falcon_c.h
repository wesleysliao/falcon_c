#ifndef _FALCON_C_H_
#define _FALCON_C_H_

// C interface for libnifalcon

#include <falcon/core/FalconDevice.h>
#include <falcon/kinematic/FalconKinematicStamper.h>
#include <falcon/firmware/FalconFirmwareNovintSDK.h>
#include <falcon/grip/FalconGripFourButton.h>

#if defined(__cplusplus)
  extern "C" {
#endif
    void * falcon_init(int device_num);
    int falcon_load_firmware(void * falcon_ref, char * filename);
    int falcon_run_io_loop(void * falcon_ref);
    double falcon_get_pos_x(void * falcon_ref);
    double falcon_get_pos_y(void * falcon_ref);
    double falcon_get_pos_z(void * falcon_ref);
    void falcon_set_force(void * falcon_ref, double x, double y, double z);
    void falcon_set_leds(void * falcon_ref, bool red, bool green, bool blue);
    void falcon_exit(void * falcon_ref);
#if defined(__cplusplus)
  }
#endif

#endif // _FALCON_C_H_
