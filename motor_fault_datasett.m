% =========================================================================
% AI-Driven Fault Diagnostics: Synthetic Dataset Generator
% Target: PWM DC Motor Current Waveform Generation
% Author: Divyansh Singh
% =========================================================================

clear; clc; close all;

% --- Simulation Parameters ---
Fs = 10000;            % Sampling Frequency (10 kHz)
dt = 1 / Fs;           % Time step
T_total = 1.0;         % Duration per sample (1 second)
t = 0:dt:(T_total-dt); % Time vector
N = length(t);
num_samples = 30;      % Number of waveform samples per class

% --- Nominal Motor Constants ---
Ra_nom = 2.0;          % Armature Resistance (Ohms)
La_nom = 0.005;        % Armature Inductance (Henries)
Ke = 0.05;             % Back-EMF constant (V/(rad/s))
Kt = 0.05;             % Torque constant (Nm/A)
J = 0.0001;            % Inertia (kg*m^2)
b = 0.001;             % Friction coefficient (Nm*s/rad)
V_supply = 12.0;       % Supply Voltage (Volts)
pwm_freq = 1000;       % PWM Frequency (1 kHz)
duty_cycle = 0.6;      % 60% Duty Cycle

% --- Generate PWM Signal ---
pwm_signal = double(mod(t, 1/pwm_freq) < (duty_cycle / pwm_freq)) * V_supply;

% --- Output Matrix: [Sample_ID, Label, Current_Waveform...] ---
% Labels: 0 = Healthy, 1 = Electrical Fault, 2 = Mechanical Fault
dataset = [];

fprintf('Generating synthetic current waveforms...\n');

for class_id = 0:2
    for s = 1:num_samples
        % Reset states
        i_arm = 0;
        omega = 0;
        current_wave = zeros(1, N);
        
        % Set parameters based on health condition
        Ra = Ra_nom;
        La = La_nom;
        TL_base = 0.1;
        
        if class_id == 1 
            % Electrical Fault: Winding short reduces resistance by 30-50%
            Ra = Ra_nom * (0.5 + 0.2*rand()); 
        elseif class_id == 2 
            % Mechanical Fault: Oscillating load torque (imbalance)
            f_fault = 25 + 5*rand(); % Fault frequency 25-30 Hz
        end
        
        % Euler Numerical Integration
        for k = 1:N
            V_in = pwm_signal(k);
            
            % Mechanical Load Torque
            if class_id == 2
                TL = TL_base + 0.08 * sin(2*pi*f_fault*t(k));
            else
                TL = TL_base;
            end
            
            % Differential Equations
            di_dt = (V_in - Ra*i_arm - Ke*omega) / La;
            domega_dt = (Kt*i_arm - b*omega - TL) / J;
            
            % Update States
            i_arm = i_arm + di_dt * dt;
            omega = omega + domega_dt * dt;
            
            % Add Measurement Noise
            current_wave(k) = i_arm + 0.02 * randn();
        end
        
        % Append to dataset row: [Class_Label, i_t0, i_t1, ...]
        dataset = [dataset; class_id, current_wave];
    end
end

% --- Save to CSV ---
writematrix(dataset, 'motor_fault_dataset.csv');
fprintf('Success! Saved %d samples to motor_fault_dataset.csv\n', size(dataset,1));

% --- Plot Sample Comparison ---
figure('Name', 'Motor Current Waveforms');
subplot(3,1,1); plot(t(1:1000), dataset(1, 2:1001), 'g'); 
title('Healthy State'); ylabel('Current (A)'); grid on;
subplot(3,1,2); plot(t(1:1000), dataset(num_samples+1, 2:1001), 'r'); 
title('Electrical Fault (Winding Short)'); ylabel('Current (A)'); grid on;
subplot(3,1,3); plot(t(1:1000), dataset(2*num_samples+1, 2:1001), 'm'); 
title('Mechanical Fault (Rotor Imbalance)'); ylabel('Current (A)'); xlabel('Time (s)'); grid on;