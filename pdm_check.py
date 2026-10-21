"""
PdM dataset check + Random Forest baseline.

Run from the folder that contains pdm_dataset_v2.mat:
    pip install numpy scipy scikit-learn
    python pdm_check.py
"""
import numpy as np
import scipy.io as sio
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import confusion_matrix

FS = 10_000          # sampling rate [Hz]
F_MAX = 200          # keep FFT bins up to this frequency [Hz]
NAMES = {1: "healthy", 2: "electrical", 3: "mechanical"}

# ---- load -----------------------------------------------------------------
d = sio.loadmat("pdm_dataset_v2.mat")
X = d["X"]                                   # windows x samples [A]
y = d["y"].ravel().astype(int)               # 1/2/3
g = d["g"].ravel().astype(int)               # run id -> used for grouped split
N = X.shape[1]
print("windows:", X.shape, "| runs:", len(np.unique(g)),
      "| per class:", {NAMES[c]: int((y == c).sum()) for c in NAMES})

# ---- features -------------------------------------------------------------
freqs = np.fft.rfftfreq(N, 1 / FS)
n_bins = np.searchsorted(freqs, F_MAX)
hann = np.hanning(N)

def features(windows):
    """log10 FFT magnitude, 0..F_MAX Hz (bin 0 carries the mean current)."""
    S = np.abs(np.fft.rfft(windows * hann, axis=1)) / N * 2
    return np.log10(S[:, :n_bins] + 1e-6)

# ---- realistic sensor errors (12-bit ADC, 185 mV/A current sensor) ---------
LSB = 3.3 / 4096 / 0.185                     # amps per ADC count
rng = np.random.default_rng(0)

def corrupt(w, noise=0.0, quantize=True, gain=0.0, offset=0.0):
    z = w.copy()
    if gain or offset:                       # per-window sensor gain / offset error
        z = z * (1 + gain * rng.uniform(-1, 1, (len(z), 1))) \
              + offset * rng.uniform(-1, 1, (len(z), 1))
    if noise:
        z = z + rng.normal(0, noise, z.shape)
    if quantize:
        z = np.round(z / LSB) * LSB
    return z

# ---- grouped cross-validation (windows of one run never split) -------------
def evaluate(label, **kw):
    F = features(corrupt(X, **kw))
    accs, pred = [], np.zeros_like(y)
    for tr, te in GroupKFold(n_splits=5).split(F, y, g):
        rf = RandomForestClassifier(n_estimators=100, random_state=0, n_jobs=-1)
        rf.fit(F[tr], y[tr])
        pred[te] = rf.predict(F[te])
        accs.append((pred[te] == y[te]).mean())
    print(f"{label:<46s} acc {np.mean(accs):.3f}  (worst fold {np.min(accs):.3f})")
    return pred

evaluate("clean + 12-bit quantization", noise=0.0)
evaluate("20 mA noise", noise=0.02)
evaluate("50 mA noise", noise=0.05)
evaluate("20 mA noise, gain +/-5%, offset +/-50 mA", noise=0.02, gain=0.05, offset=0.05)
pred = evaluate("20 mA noise, gain +/-10%, offset +/-100 mA", noise=0.02, gain=0.10, offset=0.10)

print("\nConfusion matrix for the last (hardest) case, rows = true class")
print("order:", [NAMES[c] for c in (1, 2, 3)])
print(confusion_matrix(y, pred, labels=[1, 2, 3]))