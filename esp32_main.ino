/*
 * esp32_main.ino - reference sketch for the PdM motor-fault classifier.
 *
 * STATUS: compiles against pdm_infer.h (checked on a PC with a stub Arduino
 * header) but has NOT been run on an ESP32. Bring-up checklist at the bottom.
 *
 * Arduino IDE: this file, pdm_infer.h and pdm_model.h must sit together in a
 * folder named "esp32_main". Board: "ESP32 Dev Module" (Arduino-ESP32 core 2.x/3.x).
 */
#include <Arduino.h>
#include "pdm_infer.h"

// ---------------- sensor front-end: edit to match your wiring ----------------
const int CURRENT_SENSOR_PIN = 34;            // GPIO34 = ADC1_CH6 (input only, no Wi-Fi conflict)

// The ACS712-05B is a 5 V part: output = 2.5 V at 0 A, +185 mV per amp, up to 5 V.
// That is too high for the ESP32 ADC (max ~3.1 V), so it must be divided down.
// Example: 10 kOhm (top) + 20 kOhm (bottom) -> ratio = 20 / (10 + 20) = 0.667.
const float DIVIDER_RATIO        = 2.0f / 3.0f;
const float SENSOR_V_PER_A       = 0.185f * DIVIDER_RATIO;   // volts at the ADC pin per amp
const float SENSOR_ZERO_V_NOMINAL = 2.5f * DIVIDER_RATIO;    // used only if calibration is skipped

// 10 kHz sampling: one sample every 100 us
const uint32_t SAMPLE_PERIOD_US = 1000000UL / PDM_FS;

// Class labels returned by pdm_classify(): 1, 2, 3
const char *CLASS_NAMES[] = {"Unknown", "Healthy", "Electrical Fault", "Mechanical Fault"};

float g_zero_v = SENSOR_ZERO_V_NOMINAL;       // measured zero-current voltage

// Volts at the ADC pin, using the ESP32's factory ADC calibration (not raw counts).
static inline float read_volts() {
    return (float)analogReadMilliVolts(CURRENT_SENSOR_PIN) * 0.001f;
}

// Average the sensor with the motor OFF to find the real zero-current voltage.
// The classifier relies on mean current, so an uncorrected offset hurts accuracy.
static float calibrate_zero_volts() {
    const int n = 4096;
    uint32_t sum_mv = 0;                       // 4096 * 3300 mV fits in 32 bits
    for (int i = 0; i < n; i++) {
        const uint32_t t0 = micros();
        sum_mv += analogReadMilliVolts(CURRENT_SENSOR_PIN);
        while ((micros() - t0) < SAMPLE_PERIOD_US) { }
    }
    return ((float)sum_mv / (float)n) * 0.001f;
}

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);
    pinMode(CURRENT_SENSOR_PIN, INPUT);
    pdm_init();                                // build FFT twiddle table (once)

    Serial.println("PdM classifier starting. Make sure the motor is OFF for zero calibration...");
    delay(3000);
    g_zero_v = calibrate_zero_volts();
    Serial.printf("Zero-current voltage: %.4f V (nominal %.4f V). Start the motor.\n",
                  g_zero_v, SENSOR_ZERO_V_NOMINAL);
    delay(2000);
}

void loop() {
    // 1. Acquire one 4096-sample window (0.4096 s at 10 kHz)
    uint32_t overruns = 0;
    const uint32_t t_win = micros();
    for (int n = 0; n < PDM_N; n++) {
        const uint32_t t_start = micros();
        pdm_re[n] = (read_volts() - g_zero_v) / SENSOR_V_PER_A;       // amps
        if ((micros() - t_start) > SAMPLE_PERIOD_US) overruns++;      // ADC too slow this sample
        while ((micros() - t_start) < SAMPLE_PERIOD_US) { }           // hold 10 kHz
    }
    const uint32_t win_us = micros() - t_win;

    // 2. Features + classification (overwrites pdm_re[] as FFT workspace)
    float features[PDM_NFEAT];
    const uint32_t t0 = micros();
    const int cls = pdm_classify(features);
    const uint32_t infer_us = micros() - t0;

    // 3. Telemetry. window_ms should be ~409.6; overruns should be 0.
    Serial.printf("State: %s | Mean I: %.3f A | Peak 18-32Hz: %.4f A | infer %.2f ms | window %.1f ms | overruns %lu\n",
                  CLASS_NAMES[cls], features[0], features[PDM_NFEAT - 1],
                  infer_us / 1000.0f, win_us / 1000.0f, (unsigned long)overruns);
}

/*
 * Bring-up checklist (do these in order on real hardware):
 *  1. Motor OFF: "Zero-current voltage" should be about 1.67 V (5 V sensor, 2/3 divider).
 *  2. Check "window" is ~409.6 ms and "overruns" is 0. If not, analogRead() is too slow
 *     or something is stealing CPU; move sampling to an ADC timer/DMA (I2S) instead.
 *  3. Motor ON, healthy: Mean I should match a bench ammeter within a few percent.
 *  4. Re-train with the real ADC step size if it differs from the simulated one
 *     (the simulation assumed 185 mV/A across the full 3.3 V range, about 4.4 mA per ADC step;
 *     with a 2/3 divider it is about 6.6 mA per step).
 *  5. Record real windows for each fault and check them against the simulated classes before trusting any accuracy figure.
 */
