// C interface for libnifalcon
// 2020 Wesley Liao

#include <falcon/core/FalconDevice.h>
#include <falcon/core/FalconFirmware.h>
#include <falcon/kinematic/FalconKinematicStamper.h>
#include <falcon/firmware/FalconFirmwareNovintSDK.h>
#include <falcon/grip/FalconGripFourButton.h>


extern "C" {

    void * falcon_init(int device_num) {

        libnifalcon::FalconDevice * falcon_device  = new libnifalcon::FalconDevice;

        falcon_device->setFalconKinematic<libnifalcon::FalconKinematicStamper>();
        falcon_device->setFalconFirmware<libnifalcon::FalconFirmwareNovintSDK>();
        falcon_device->setFalconGrip<libnifalcon::FalconGripFourButton>();

        if(!falcon_device->open(device_num)){
            return NULL;
        }

        void * falcon_ref = static_cast<void *>(falcon_device);
        return falcon_ref;
    }


    int falcon_load_firmware(void * falcon_ref, char * filename) {
        libnifalcon::FalconDevice * falcon_device = static_cast<libnifalcon::FalconDevice *>(falcon_ref);

        falcon_device->setFirmwareFile(filename);
        falcon_device->loadFirmware(10, false);

        return falcon_device->getErrorCode();
    }


    int falcon_run_io_loop(void * falcon_ref) {
        libnifalcon::FalconDevice * falcon_device = static_cast<libnifalcon::FalconDevice *>(falcon_ref);

        falcon_device->runIOLoop(falcon_device->FALCON_LOOP_KINEMATIC | falcon_device->FALCON_LOOP_GRIP);

        return falcon_device->getErrorCode();
    }


    double falcon_get_pos_x(void * falcon_ref) {
        libnifalcon::FalconDevice * falcon_device = static_cast<libnifalcon::FalconDevice *>(falcon_ref);

        std::array<double, 3> pos = falcon_device->getPosition();
        return pos[0];
    }

    double falcon_get_pos_y(void * falcon_ref) {
        libnifalcon::FalconDevice * falcon_device = static_cast<libnifalcon::FalconDevice *>(falcon_ref);

        std::array<double, 3> pos = falcon_device->getPosition();
        return pos[1];
    }

    double falcon_get_pos_z(void * falcon_ref) {
        libnifalcon::FalconDevice * falcon_device = static_cast<libnifalcon::FalconDevice *>(falcon_ref);

        std::array<double, 3> pos = falcon_device->getPosition();
        return pos[2];
    }


    void falcon_set_force(void * falcon_ref, double x, double y, double z) {
        libnifalcon::FalconDevice * falcon_device = static_cast<libnifalcon::FalconDevice *>(falcon_ref);

        std::array<double, 3> force;
        force[0] = x;
        force[1] = y;
        force[2] = z;
        falcon_device->setForce(force);
    }


    void falcon_set_leds(void * falcon_ref, bool red, bool green, bool blue) {
        libnifalcon::FalconDevice * falcon_device = static_cast<libnifalcon::FalconDevice *>(falcon_ref);

        char led_command = ((red * libnifalcon::FalconFirmware::RED_LED) |
                            (green * libnifalcon::FalconFirmware::GREEN_LED) |
                            (blue * libnifalcon::FalconFirmware::BLUE_LED));

        falcon_device->getFalconFirmware()->setLEDStatus(led_command);
    }


    void falcon_exit(void * falcon_ref) {
        libnifalcon::FalconDevice * falcon_device = static_cast<libnifalcon::FalconDevice *>(falcon_ref);

        falcon_device->close();

        delete falcon_device;
    }

}
