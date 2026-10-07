#include "Lidar.h"

void Lidar::stop() {
    Serial2.write(0xA5);
    Serial2.write(0x25);
    Serial2.flush();
    recvPos = 0;
}

u_result Lidar::startScan(bool force, uint32_t timeout) {
    // Serial2.begin(lidar_baud) is called once by the sketch before this method.
    stop();
    delay(20);
    while (Serial2.available() > 0) {
        Serial2.read();
    }
    currentMeasurement = RPLidarMeasurement{};
    Serial2.write(0xA5);
    Serial2.write(force ? 0x21 : 0x20);

    uint8_t header[7] = {};
    const u_result result = waitResponseHeader(header, timeout);
    if (result != RESULT_OK) {
        return result;
    }
    // Decode the wire bytes explicitly instead of relying on packed bitfields.
    const uint32_t descriptor = static_cast<uint32_t>(header[2]) |
        (static_cast<uint32_t>(header[3]) << 8) |
        (static_cast<uint32_t>(header[4]) << 16) |
        (static_cast<uint32_t>(header[5]) << 24);
    if (header[6] != 0x81 || (descriptor & 0x3FFFFFFFUL) != 5 ||
        (descriptor >> 30) != 1) {
        return RESULT_INVALID_DATA;
    }
    return RESULT_OK;
}

u_result Lidar::waitResponseHeader(uint8_t *header, uint32_t timeout) {
    uint8_t pos = 0;
    const uint32_t started = millis();
    while (static_cast<uint32_t>(millis() - started) < timeout) {
        const int value = Serial2.read();
        if (value < 0) {
            continue;
        }
        if (pos == 0 && value != 0xA5) {
            continue;
        }
        if (pos == 1 && value != 0x5A) {
            pos = value == 0xA5 ? 1 : 0;
            continue;
        }
        header[pos++] = static_cast<uint8_t>(value);
        if (pos == 7) {
            return RESULT_OK;
        }
    }
    return RESULT_OPERATION_TIMEOUT;
}

u_result Lidar::waitPoint(uint32_t timeout) {
    const uint32_t started = millis();
    while (static_cast<uint32_t>(millis() - started) < timeout) {
        const int value = Serial2.read();
        if (value < 0) {
            continue;
        }
        const uint8_t byte = static_cast<uint8_t>(value);
        if (recvPos == 0 && ((byte ^ (byte >> 1)) & 1) == 0) {
            continue;
        }
        if (recvPos == 1 && (byte & 1) == 0) {
            recvPos = 0;
            // This byte may itself be the beginning of the next packet.
            if (((byte ^ (byte >> 1)) & 1) != 0) {
                packet[recvPos++] = byte;
            }
            continue;
        }
        packet[recvPos++] = byte;
        if (recvPos != sizeof(packet)) {
            continue;
        }
        recvPos = 0;
        const uint16_t angleQ6 =
            (static_cast<uint16_t>(packet[1]) |
             (static_cast<uint16_t>(packet[2]) << 8)) >> 1;
        if (angleQ6 >= 360 * 64) {
            continue;
        }
        const uint16_t distanceQ2 = static_cast<uint16_t>(packet[3]) |
            (static_cast<uint16_t>(packet[4]) << 8);
        currentMeasurement.distance = distanceQ2 / 4.0f;
        currentMeasurement.angle = angleQ6 / 64.0f;
        currentMeasurement.quality = packet[0] >> 2;
        currentMeasurement.startBit = (packet[0] & 1) != 0;
        return RESULT_OK;
    }
    // Keep partial packets for the next call; the old point is not new data.
    return RESULT_OPERATION_TIMEOUT;
}
