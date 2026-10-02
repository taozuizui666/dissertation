#include <SoftwareSerial.h>
#include <RPLidar.h>
#include "control_slide.h"
#include "randomForest.h"

// ports

#define Lidar_ctr     8   //control the spin speed of lidar 
#define LEFT_MOTO     9
#define RIGHT_MOTO    6

// paras
#define serial_baud         115200
#define lidar_baud          115200
#define V_car               100       // velocity of the car
#define Sensi               1         // sensitivity of control ; bigger than more sensitive

#define degree_90           LIDAR_RESOLUTION/4
#define degree_270          3*LIDAR_RESOLUTION/4
#define LIDAR_RESOLUTION    200
#define time_of_round       150     ////-------------------about 147 ms a round------------------
#define k_best              8

//-------------Lidar--------------------
RPLidar lidar;
uint16_t distances[LIDAR_RESOLUTION];
Eloquent::ML::Port::RandomForest clf;

int lidarDataSelection[k_best] = {22, 23, 24, 25, 26, 27, 28, 29};

long last_time = 0;
uint8_t ML_contr=0;

void setup() {  

  for (int a = 0; a < LIDAR_RESOLUTION; a++) {
    distances[a] = 0;
  }
  lidar.begin(Serial);
  //-------------pin outputs---------------
  pinMode(Lidar_ctr, OUTPUT);
  pinMode(LEFT_MOTO, OUTPUT);
  pinMode(RIGHT_MOTO, OUTPUT);

  rplidar_response_device_info_t info;
  if (IS_OK(lidar.getDeviceInfo(info, 100))) {
      lidar.startScan();
      analogWrite(Lidar_ctr, 255);
      delay(1000);
  }
  last_time = millis();
  //---------------end of setup------------------
}

void loop() {
  while(millis() - last_time <= time_of_round){
    lidar.waitPoint();
    uint16_t dist = (uint16_t)lidar.getCurrentPoint().distance;
    uint16_t angl = (uint16_t)lidar.getCurrentPoint().angle;
    // uint16_t qual = (uint16_t)lidar.getCurrentPoint().quality;
    int index = (int)((angl / 360.0f) * (float)LIDAR_RESOLUTION);

    if((index<degree_90)||(index>degree_270)){
      if (dist<10000) {
        distances[index] = (uint16_t)dist;
      }else{}
    }
  }

  float selectedData[k_best];
  for (int i = 0; i < k_best; i++) {
    selectedData[i] = distances[lidarDataSelection[i]];
  }  

  ML_contr = clf.predict(selectedData);
  slide_control(ML_contr, V_car, LEFT_MOTO, RIGHT_MOTO, Sensi);

  // while (Serial.available()) {
  //   Serial.read();
  // }

  last_time = millis();
}
