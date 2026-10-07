#include "HardwareSerial.h"
#include "Lidar.h"

Lidar::Lidar()
{
    _currentMeasurement.distance = 0;
    _currentMeasurement.angle = 0;
    _currentMeasurement.quality = 0;
    _currentMeasurement.startBit = 0;
}


Lidar::~Lidar()
{

}

u_result Lidar::startScan(bool force, uint32_t timeout)
{    
    {
        Serial2.begin(lidar_baud);
        Serial2.write(0xA5);
        Serial2.write(0x20);        
        // waiting for confirmation
        rplidar_ans_header_t response_header;
        _waitResponseHeader(&response_header, timeout);


        // verify whether we got a correct header
        if (response_header.type != RPLIDAR_ANS_TYPE_MEASUREMENT) {
            return 1;
        }

        if (response_header.size < sizeof(rplidar_response_measurement_node_t)) {
            return 1;
        }
    }
    return 0;
}

// wait for one sample point to arrive
u_result Lidar::waitPoint(uint32_t timeout)
{
uint32_t currentTs = millis();
uint32_t remainingtime;
rplidar_response_measurement_node_t node;
uint8_t *nodebuf = (uint8_t*)&node;

uint8_t recvPos = 0;

while ((remainingtime=millis() - currentTs) <= timeout) {
        int currentbyte = Serial2.read();
        if (currentbyte<0) continue;

        switch (recvPos) {
            case 0: // expect the sync bit and its reverse in this byte          {
                {
                    uint8_t tmp = (currentbyte>>1);
                    if ( (tmp ^ currentbyte) & 0x1 ) {
                        // pass
                    } else {
                        continue;
                    }

                }
                break;
            case 1: // expect the highest bit to be 1
                {
                    if (currentbyte & RPLIDAR_RESP_MEASUREMENT_CHECKBIT) {
                        // pass
                    } else {
                        recvPos = 0;
                        continue;
                    }
                }
                break;
        }
        nodebuf[recvPos++] = currentbyte;

        if (recvPos == sizeof(rplidar_response_measurement_node_t)) {
            // store the data ...
            _currentMeasurement.distance = node.distance_q2/4.0f;
            _currentMeasurement.angle = (node.angle_q6_checkbit >> RPLIDAR_RESP_MEASUREMENT_ANGLE_SHIFT)/64.0f;
            _currentMeasurement.quality = (node.sync_quality>>RPLIDAR_RESP_MEASUREMENT_QUALITY_SHIFT);
            _currentMeasurement.startBit = (node.sync_quality & RPLIDAR_RESP_MEASUREMENT_SYNCBIT);
            return 0;
        }
        
}
return RESULT_OPERATION_TIMEOUT;
}

u_result Lidar::_waitResponseHeader(rplidar_ans_header_t * header, uint32_t timeout)
{
    uint8_t  recvPos = 0;
    uint32_t currentTs = millis();
    uint32_t remainingtime;
    uint8_t *headerbuf = (uint8_t*)header;
    while ((remainingtime=millis() - currentTs) <= timeout) {
        
        int currentbyte = Serial2.read();
        if (currentbyte<0) continue;
        switch (recvPos) {
        case 0:
            if (currentbyte != RPLIDAR_ANS_SYNC_BYTE1) {
                continue;
            }
            break;
        case 1:
            if (currentbyte != RPLIDAR_ANS_SYNC_BYTE2) {
                recvPos = 0;
                continue;
            }
            break;
        }
        headerbuf[recvPos++] = currentbyte;

        if (recvPos == sizeof(rplidar_ans_header_t)) {
            return 0;
        }


    }

    return 1;
}

