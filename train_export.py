"""
train_export.py - compact Random Forest for motor-fault detection, exported to C++.

Pipeline
  1. load pdm_dataset_v2.mat (X windows, y labels 1/2/3, g run ids)
  2. hold out 20 % of the RUNS as a final test set (never used for tuning)
  3. compact band-energy features (mirrors pdm_infer.h exactly)
  4. choose training augmentation + forest size with grouped CV on the training runs only
  5. final test on the held-out runs under several sensor-error conditions
  6. export pdm_model.h and verify the C++ gives the same answers as Python

Usage:   python train_export.py            (needs numpy scipy scikit-learn matplotlib; g++ for step 6)
         python train_export.py --no-cpp   (skip the C++ parity check)
"""
import argparse, json, math, os, shutil, subprocess, sys, tempfile
import numpy as np
import scipy.io as sio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold, train_test_split
from sklearn.metrics import confusion_matrix

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="pdm_dataset_v2.mat")
ap.add_argument("--out", default=".")
ap.add_argument("--no-cpp", action="store_true")
args = ap.parse_args()
OUT = args.out
os.makedirs(OUT, exist_ok=True)

FS = 10_000
NAMES = {1: "healthy", 2: "electrical", 3: "mechanical"}
SEED = 42

# --------------------------------------------------------------------------
# 1. data
# --------------------------------------------------------------------------
d = sio.loadmat(args.data)
X = d["X"].astype(np.float64)
y = d["y"].ravel().astype(int)
g = d["g"].ravel().astype(int)
N = X.shape[1]
DF = FS / N
print(f"data: {X.shape}, runs: {len(np.unique(g))}")

# --------------------------------------------------------------------------
# 2. split by run (stratified by class)
# --------------------------------------------------------------------------
runs = np.unique(g)
run_cls = np.array([y[g == r][0] for r in runs])
tr_runs, te_runs = train_test_split(runs, test_size=0.2, stratify=run_cls, random_state=SEED)
tr = np.isin(g, tr_runs); te = np.isin(g, te_runs)
Wtr, ytr, gtr = X[tr], y[tr], g[tr]
Wte, yte, gte = X[te], y[te], g[te]
print(f"train: {len(tr_runs)} runs / {tr.sum()} windows | test: {len(te_runs)} runs / {te.sum()} windows")

# --------------------------------------------------------------------------
# 3. features (must mirror pdm_infer.h)
# --------------------------------------------------------------------------
BAND_EDGES_HZ = [2.5, 10, 18, 22, 26, 32, 45, 70, 120, 200]
def hz2bin(f): return int(math.ceil(f / DF - 1e-9))
EDGES = [hz2bin(f) for f in BAND_EDGES_HZ]
BAND_LO, BAND_HI = EDGES[:-1], EDGES[1:]
PEAK_LO, PEAK_HI = hz2bin(18), hz2bin(32)       # mechanical-fault search band
FLOOR_LO, FLOOR_HI = hz2bin(45), hz2bin(200)    # noise-floor band
NB = len(BAND_LO)
NFEAT = 1 + NB + 1
FEAT_NAMES = (["mean_A"] + [f"E_{BAND_EDGES_HZ[i]:g}-{BAND_EDGES_HZ[i+1]:g}Hz" for i in range(NB)]
              + ["peak_excess_18-32Hz"])
HANN = 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(N) / N)   # periodic Hann

def features(W):
    """Band energies with the estimated white-noise floor subtracted (clipped at 0),
    so the features do not depend on how noisy the current sensor is."""
    mean = W.mean(1, keepdims=True)
    S = np.fft.rfft((W - mean) * HANN, axis=1)
    a2 = (2.0 / N) ** 2 * (S.real ** 2 + S.imag ** 2)
    fl = a2[:, FLOOR_LO:FLOOR_HI].mean(1)                 # noise power per bin
    cols = [mean[:, 0]]
    for lo, hi in zip(BAND_LO, BAND_HI):
        cols.append(np.maximum(a2[:, lo:hi].sum(1) - (hi - lo) * fl, 0.0))
    pk2 = a2[:, PEAK_LO:PEAK_HI].max(1)
    cols.append(np.sqrt(np.maximum(pk2 - fl, 0.0)))
    return np.stack(cols, 1)

