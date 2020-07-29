#include <iostream>
#include <csignal>

#include "falcon_c.h"

bool stop = false;
void sigproc(int i)
{
    if(!stop)
    {
        stop = true;
        std::cout << "Quitting" << std::endl;
    }
    else exit(0);
}

int main(int argc, char *argv[]) {

    signal(SIGINT, sigproc);


    void * falcon_ref = falcon_init(0);
    printf("init\n");
    int error = falcon_load_firmware(falcon_ref, "firmware/novint_T2.bin");
    printf("firmware %d\n", error);

    while(!stop) {

        error = falcon_run_io_loop(falcon_ref);
        printf("%d ", error);
        double x = falcon_get_pos_x(falcon_ref);
        double y = falcon_get_pos_y(falcon_ref);
        double z = falcon_get_pos_z(falcon_ref);
        printf("%f %f %f\n", x, y, z);

    }

    //void falcon_set_force(void * falcon_ref, float x, float y, float z);
    falcon_exit(falcon_ref);

    return 0;
}
