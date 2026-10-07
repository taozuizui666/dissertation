#ifndef TEENSY_SELF_DRIVING_CONTROL_SLIDE_H
#define TEENSY_SELF_DRIVING_CONTROL_SLIDE_H

#include <Arduino.h>

void stop_CS(int left_moto, int right_moto);
void slide_control(int command, int v_car, int left_moto, int right_moto,
                   int sensi);

#endif
