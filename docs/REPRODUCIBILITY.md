# Reproduction Instructions

## Environment

Use Python 3.11 and install `requirements-notebooks.txt` from the root directory.
The supplied Random Forest loads under scikit-learn 1.6.1. Do not use the older
100-tree model from the original project as a substitute for the included candidate.
Other package versions from the historical training run are not fully recovered.

`reports/validation_environment.json`, when present, describes local snapshot
verification only. It is not the historical training environment or a full lockfile.
Capture a new execution environment with:

```powershell
.\.venv\Scripts\python.exe -m pip freeze > execution-environment.txt
```

## Main Notebook

Start JupyterLab from the repository root and open
`training_notebooks/cold_head_model_comparison_and_export.ipynb`.
Set `EXTERNAL_DATASET_DIR` to the authorized dataset folder. Leave `CHANNEL_INDEX=1`,
`RANDOM_STATE=42`, `MAX_SAMPLES_PER_FILE=25000` and `MAX_SAMPLES_PER_CLASS=50000`
to follow the recorded re-evaluation protocol. Execute cells in order.

The selected channel is the second channel (zero-based index 1). The supervised
sample has 125,000 windows: Maintenance 50,000, Normal 50,000, Compressor Down 25,000.
Per-file extraction uses NumPy `default_rng(42).choice(..., replace=False)`, with
selected indices sorted. Class-level sampling uses a fresh generator with seed 42.
The metadata field `sample_index` is an index after file sampling; it is not a
persisted index into the original pickle file. Exact historical index lists are
unavailable. Matching results requires the same files, row order and compatible
software behavior, not just the RF seed.

The exploratory clustering set follows a different path: six labeled files are
capped at 25,000 windows each, and 2,343 NASA windows are included. This gives
152,343 observations when the inventory matches. Eight statistics are standardized
and projected onto two PCA components before clustering. No supervised holdout is
defined for this exploratory geometry. Internal scores exclude noise, but include
unlabeled NASA observations; ARI and NMI exclude rows with unknown reference labels.
The timing column measures `fit_predict` only, excluding preprocessing and metrics.
Full silhouette evaluation and OPTICS can take substantial CPU time and memory.

The deployable K-means path instead uses five standardized features with no PCA.
Its fitted scaler, centroids, majority-vote mapping and distance threshold are
serialized together. The candidate K-means pickle is not included in this snapshot.

The RF uses a stratified random 75/25 split and a fresh
`Pipeline(StandardScaler(), RandomForestClassifier(...))`. Scaling is fitted on the
training split only. Leave-one-file-out creates a new pipeline per fold and fits
scaling only on the remaining files. The sole compressor-down file cannot form a
closed-set LOFO test because removing it removes class 2 from training.

## Outputs and GUI Deployment

`OUTPUT_DIR` is `Path.cwd() / 'trained_models'`, so the output folder is relative to
the kernel working directory, not necessarily the notebook file. Model reports
have separate K-means and RF filenames. Training outputs are ignored by Git.
The exported RF remains fitted on the 75% training split used for evaluation;
the notebook does not silently refit it on all data after scoring.

To test a newly validated RF in the GUI, copy the notebook's
`random_forest_model_candidate.pkl` to the repository root, intentionally replacing
the candidate only after comparison. The GUI searches for:

1. `cold_head_status_model.pkl`
2. `random_forest_model_candidate.pkl`
3. `random_forest_model.pkl`

Only item 2 is shipped here. A new K-means export is named
`cold_head_status_model_candidate.pkl`; choosing it for the GUI requires an explicit
rename to item 1. Do not introduce item 1 when intending to test the RF.

## Figures

- `generate_thesis_diagrams.py`: integration schematic and proposed controlled-update
  workflow. The workflow is an architectural description; automatic anomaly storage
  and model retraining are not implemented by the live RF path.
- `tools/generate_dataset_composition.py`: labeled inventory only, no NASA entry;
  output is `thesis_figures/03_dataset_composition.png`.
- Notebook's Report figures cell: data-dependent plots under
  `OUTPUT_DIR / 'report_figures'`.

The waveform figure shows pointwise means of 12 selected windows per class, seed 42,
without smoothing. The windows are not phase-aligned; their means are descriptive
summaries, not typical individual waveforms. Some Normal windows have flattened
extrema whose origin is unverified. Figure code retains the generic ADC-value axis
because a current calibration is not established.

The notebook's `05_random_forest_confusion_matrix.png` uses all sampled observations,
including training rows, despite an older inline comment mentioning holdout.
It must be captioned as a sampled-data diagnostic. Holdout accuracy comes from
the RF evaluation cell. Do not present that figure as independent test evidence.

## Offline Verification

```powershell
.\.venv\Scripts\python.exe tools\verify_repository.py
.\.venv\Scripts\python.exe tools\verify_repository.py --model
```

The first command uses the standard library to check Python syntax, notebook JSON,
main notebook cell syntax, cleaned outputs, and artifact hashes. The second also
loads the supplied model, checks classes and dimensions, and performs an interface
smoke test on a constant input. This generated input is a software check only;
it is not used for results, training, figures or scientific claims.

## Outstanding Experimental Records

Effective ADC timestamps/rate, analog conditioning and calibration, quantitative
oscilloscope errors, device serials, session identifiers, shutdown mechanism and
pressure during `dataset_no_comp.pkl` remain undocumented. File-separated validation
does not establish device-independent validation without those records.