# --------------------------------------------------------------------------
# sensor error model (12-bit ADC, 185 mV/A current sensor)
# --------------------------------------------------------------------------
LSB = 3.3 / 4096 / 0.185
CONDS = {                       # name: (noise A rms, gain +/-, offset +/- A)
    "clean":  (0.00, 0.00, 0.00),
    "noise50": (0.05, 0.00, 0.00),
    "moderate": (0.02, 0.05, 0.05),
    "harsh":  (0.02, 0.10, 0.10),
}
def corrupt(W, cond, rng):
    noise, gain, off = CONDS[cond]
    Z = W.copy()
    if gain or off:
        Z = Z * (1 + gain * rng.uniform(-1, 1, (len(Z), 1))) + off * rng.uniform(-1, 1, (len(Z), 1))
    if noise:
        Z = Z + rng.normal(0, noise, Z.shape)
    Z = np.round(Z / LSB) * LSB                       # ADC quantisation
    return Z.astype(np.float32).astype(np.float64)    # exactly what the C++ will receive

def build(W, seed):
    rng = np.random.default_rng(seed)
    Wc = {c: corrupt(W, c, rng) for c in CONDS}
    return Wc, {c: features(Wc[c]) for c in CONDS}

Wtr_c, Ftr = build(Wtr, 1)
Wte_c, Fte = build(Wte, 2)

# --------------------------------------------------------------------------
# 4a. choose training augmentation by grouped CV on TRAIN runs
# --------------------------------------------------------------------------
AUGS = {"none": ["clean"], "moderate": ["clean", "moderate"], "harsh": ["clean", "moderate", "harsh"],
        "wide": ["clean", "noise50", "moderate", "harsh"]}
EVAL = ["clean", "noise50", "moderate", "harsh"]

def make_rf(n, depth):
    return RandomForestClassifier(n_estimators=n, max_depth=depth, random_state=SEED, n_jobs=-1)

def cv_scores(aug, n, depth):
    scores = {c: [] for c in EVAL}
    for a, b in GroupKFold(5).split(Wtr, ytr, gtr):
        Fa = np.vstack([Ftr[c][a] for c in AUGS[aug]]); ya = np.tile(ytr[a], len(AUGS[aug]))
        rf = make_rf(n, depth).fit(Fa.astype(np.float32), ya)
        for c in EVAL:
            scores[c].append((rf.predict(Ftr[c][b].astype(np.float32)) == ytr[b]).mean())
    return {c: float(np.mean(v)) for c, v in scores.items()}

print("\n[aug choice] 30 trees, depth 8, grouped 5-fold CV on training runs")
aug_res = {}
for aug in AUGS:
    s = cv_scores(aug, 30, 8)
    aug_res[aug] = s
    print(f"  train aug {aug:<9s}: " + "  ".join(f"{c} {s[c]:.3f}" for c in EVAL) + f"  | mean {np.mean(list(s.values())):.3f}")
AUG = max(aug_res, key=lambda a: np.mean(list(aug_res[a].values())))
print("  -> using training augmentation:", AUG)

# --------------------------------------------------------------------------
# 4b. model-size sweep
# --------------------------------------------------------------------------
def model_bytes(rf):
    nodes = sum(e.tree_.node_count for e in rf.estimators_)
    leaves = sum(int((e.tree_.children_left == -1).sum()) for e in rf.estimators_)
    return nodes * (1 + 4 + 2 + 2) + leaves * len(rf.classes_) * 4 + 2 * len(rf.estimators_), nodes, leaves

TREES = [5, 10, 20, 30, 50]
DEPTHS = [4, 6, 8, 12]
Fall = np.vstack([Ftr[c] for c in AUGS[AUG]]).astype(np.float32)
yall = np.tile(ytr, len(AUGS[AUG]))
sweep = []
print("\n[sweep] trees x depth: CV accuracy (mean of the 4 sensor conditions) and size")
for n in TREES:
    for dp in DEPTHS:
        s = cv_scores(AUG, n, dp)
        rf = make_rf(n, dp).fit(Fall, yall)
        size, nodes, leaves = model_bytes(rf)
        sweep.append(dict(trees=n, depth=dp, acc=float(np.mean(list(s.values()))),
                          acc_clean=s["clean"], acc_mod=s["moderate"], acc_harsh=s["harsh"],
                          bytes=size, nodes=nodes))
        print(f"  trees {n:>2d} depth {dp:>2d}: acc {sweep[-1]['acc']:.3f}  size {size/1024:6.1f} KB  nodes {nodes}")
best = max(r["acc"] for r in sweep)
ok = [r for r in sweep if r["acc"] >= best - 0.01]
CHOSEN = min(ok, key=lambda r: r["bytes"])
print(f"\n  best CV accuracy {best:.3f}; smallest model within 1 point: "
      f"{CHOSEN['trees']} trees, depth {CHOSEN['depth']}, {CHOSEN['bytes']/1024:.1f} KB")

