import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from micromlgen import port

print("Loading motor_fault_dataset.csv...")
data = pd.read_csv('motor_fault_dataset.csv', header=None)

labels = data.iloc[:, 0].values.astype(int)
waveforms = data.iloc[:, 1:].values

num_samples, signal_length = waveforms.shape
Fs = 10000

print(f"Dataset Loaded: {num_samples} samples, {signal_length} time-points per sample.")

print("Extracting FFT Frequency Features...")

freqs = rfftfreq(signal_length, 1/Fs)

X_fft = []
for i in range(num_samples):
    fft_vals = np.abs(rfft(waveforms[i]))
    X_fft.append(fft_vals)

X_fft = np.array(X_fft)

plt.figure(figsize=(10, 6))
class_names = ['Healthy State', 'Electrical Fault', 'Mechanical Fault']
colors = ['g', 'r', 'm']

for c in range(3):
    idx = np.where(labels == c)[0][0]
    plt.plot(freqs[1:1000], X_fft[idx][1:1000], label=class_names[c], color=colors[c], alpha=0.8)

plt.title('Frequency Spectrum (FFT) - Feature Space')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('fft_spectrum.png')
plt.show()

X_train, X_test, y_train, y_test = train_test_split(X_fft, labels, test_size=0.3, random_state=42, stratify=labels)

clf = RandomForestClassifier(n_estimators=20, max_depth=5, random_state=42)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
print("\n=== Model Performance ===")
print(classification_report(y_test, y_pred, target_names=class_names))

cpp_code = port(clf, classmap={0: 'Healthy', 1: 'Electrical Fault', 2: 'Mechanical Fault'})

with open('MotorClassifier.h', 'w') as file:
    file.write(cpp_code)

print("\nSuccess! C++ Header 'MotorClassifier.h' has been generated.")