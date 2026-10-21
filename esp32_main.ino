#include <Arduino.h>
#include "pdm_infer.h"

const int CURRENT_SENSOR_PIN = 34; // ESP32 ADC pin connected to ACS712
const float ADC_VREF = 3.3f;
const float ADC_MAX = 4095.0f;     // 12-bit ADC max value
const float SENSOR_ZERO_V = 1.65f; // VCC/2 for 3.3V system
const float SENSOR_SENSITIVITY = 0.185f; // 185 mV/A for 5A ACS712

// Calculate microseconds per sample (1,000,000 / 10,000 = 100 us)
const uint32_t SAMPLE_PERIOD_US = 1000000 / PDM_FS; 

// Class labels corresponding to the 1, 2, 3 outputs from pdm_predict()
const char* CLASS_NAMES[] = {"Unknown", "Healthy", "Electrical Fault", "Mechanical Fault"};

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);
    pinMode(CURRENT_SENSOR_PIN, INPUT);

    // Initialize the FFT twiddle factors (must be called once at startup)
    pdm_init(); 
    
    Serial.println("ESP32 PdM Motor Fault Classifier Initialized.");
}

void loop() {
    // 1. Acquire 4096-sample window (0.4096 seconds at 10 kHz)
    for (int n = 0; n < PDM_N; n++) {
        uint32_t t_start = micros();
        
        // Read hardware ADC
        int raw_adc = analogRead(CURRENT_SENSOR_PIN);
        
        // Convert to Voltage, then to Amperes
        float voltage = (raw_adc * ADC_VREF) / ADC_MAX;
        pdm_re[n] = (voltage - SENSOR_ZERO_V) / SENSOR_SENSITIVITY;
        
        // Busy-wait to maintain deterministic 10 kHz sample rate
        while ((micros() - t_start) < SAMPLE_PERIOD_US) {
            // Wait
        }
    }

    // 2. Extract features and classify
    // Note: pdm_classify() does an in-place FFT, overwriting pdm_re[]
    float features[PDM_NFEAT];
    uint32_t t0 = micros();
    int cls = pdm_classify(features);
    uint32_t infer_us = micros() - t0;

    // 3. Serial Telemetry Output
    Serial.printf("State: %s | Mean I: %.2f A | Peak 18-32Hz: %.4f A | Inference Time: %.2f ms\n",
                  CLASS_NAMES[cls], features[0], features[PDM_NFEAT - 1], infer_us / 1000.0f);
}