# --------------------------------------------------------------------------
# 5. final model and held-out test
# --------------------------------------------------------------------------
rf = make_rf(CHOSEN["trees"], CHOSEN["depth"]).fit(Fall, yall)
size_bytes, n_nodes, n_leaves = model_bytes(rf)

def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0, c - h), min(1, c + h)

print(f"\n[held-out test] {te.sum()} windows from {len(te_runs)} runs never used for tuning")
test_res, cms = {}, {}
for c in CONDS:
    pred = rf.predict(Fte[c].astype(np.float32))
    k = int((pred == yte).sum()); lo, hi = wilson(k, len(yte))
    cms[c] = confusion_matrix(yte, pred, labels=[1, 2, 3])
    test_res[c] = dict(correct=k, total=int(len(yte)), acc=k / len(yte), ci95=[lo, hi])
    print(f"  {c:<9s}: {k}/{len(yte)} = {k/len(yte):.3f}   (95% CI {lo:.3f}-{hi:.3f})")

# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.5))
for dp, mk in zip(DEPTHS, "osd^"):
    pts = [r for r in sweep if r["depth"] == dp]
    ax.plot([r["bytes"] / 1024 for r in pts], [100 * r["acc"] for r in pts], marker=mk, label=f"depth {dp}")
ax.scatter([CHOSEN["bytes"] / 1024], [100 * CHOSEN["acc"]], s=220, facecolors="none", edgecolors="k", linewidths=2, label="chosen")
ax.set_xscale("log"); ax.set_xlabel("model size in flash [KB]"); ax.set_ylabel("grouped-CV accuracy [%]  (mean of 4 sensor conditions)")
ax.set_title("Accuracy vs model size"); ax.grid(alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig_accuracy_vs_size.png"), dpi=150); plt.close(fig)

fig, axs = plt.subplots(1, 4, figsize=(15, 3.8))
for ax, c in zip(axs, ["clean", "noise50", "moderate", "harsh"]):
    cm = cms[c]; ax.imshow(cm, cmap="Blues")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, cm[i, j], ha="center", va="center", color="w" if cm[i, j] > cm.max() / 2 else "k")
    ax.set_xticks(range(3)); ax.set_yticks(range(3))
    ax.set_xticklabels([NAMES[i] for i in (1, 2, 3)], rotation=20); ax.set_yticklabels([NAMES[i] for i in (1, 2, 3)])
    ax.set_xlabel("predicted"); ax.set_ylabel("true")
    ax.set_title(f"{c}: {test_res[c]['acc']*100:.1f}%")
fig.suptitle("Held-out test runs"); fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig_confusion_test.png"), dpi=150); plt.close(fig)

