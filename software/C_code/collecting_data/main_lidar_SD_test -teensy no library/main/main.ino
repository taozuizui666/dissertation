#include <SoftwareSerial.h>
#include <SPI.h>
#include <SD.h>
#include "control_slide.h"
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
#define lidar_baud         115200
#define V_car       70       // velocity of the car
#define Sensi       1         // sensitivity of control ; bigger than more sensitive
#define Lidar_head_num      7     //A5 5A 05 00 00 40 81 
#define Lidar_data_bin_num  5

#define time_of_round       160     ////-------------------about 147 ms a round------------------
#define num_of_round        250     // the number of data after a round   250
#define NUM_of_yield        50      // how many rounds to yield
#define NUM_to_store        50      // how many rounds to store into SD

//-------------bluetooth----------------
int receive_bt = -1;             // data received from bluetooth
#define SD_start_store    255
bool SD_store  = 0;
//-------------SD_card------------------
////attention ! File is not FILE
File f;
#define FILE_NAME   "square.txt"

//-------------lidar_data---------------
bool Lidar_head_message = 0;
unsigned char   Lidar_data;
unsigned char   Lidar_init[Lidar_head_num];
unsigned char   Lidar_5byte[Lidar_data_bin_num];
int             Lidar_list_ang[num_of_round]; //*Lidar_data_bin_num
float           Lidar_list_dis[num_of_round]; //*Lidar_data_bin_num

uint16_t     angle_raw;
uint16_t     dist_raw;
float        angle_real;
float        dist_real;

long last_time = 0;
int flush_counter = 0;
bool is_recording = false;

void setup() {  
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
  f = SD.open(FILE_NAME,FILE_WRITE);
  f.close();
  // f.print(0);
  // f.print('\n');
  // f.flush();
  //// control the spin speed of lidar
  analogWrite(Lidar_ctr, 255); 
  // connect to bluetooth
  Serial1.begin(bluetooth_baud);
  //-------------Lidar---------------------
  //// connect RX2/TX2 to lidar's RX/TX
  Serial2.begin(lidar_baud);
  //// turn on the lidar to receive data
  //// attention! lidar can only receive data when it is spinning
  Serial2.write(0xA5);
  Serial2.write(0x40);    // Reset RPLidar
  delay(3000);
  Serial2.write(0xA5);
  Serial2.write(0x20);    // command RPLidar to spin  
  //-------------end of setup()-----------
}

void loop() {
  //-------------bluetooth 控制与文件管理----------------
  if(Serial1.available()) {
    receive_bt = Serial1.read();
    
    // 收到 255: 开始记录
    if(receive_bt == 255) {
      if (!is_recording) {
        // 只有在还没开始时才打开文件
        f = SD.open(FILE_NAME, FILE_WRITE);
        if (f) {
          is_recording = true;
          digitalWrite(2, HIGH);
        } 
      }
    } 
    // 收到 200: 停止记录并保存
    else if(receive_bt == 200) {
      if (is_recording) {
        is_recording = false;
        f.close(); // 此时才关闭文件，确保数据写入
        digitalWrite(2, LOW);   
      }
    }    
    slide_control(receive_bt, V_car, LEFT_MOTO, RIGHT_MOTO, Sensi);
  }

  //----------------------lidar 数据处理--------------------------------
  // 如果还在等待头部，读取数据
  if((!Lidar_head_message) && (Serial2.available() >= Lidar_head_num)) {
    // 快速丢弃缓冲区里的头部数据，防止堆积
    for(int i=0; i<Lidar_head_num; i++) {
      Serial2.read();
    }
    Lidar_head_message = 1;
    last_time = millis(); // 重置计时器
  }
  // 进入数据采集循环
  if (Lidar_head_message) {
    digitalWrite(3, HIGH);
    // 如果还没超时，拼命读数据
    if (millis() - last_time <= time_of_round) {
      while (Serial2.available() >= Lidar_data_bin_num) {
         // 读取5个字节
         for(int i=0; i<Lidar_data_bin_num; i++) {
           Lidar_5byte[i] = Serial2.read();
         }
         
         // 解析
         angle_raw = (((uint16_t)Lidar_5byte[2] << 8) | Lidar_5byte[1]) >> 1;
         dist_raw = (((uint16_t)Lidar_5byte[4] << 8) | Lidar_5byte[3]);
         angle_real = angle_raw / 64.0;
         dist_real = dist_raw / 4.0;
         
         if(dist_real < 20000) {
           int index = (int)(angle_real / 360.0f * (float)num_of_round);
           if (index >= 0 && index < num_of_round) {
              if(dist_real == 0 && index > 0) {
                Lidar_list_dis[index] = 0;//Lidar_list_dis[index-1];
              } else {
                Lidar_list_dis[index] = dist_real;
              }
           }
         }
      }
    } 
    else {
      // ------------------- 时间到 (一圈结束) -------------------
      
      // 1. 如果正在录制，写入SD卡
      if(is_recording && f) {
        // 构建一个长字符串写入通常比多次调用 print 更快，或者直接循环 print
        for(int i=0; i<num_of_round; i++){
          f.print(Lidar_list_dis[i]);
          f.print(',');
          // 每打印几个数据 yield 一次，防止看门狗咬人
          if (i % NUM_of_yield == 0) yield(); 
        }
        f.println(receive_bt);
        
        // 每10圈数据物理保存一次，避免每次都操作Flash
        flush_counter++;
        if (flush_counter > NUM_to_store) {
          f.flush(); 
          flush_counter = 0;
        }
      }
      
      // 2. 关键步骤：写入SD卡消耗了时间，此时串口缓冲区堆满了旧数据
      // 必须清空缓冲区，否则下一圈读到的全是延迟数据
      // 清空缓冲区里能组成完整 5 字节的数据包
      int avail = Serial2.available();
      int full_packets = avail / 5;  // 能组成多少个完整包

      for (int p = 0; p < full_packets; p++) {
        for (int b = 0; b < 5; b++) {
          if (Serial2.available()) Serial2.read();
        }
      }

      last_time = millis(); // 重置计时器
    }
  }
}
// int map(float x, int in_min, int in_max, int out_min, int out_max)
// {
// 	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
// }