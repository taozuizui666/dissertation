#include "Arduino.h"
#include <SPI.h>
#include <SD.h>
#include "control_slide.h"
#include "Lidar.h"
// ports
#define Lidar_TX    7   //teensy RX2
#define Lidar_RX    8   //teensy TX2
#define Lidar_ctr   9   //control the spin speed of lidar
#define CS          10  //chip select(from SD_card module)
#define MOSI        11
#define MISO        12
#define SCK         13  //serial clk(from SD_card module)
#define LEFT_MOTO   14
#define RIGHT_MOTO  15
// paras
#define bluetooth_baud     9600
#define serial_baud        115200
#define V_car       150       // velocity of the car
#define Sensi       2         // sensitivity of control ; bigger than more sensitive


#define time_of_round       120     ////-------------------about 147 ms a round------------------
#define LIDAR_RESOLUTION    200     // the number of data after a round   250
#define degree_90           LIDAR_RESOLUTION/4
#define degree_270          3*LIDAR_RESOLUTION/4

#define NUM_of_yield        50      // how many rounds to yield
#define NUM_to_store        50      // how many rounds to store into SD

//-------------bluetooth----------------
int receive_bt = -1;             // data received from bluetooth

//-------------SD_card------------------
////attention ! File is not FILE
File f;
#define FILE_NAME   "data.txt"

//-------------lidar_data---------------
Lidar rplidar;
uint16_t distances[LIDAR_RESOLUTION];

long last_time = 0;
int flush_counter = 0;
bool is_recording = false;

void setup() {  

  for (int a = 0; a < LIDAR_RESOLUTION; a++) {
    distances[a] = 0;
  }
  // LED   
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  //-------------pin outputs---------------
  pinMode(Lidar_ctr, OUTPUT);
  pinMode(CS, OUTPUT);
  pinMode(LEFT_MOTO,OUTPUT);
  pinMode(RIGHT_MOTO,OUTPUT); 
  //------------test lidar's data--------
  // Serial.begin(serial_baud);
  //-------------SD_card------------------
  SD.begin(CS);
  // connect to bluetooth
  Serial1.begin(bluetooth_baud);
  //-------------Lidar---------------------
  //// connect RX2/TX2 to lidar's RX/TX
  Serial2.begin(lidar_baud);
  delay(1000);
  if(rplidar.startScan()==0){
    digitalWrite(3, HIGH);
    analogWrite(Lidar_ctr, 200); 
    delay(100);
  }else{
    // digitalWrite(2, HIGH);
    while (1){
      digitalWrite(3, HIGH);
      delay(500);
      digitalWrite(3, LOW);
      delay(500);
    }
  }
  last_time = millis();
  //-------------end of setup()-----------
}

void loop() {

  //----------------------lidar 数据处理--------------------------------

  while(millis() - last_time <= time_of_round){
    //-------------bluetooth 控制与文件管理----------------
    if(Serial1.available()) {
      receive_bt = Serial1.read();
          if(receive_bt == 255) {
        if (!is_recording) {
          f = SD.open(FILE_NAME, FILE_WRITE);
          if (f) {
            is_recording = true;
            digitalWrite(2, HIGH);
          } 
        }
      } 
      else if(receive_bt == 200) {
        if (is_recording) {
          is_recording = false;
          f.close(); 
          digitalWrite(2, LOW);   
        }
      }    
      slide_control(receive_bt, V_car, LEFT_MOTO, RIGHT_MOTO, Sensi);
    }    
    rplidar.waitPoint();
    uint16_t dist = (uint16_t)rplidar.getCurrentPoint().distance;
    uint16_t angl = (uint16_t)rplidar.getCurrentPoint().angle;
    
    int index = (int)((angl / 360.0f) * (float)LIDAR_RESOLUTION);

    if((index<degree_90)||(index>degree_270)){
      if (dist<10000) {
        distances[index] = (uint16_t)dist;
      }else{}
    }
  }
  if(is_recording==true){
    for(int i=0;i<LIDAR_RESOLUTION;i++) {
      f.print(distances[i]);
      f.print(',');
    }
    f.println(receive_bt);
  }else {}
  while (Serial.available()) {
    Serial.read();
  }
  last_time = millis();
  //---------------------end of loop-------------------------
}