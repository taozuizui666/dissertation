#include <Arduino.h>
#include "Lidar.h"
#include "control_slide.h"
#include "randomForest.h"

#if !defined(ARDUINO_TEENSY40)
#error "Select Teensy 4.0 in Tools > Board."
#endif

// Same wiring as the Teensy Lidar.h data-collection sketch.
// Lidar TX -> Teensy pin 7 (RX2); Lidar RX -> pin 8 (TX2).
constexpr uint8_t LIDAR_MOTOR_PIN = 9;
constexpr uint8_t LEFT_MOTOR_PIN = 14;
constexpr uint8_t RIGHT_MOTOR_PIN = 15;
constexpr uint8_t ERROR_LED_PIN = 2;
constexpr uint8_t READY_LED_PIN = 3;

constexpr int CAR_SPEED = 100;
constexpr int STEERING_SENSITIVITY = 2;
constexpr uint8_t LIDAR_MOTOR_PWM = 200;
constexpr uint32_t USB_BAUD = 115200;
constexpr uint32_t CONTROL_INTERVAL_MS = 150;
constexpr uint32_t FEATURE_TIMEOUT_MS = 500;
constexpr uint32_t POINT_TIMEOUT_MS = 5;
// Training inputs and class commands travel together with the model header.
constexpr uint16_t LIDAR_RESOLUTION = ModelConfig::LIDAR_RESOLUTION;
constexpr uint16_t MAX_DISTANCE_MM = ModelConfig::MAX_DISTANCE_MM;
constexpr uint16_t FEATURE_COUNT = ModelConfig::FEATURE_COUNT;
constexpr auto &FEATURE_INDICES = ModelConfig::FEATURE_INDICES;

Lidar lidar;
Eloquent::ML::Port::RandomForest classifier;
uint16_t distances[LIDAR_RESOLUTION] = {};
uint32_t featureUpdatedAt[FEATURE_COUNT] = {};
bool featureSeen[FEATURE_COUNT] = {};
bool lidarReady = false;
uint32_t lastControlAt = 0;
uint32_t lastDebugAt = 0;

bool featuresAreFresh(uint32_t now) {
    for (uint16_t i = 0; i < FEATURE_COUNT; ++i) {
        if (!featureSeen[i] ||
            static_cast<uint32_t>(now - featureUpdatedAt[i]) >= FEATURE_TIMEOUT_MS) {
            return false;
        }
    }
    return true;
}

void setup() {
    analogWriteResolution(8);
    pinMode(LIDAR_MOTOR_PIN, OUTPUT);
    pinMode(LEFT_MOTOR_PIN, OUTPUT);
    pinMode(RIGHT_MOTOR_PIN, OUTPUT);
    pinMode(ERROR_LED_PIN, OUTPUT);
    pinMode(READY_LED_PIN, OUTPUT);
    stop_CS(LEFT_MOTOR_PIN, RIGHT_MOTOR_PIN);
    analogWrite(LIDAR_MOTOR_PIN, 0);
    digitalWrite(ERROR_LED_PIN, LOW);
    digitalWrite(READY_LED_PIN, LOW);

    Serial.begin(USB_BAUD);  // USB debug only; never wait for a connected PC.
    Serial2.begin(lidar_baud);
    delay(1000);
    analogWrite(LIDAR_MOTOR_PIN, LIDAR_MOTOR_PWM);
    delay(100);
    lidarReady = lidar.startScan() == RESULT_OK;
    if (!lidarReady) {
        lidar.stop();
        analogWrite(LIDAR_MOTOR_PIN, 0);
    }
    lastControlAt = millis();
}

void loop() {
    if (!lidarReady) {
        stop_CS(LEFT_MOTOR_PIN, RIGHT_MOTOR_PIN);
        digitalWrite(ERROR_LED_PIN, (millis() / 500) % 2);
        return;  // Check wiring and reset the board to retry startup.
    }

    if (lidar.waitPoint(POINT_TIMEOUT_MS) == RESULT_OK) {
        const RPLidarMeasurement &point = lidar.getCurrentPoint();
        if (point.angle >= 0 && point.angle < 360 &&
            point.distance > 0 && point.distance < MAX_DISTANCE_MM &&
            point.quality > 0) {
            // Preserve the original integer-degree binning used during training.
            const uint16_t angle = static_cast<uint16_t>(point.angle);
            const uint16_t index = static_cast<uint16_t>(
                (angle / 360.0f) * LIDAR_RESOLUTION);
            if (ModelConfig::isActiveIndex(index)) {
                distances[index] = static_cast<uint16_t>(point.distance);
                for (uint16_t i = 0; i < FEATURE_COUNT; ++i) {
                    if (FEATURE_INDICES[i] == index) {
                        featureUpdatedAt[i] = millis();
                        featureSeen[i] = true;
                    }
                }
            }
        }
    }

    const uint32_t now = millis();
    if (!featuresAreFresh(now)) {
        stop_CS(LEFT_MOTOR_PIN, RIGHT_MOTOR_PIN);
        digitalWrite(ERROR_LED_PIN, HIGH);
        digitalWrite(READY_LED_PIN, LOW);
        return;
    }
    digitalWrite(ERROR_LED_PIN, LOW);
    digitalWrite(READY_LED_PIN, HIGH);
    if (static_cast<uint32_t>(now - lastControlAt) < CONTROL_INTERVAL_MS) {
        return;
    }
    lastControlAt = now;

    float selectedData[FEATURE_COUNT];
    for (uint16_t i = 0; i < FEATURE_COUNT; ++i) {
        selectedData[i] = distances[FEATURE_INDICES[i]];
    }
    const int command = ModelConfig::commandForClass(classifier.predict(selectedData));
    slide_control(command, CAR_SPEED, LEFT_MOTOR_PIN, RIGHT_MOTOR_PIN,
                  STEERING_SENSITIVITY);

    if (Serial && Serial.availableForWrite() >= 48 &&
        static_cast<uint32_t>(now - lastDebugAt) >= 500) {
        lastDebugAt = now;
        Serial.print("steering=");
        Serial.println(command);
    }
}
