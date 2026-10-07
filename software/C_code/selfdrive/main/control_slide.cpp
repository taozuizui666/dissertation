#include "control_slide.h"

// Preserve the motor calibration and steering formula of the Teensy
// collecting_data sketch, rather than the UNO's different calibration.
constexpr int MOTOR_BIAS = 10;

static int pwmValue(int value) {
    return constrain(value, 0, 255);
}

void stop_CS(int left_moto, int right_moto) {
    analogWrite(left_moto, 0);
    analogWrite(right_moto, 0);
}

void slide_control(int command, int v_car, int left_moto, int right_moto,
                   int sensi) {
    if (command == 200) {
        stop_CS(left_moto, right_moto);
    } else if (command == 201) {
        analogWrite(left_moto, pwmValue(v_car + MOTOR_BIAS));
        analogWrite(right_moto, pwmValue(v_car));
    } else if (command == 255) {
        // Existing recording command does not change the motor outputs.
        return;
    } else if (command >= 0 && command <= 15) {
        const int steering = (10 - command) * sensi;
        analogWrite(left_moto, pwmValue(MOTOR_BIAS + v_car - steering));
        analogWrite(right_moto, pwmValue(v_car + steering));
    } else {
        stop_CS(left_moto, right_moto);
    }
}
