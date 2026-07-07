# esp32-motor-diagnostics
AI-Driven Predictive Maintenance for PWM DC Motors

📌 Project Overview

This project bridges the gap between power electronics and TinyML. It aims to develop an intelligent Edge AI system capable of detecting anomalies and predicting mechanical/electrical faults in PWM-driven DC motors before catastrophic failure occurs.

Instead of relying on cloud computing, the machine learning inference runs locally on the microcontroller (Edge AI), making the system fast, secure, and independent of network latency.

🚀 Current Status: Phase 1 (Planning & Simulation)

This repository is currently being initialized. Active development is mapped out in the timeline below.

[x] Project architecture finalized.

[ ] MATLAB/Simulink models for healthy and faulty DC motors.

[ ] Synthetic data generation and feature extraction (FFT).

[ ] ML Model training (Python/TensorFlow).

[ ] Edge deployment on ESP32 (C++/TensorFlow Lite for Microcontrollers).

[ ] Physical hardware validation.

🏗️ System Architecture

The system pipeline consists of three major stages:

Simulation & Data Harvesting: Using MATLAB/Simulink to model DC motor physics and introduce deliberate faults (e.g., voltage sags, rotor imbalance).

Feature Extraction: Processing current and voltage waveforms using Fast Fourier Transform (FFT) to identify frequency harmonics unique to specific faults.

Edge Deployment: Training a lightweight neural network and compiling it via TensorFlow Lite to run directly on an ESP32 microcontroller attached to the physical motor.

💻 Tech Stack

Simulation: MATLAB, Simulink

Hardware: ESP32, L298N Motor Driver, 12V DC Motor, ACS712 Current Sensor

Machine Learning: Python, TensorFlow / Keras, TensorFlow Lite for Microcontrollers

Embedded Software: C++, Arduino IDE / PlatformIO

👨‍💻 Author

[Your Name] - 3rd Year Electrical Engineering, NIT Hamirpur

Note: Source code, CAD files, and ML datasets will be pushed to this repository as the project phases are completed.
