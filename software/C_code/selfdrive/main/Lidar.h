#ifndef TEENSY_SELF_DRIVING_LIDAR_H
#define TEENSY_SELF_DRIVING_LIDAR_H

#include <Arduino.h>

// Based on collecting_data/main_lidar_SD_test -teensy -lidar.h/main/Lidar.*.
// Standard RPLIDAR scan protocol, using Teensy 4.0 Serial2 (RX=7, TX=8).
constexpr uint32_t lidar_baud = 115200;
using u_result = uint32_t;
constexpr u_result RESULT_OK = 0;
constexpr u_result RESULT_INVALID_DATA = 0x80008001UL;
constexpr u_result RESULT_OPERATION_TIMEOUT = 0x80008002UL;

struct RPLidarMeasurement {
    float distance = 0;  // millimetres
    float angle = 0;     // degrees
    uint8_t quality = 0;
    bool startBit = false;
};

class Lidar {
public:
    static constexpr uint32_t RPLIDAR_DEFAULT_TIMEOUT = 500;
    u_result startScan(bool force = false,
                       uint32_t timeout = RPLIDAR_DEFAULT_TIMEOUT * 2);
    void stop();
    u_result waitPoint(uint32_t timeout = RPLIDAR_DEFAULT_TIMEOUT);
    const RPLidarMeasurement &getCurrentPoint() const {
        return currentMeasurement;
    }

private:
    u_result waitResponseHeader(uint8_t *header, uint32_t timeout);
    RPLidarMeasurement currentMeasurement;
    uint8_t packet[5] = {};
    uint8_t recvPos = 0;
};

#endif
