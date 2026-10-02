#include <SoftwareSerial.h>
#include <SPI.h>
#include <SD.h>
#include "control_slide.h"
#include "SD_card.h"
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
#define SCK_MHZ     10  // 10HZ
#define baud        115200
#define baud2       115200
#define bufsize     256       // SD_card's buf size
#define V_car       200       // velocity of the car
#define Sensi       1         // sensitivity of control ; bigger than more sensitive
#define Lidar_head_num      7     //A5 5A 05 00 00 40 81 
#define Lidar_data_bin_num  5
#define num_of_round        320   // the number of data after a round

//-------------bluetooth----------------
//// connect bluetooth to the board
SoftwareSerial bluetooth(0,1);  // bluetooth's pin RX,TX
int receive_bt = 0;             // data received from bluetooth
//-------------SD_card------------------
////attention ! File is not FILE
File f;
//-------------lidar_data---------------
bool Lidar_head_message;
bool new_start;                 // a round is finished
int  Lidar_list_index;
unsigned char   Lidar_data;
unsigned char   Lidar_init[Lidar_head_num];
unsigned char   Lidar_5byte[Lidar_data_bin_num];
unsigned char   Lidar_list[num_of_round*Lidar_data_bin_num];

//// millis time
unsigned long start_time;
const unsigned long runtime = 30*60*1000;

#define Method  2

void setup() {
  start_time = millis();
  //-------------Lidar---------------------
  //// connect RX2/TX2 to lidar's RX/TX
  Serial2.begin(baud2);
  //// turn on the lidar to receive data
  //// attention! lidar can only receive data when it is spinning

  Serial2.write(0xA5);
  Serial2.write(0x20);  
  //-------------pin outputs---------------
  pinMode(Lidar_ctr, OUTPUT);
  pinMode(CS, OUTPUT);
  pinMode(MOSI, OUTPUT);
  pinMode(SCK, OUTPUT);
  pinMode(LEFT_MOTO,OUTPUT);
  pinMode(RIGHT_MOTO,OUTPUT); 

  //// control the spin speed of lidar
  analogWrite(Lidar_ctr, 255);  
  //-------------bluetooth----------------
  bluetooth.begin(baud);  // bluetooth's 波特率
  //-------------SD_card------------------
  // SD_module_init(CS);     // initialize the SD_module and create Folder 
  // if(!SD.exists("Database/data0.txt"))
  // {
  //   f = SD.open("Database/data0.txt",FILE_WRITE);
  //   if(f){
  //     f.close();
  //   }
  // }
  //------------test lidar's data--------
  Serial.begin(baud);
  Lidar_head_message=0;
  new_start = 0;
  Lidar_list_index = 0;
  //-------------end of setup()-----------
}

void loop() {
  if(millis()-start_time < runtime){
    //-------------bluetooth----------------
    //// use bluetooth to control the car
    // if(bluetooth.available())
    // {
    //   receive_bt = bluetooth.read();
    //   slide_control(receive_bt,V_car,LEFT_MOTO,RIGHT_MOTO,Sensi);
    //   if(receive_bt==200)// when control_signal is "stop",then stop both car and lidar
    //   {Serial2.write(0xA5);
    //     Serial2.write(0x25);}
    // }
    if((!Lidar_head_message)&&(Serial2.available()==Lidar_head_num))
    {
      for(int i=0;i<Lidar_head_num;i++)
      {
        Lidar_data = Serial2.read();
        Serial.write(Lidar_data);
      }// release the reading buff, otherwise the message will stay in the buff
      Lidar_head_message = 1;
    }
    //--------------------------------------------------------
    //--------------------------------------------------------
    //// write data for a hole circle(each angle has 5byte data)
#if Method==1    
    while(new_start != 1)
    {
      if(Lidar_head_message && Serial2.available()>=Lidar_data_bin_num)
      {
        for(int i=0;i<Lidar_data_bin_num;i++,Lidar_list_index++)
        {
          Lidar_5byte[i] = Serial2.read();
          Lidar_list[Lidar_list_index] = Lidar_5byte[i];
        }
        if((Lidar_5byte[0] & 0x01) == 1)
        {
          new_start = 1;
        }
      }
    }
    f = SD.open("Database/data0.txt",FILE_WRITE);
    for(int i=0;i<Lidar_list_index;i++)
    {
      // Serial.write(Lidar_list[i]);
      //// Serial.print(Lidar_list[i]);
      ////----------write Lidar_list data to SD_card--------------
      f.print(Lidar_list[i]);
      f.print(",");
    }
    f.print("\n");
    f.close();
    Lidar_list_index = 0;
    new_start = 0;
    //--------------------------------------------------------
    //--------------------------------------------------------
#elif Method==2
    if(Lidar_head_message && Serial2.available()>=Lidar_data_bin_num)
    {
      for(int i=0;i<Lidar_data_bin_num;i++)
      {
        Lidar_5byte[i] = Serial2.read();
      }
      for(int i=0;i<Lidar_data_bin_num;i++)
      {
          Serial.write(Lidar_5byte[i]);
      } 
    }
#else

#endif
  //---------------big if---------------------  
  }else{
    analogWrite(Lidar_ctr,0);
    while(1);
  }
  //--------------end of loop()-------------
}
