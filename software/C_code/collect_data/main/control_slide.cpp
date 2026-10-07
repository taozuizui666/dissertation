#include "core_pins.h"
#include "control_slide.h"
#define bias    10
void stop_CS(int left_moto,int right_moto)
{
    analogWrite(left_moto, 0);
    analogWrite(right_moto, 0);    
}

void ahead_CS(int v_car,int left_moto,int right_moto)
{
    analogWrite(left_moto, v_car + bias);
    analogWrite(right_moto, v_car);
}

void slide_control(int receive_bt,int v_car,int left_moto,int right_moto,int sensi)
{
    switch(receive_bt){
        case 200:
            stop_CS(left_moto,right_moto);
            break;
        case 201:
            ahead_CS(v_car,left_moto,right_moto);
            break;
        case 255:
            break; // start SD store
        default:
            analogWrite(left_moto,bias + v_car-(10-receive_bt)*sensi);
            analogWrite(right_moto, v_car+(10-receive_bt)*sensi);
            break;
    }
}