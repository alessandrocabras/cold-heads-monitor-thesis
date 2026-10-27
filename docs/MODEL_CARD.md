# Random Forest Candidate

## Artifact and Intended Use

`random_forest_model_candidate.pkl` is the GUI-oriented three-category classifier
selected for testing after the later re-evaluation. It estimates a present operating
category, not remaining useful life or time to failure. It has not been validated
as an autonomous maintenance authority.

Its SHA-256, observed pipeline parameters and training-row count are recorded in
`reports/model_metadata.json`. Load only the supplied trusted artifact or models
you trained yourself; joblib/pickle deserialization can execute code.

## Input and Output

- Input: a two-dimensional array `(n_windows, 128)` of recorded waveform values.
- Channel: second acquisition channel, zero-based index 1.
- Pipeline: per-position `StandardScaler` followed by a Random Forest.
- Labels: `0=Maintenance`, `1=Normal`, `2=Compressor Down`.
- Trees: 300; `random_state=42`; `class_weight='balanced'`; `n_jobs=-1`.
- Criterion: Gini; `max_features='sqrt'`; bootstrap enabled; unlimited depth;
  `min_samples_split=2`; `min_samples_leaf=1`.
- Scaler training support: 93,750 rows (75% of the 125,000 sampled observations).

Parameters not listed above are captured directly from the artifact in the metadata.
The model was loaded without a scikit-learn version mismatch under version 1.6.1.
This does not establish historical versions of NumPy, SciPy, joblib or Python.

## Evidence and Limits

Random holdout accuracy was reported as 0.999968. File holdout performance was
lower on `head_new.pkl` (0.85408). Compressor Down has only one labeled source file.
The name of that category does not establish that the acquisition captured an
actual hardware fault. Maintenance labels are service-hour proxies.

Apparent flattening near the extrema of some Normal windows may provide an
acquisition-specific cue; its origin and influence on predictions are unverified.
Randomly mixing windows from the same file across train/test can yield optimistic
scores even with correctly isolated scaling.

The RF always predicts one of the three known categories. It has no validated
novelty-rejection mechanism. `Unknown Anomaly` belongs to the optional K-means
distance rule and must not be attributed to this RF.

## K-Means Alternative

`cold_head_status_model.py` implements five features in order: mean, population
standard deviation, maximum, minimum and peak-to-peak range. A fitted StandardScaler
and three-cluster K-means are stored with the majority-label mapping.
The threshold is `max(training nearest-centroid distance) + 0.5` in standardized
feature space. The reported threshold was 1.881988390350367. Zero training rejection
is guaranteed by this construction and is not an independent anomaly benchmark.
