% =========================================================================
% AI-Driven Fault Diagnostics: Synthetic Dataset Generator V2
% Target: PWM DC Motor Current Waveform Generation (Simulink)
% =========================================================================

clear; clc;

% --- Defaults ---
T0 = 0.05; A_imb = 0; R_ext = 1.0; Kt_motor = 0.055; Duty = 88; f_imb = 25;   
mdl = 'pmdc_hbridge_motor'; % Updated to your new model name
W = 4096; nRuns = 30; 
rng(1); % Seed for reproducible data

X = []; y = []; g = []; runId = 0;

fprintf('Starting Simulink Dataset Generation (90 runs total)...\n');

for c = 1:3
    for r = 1:nRuns
        runId = runId + 1;
        s = (c==2) * (0.10 + 0.15*rand); % winding-short severity (10-25%)
        
        in = Simulink.SimulationInput(mdl);
        in = in.setModelParameter('StopTime','4');
        in = in.setVariable('T0',       0.0475 + 0.005*rand);
        in = in.setVariable('Duty',     80 + 15*rand);
        in = in.setVariable('Kt_motor', 0.055 * (1-s));
        in = in.setVariable('R_ext',    1.0 * (1-s));
        in = in.setVariable('A_imb',    (c==3) * (0.02 + 0.04*rand));
        in = in.setVariable('f_imb',    22 + 5*rand);
        
        fprintf('Simulating Class %d, Run %d...\n', c, r);
        out = sim(in);
        
        ia = out.ia(15001:end); 
        ia = ia(:);
        
        for k = 1:W:(numel(ia)-W+1)
            X(end+1,:) = ia(k:k+W-1)'; 
            y(end+1,1) = c; 
            g(end+1,1) = runId;
        end
    end
end

save('pdm_dataset_v2.mat', 'X', 'y', 'g');
fprintf('Success! Saved pdm_dataset_v2.mat\n');