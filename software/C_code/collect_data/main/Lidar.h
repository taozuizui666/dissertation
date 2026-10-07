#ifndef LIDAR_H
#define LIDAR_H

#include "Arduino.h"

#define lidar_baud         115200

#define RESULT_FAIL_BIT        0x80000000
#define RPLIDAR_RESP_MEASUREMENT_SYNCBIT        (0x1<<0)
#define RPLIDAR_RESP_MEASUREMENT_QUALITY_SHIFT  2
#define RPLIDAR_RESP_MEASUREMENT_CHECKBIT       (0x1<<0)
#define RPLIDAR_RESP_MEASUREMENT_ANGLE_SHIFT    1
#define RESULT_OPERATION_TIMEOUT  (0x8002 | RESULT_FAIL_BIT)
#define RPLIDAR_ANS_TYPE_MEASUREMENT      0x81

#define RPLIDAR_ANS_SYNC_BYTE1       0xA5
#define RPLIDAR_ANS_SYNC_BYTE2       0x5A

// typedef signed int int8_t __attribute__((__mode__(__QI__)));
// typedef unsigned int uint8_t __attribute__((__mode__(__QI__)));
// typedef signed int int16_t __attribute__ ((__mode__ (__HI__)));
// typedef unsigned int uint16_t __attribute__ ((__mode__ (__HI__)));
// // typedef signed int int32_t __attribute__ ((__mode__ (__SI__)));
// typedef unsigned int uint32_t __attribute__ ((__mode__ (__SI__)));
typedef signed char int8_t;
typedef unsigned char uint8_t;
// typedef signed int int16_t;
// typedef unsigned int uint16_t;
typedef signed long int int32_t;
typedef unsigned long int uint32_t;

typedef uint32_t u_result;

typedef struct _rplidar_ans_header_t {
    uint8_t  syncByte1; // must be RPLIDAR_ANS_SYNC_BYTE1
    uint8_t  syncByte2; // must be RPLIDAR_ANS_SYNC_BYTE2
    uint32_t size:30;
    uint32_t subType:2;
    uint8_t  type;
} __attribute__((packed)) rplidar_ans_header_t;

typedef struct _rplidar_response_measurement_node_t {
    uint8_t    sync_quality;      // syncbit:1;syncbit_inverse:1;quality:6;
    uint16_t   angle_q6_checkbit; // check_bit:1;angle_q6:15;
	uint16_t   distance_q2;
} __attribute__((packed)) rplidar_response_measurement_node_t;

struct RPLidarMeasurement
{
    float distance;
    float angle;
    uint8_t quality;
    bool  startBit;
};

class Lidar
{
public:
    enum {
        RPLIDAR_SERIAL_BAUDRATE = 115200,  
        RPLIDAR_DEFAULT_TIMEOUT = 500,
    };
    
    Lidar();  
    ~Lidar();

    u_result startScan(bool force = false, uint32_t timeout = RPLIDAR_DEFAULT_TIMEOUT*2);
    // wait for one sample point to arrive
    u_result waitPoint(uint32_t timeout = RPLIDAR_DEFAULT_TIMEOUT);
    
    // retrieve currently received sample point
    
    const RPLidarMeasurement & getCurrentPoint()
    {
        return _currentMeasurement;
    }

protected:
    u_result _waitResponseHeader(rplidar_ans_header_t * header, uint32_t timeout);

protected:
    RPLidarMeasurement _currentMeasurement;
};

#endif