# --------------------------------------------------------------------------
# 6a. export pdm_model.h
# --------------------------------------------------------------------------
feat, thr, left, right, leafp, roots = [], [], [], [], [], []
for est in rf.estimators_:
    t = est.tree_; base = len(feat); roots.append(base)
    for i in range(t.node_count):
        if t.children_left[i] == -1:
            v = t.value[i, 0, :]; v = v / v.sum()
            feat.append(-1); thr.append(0.0); left.append(len(leafp) // 3); right.append(-1)
            leafp.extend(float(x) for x in v)
        else:
            feat.append(int(t.feature[i])); thr.append(float(np.float32(t.threshold[i])))
            left.append(base + int(t.children_left[i])); right.append(base + int(t.children_right[i]))
assert max(left + right) < 32767 and list(rf.classes_) == [1, 2, 3]

def carr(ctype, name, vals, fmt, per=8):
    lines = [", ".join(fmt(v) for v in vals[i:i + per]) for i in range(0, len(vals), per)]
    return f"static const {ctype} {name}[{len(vals)}] = {{\n    " + ",\n    ".join(lines) + "\n};\n"
ff = lambda v: f"{v:.9e}f"
with open(os.path.join(OUT, "pdm_model.h"), "w") as f:
    f.write("// GENERATED by train_export.py - do not edit.\n#ifndef PDM_MODEL_H\n#define PDM_MODEL_H\n#include <stdint.h>\n\n")
    f.write(f"#define PDM_FS {FS}\n#define PDM_N {N}\n#define PDM_NCLASS 3\n#define PDM_NTREES {len(roots)}\n")
    f.write(f"#define PDM_NBANDS {NB}\n#define PDM_NFEAT {NFEAT}\n")
    f.write(f"#define PDM_PEAK_LO {PEAK_LO}\n#define PDM_PEAK_HI {PEAK_HI}\n#define PDM_FLOOR_LO {FLOOR_LO}\n#define PDM_FLOOR_HI {FLOOR_HI}\n\n")
    f.write("// feature order: " + ", ".join(FEAT_NAMES) + "\n")
    f.write(carr("int16_t", "PDM_BAND_LO", BAND_LO, str) + carr("int16_t", "PDM_BAND_HI", BAND_HI, str))
    f.write(carr("uint16_t", "PDM_ROOT", roots, str))
    f.write(carr("int8_t", "PDM_FEAT", feat, str, 16))
    f.write(carr("float", "PDM_THR", thr, ff, 6))
    f.write(carr("int16_t", "PDM_LEFT", left, str, 12))
    f.write(carr("int16_t", "PDM_RIGHT", right, str, 12))
    f.write(carr("float", "PDM_LEAF", leafp, ff, 6))
    f.write("\n#endif\n")

# --------------------------------------------------------------------------
# 6b. test vectors + C++ parity check (all four sensor conditions)
# --------------------------------------------------------------------------
Wv = np.vstack([Wte_c[c] for c in CONDS]).astype(np.float32); Fv = np.vstack([Fte[c] for c in CONDS]).astype(np.float32)
yv = np.tile(yte, len(CONDS))      # parity is checked on ALL four sensor conditions
Wv.tofile(os.path.join(OUT, "test_windows.bin")); Fv.tofile(os.path.join(OUT, "test_py_features.bin"))
py_pred = rf.predict(Fv)
parity = None
if not args.no_cpp and shutil.which("g++"):
    exe = os.path.join(tempfile.mkdtemp(), "test_pdm.exe" if os.name == "nt" else "test_pdm")
    cmd = ["g++", "-O2", "-std=c++11", "-Wall", "-Wextra", "-fno-exceptions", "-fno-rtti",
           os.path.join(OUT, "test_pdm.cpp"), "-I", OUT, "-o", exe, "-lm"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("\n[C++ build]", "OK, no warnings" if r.returncode == 0 and not r.stderr.strip() else (r.stderr or "failed"))
    if r.returncode == 0:
        csv = os.path.join(OUT, "cpp_out.csv")
        subprocess.run([exe, os.path.join(OUT, "test_windows.bin"), os.path.join(OUT, "test_py_features.bin"), csv], check=True)
        arr = np.genfromtxt(csv, delimiter=",", skip_header=1)
        c_full, c_model, c_feat = arr[:, 1].astype(int), arr[:, 2].astype(int), arr[:, 3:]
        Fv64 = Fv.astype(np.float64)
        rel = np.abs(c_feat - Fv64) / (np.abs(Fv64).max(0, keepdims=True) + 1e-30)   # fraction of column full scale
        parity = dict(
            windows=int(len(py_pred)),
            model_only_agree=int((c_model == py_pred).sum()),
            end_to_end_agree=int((c_full == py_pred).sum()),
            cpp_end_to_end_correct=int((c_full == yv).sum()),
            py_correct=int((py_pred == yv).sum()),
            feat_err_median_fullscale=float(np.median(rel)), feat_err_max_fullscale=float(rel.max()),
            worst_feature=FEAT_NAMES[int(np.unravel_index(rel.argmax(), rel.shape)[1])])
        print("[parity]", json.dumps(parity, indent=2))
elif not args.no_cpp:
    print("\n[C++ build] g++ not found - skipped (install MinGW-w64/MSYS2 or use WSL, then re-run)")

# --------------------------------------------------------------------------
# resource estimate + results file
# --------------------------------------------------------------------------
butterflies = (N // 2) * int(math.log2(N))
flops = butterflies * 10 + N * 6 + 3 * N                       # FFT + window/mean + band sums
depth_used = max(e.tree_.max_depth for e in rf.estimators_)
resources = dict(
    model_flash_bytes=size_bytes, nodes=n_nodes, leaves=n_leaves, trees=CHOSEN["trees"], max_depth=int(depth_used),
    ram_static_bytes=3 * 16 * 1024, window_seconds=N / FS, approx_flops=int(flops),
    tree_comparisons_max=CHOSEN["trees"] * int(depth_used))
summary = dict(dataset=dict(windows=int(len(y)), runs=int(len(runs)), train_runs=int(len(tr_runs)), test_runs=int(len(te_runs))),
               training_augmentation=AUG, aug_cv=aug_res, chosen=CHOSEN, test=test_res, parity=parity, resources=resources,
               features=FEAT_NAMES)
with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(summary, f, indent=2)
print("\n[resources]", json.dumps(resources, indent=2))
print("\nwrote: pdm_model.h, results.json, fig_accuracy_vs_size.png, fig_confusion_test.png, test vectors")
