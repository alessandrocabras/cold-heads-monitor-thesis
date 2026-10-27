# Cold Heads Monitor: Thesis Review Materials

Software, acquisition firmware, training notebooks and recorded evaluation results
for electrical condition monitoring of cryogenic cold heads used in radio astronomy.
This repository is a curated review snapshot prepared from the working project.
The published clustering experiment and the subsequent GUI-oriented re-evaluation
are separate experimental stages; their scores must not be treated as interchangeable.

Repository: https://github.com/alessandrocabras/cold-heads-monitor-thesis

## Start Here

- [Reviewer guide](docs/REVIEWER_GUIDE.md): map from thesis claims to files.
- [Experimental results](docs/RESULTS.md): recorded scores and their limitations.
- [Reproduction instructions](docs/REPRODUCIBILITY.md): setup, training and figures.
- [Model card](docs/MODEL_CARD.md): supplied Random Forest, preprocessing and labels.
- [Dataset inventory](datasets/inventory.json): file counts and category assignments.
- [Firmware notes](fw/README.md): acquisition order, protocol and timing limitations.

The full waveform datasets are not distributed here. The supplied model, inventory,
diagrams and recorded scores can be inspected without them. Training and waveform
figures require the original datasets. No synthetic waveform data are substituted.

## Local Setup

Use Python 3.11. From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe tools\verify_repository.py
.\.venv\Scripts\python.exe tools\verify_repository.py --model
```

The scikit-learn version is pinned to `1.6.1` for the supplied candidate model.
Other dependency bounds define a supported setup, not a recovered historical lockfile.

## Graphical Interface

```powershell
.\.venv\Scripts\python.exe cold_heads_monitor_gui.py
```

The GUI opens without the instrument. Live acquisition requires the CHM hardware
and its reachable Ethernet address, entered in the connection panel. Saved local
connection settings are ignored by Git. The prototype endpoint embedded in the
source is an installation example, not a publicly reachable service.

## Notebooks and Figures

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-notebooks.txt
.\.venv\Scripts\python.exe -m jupyterlab training_notebooks
```

Open `cold_head_model_comparison_and_export.ipynb`, set `EXTERNAL_DATASET_DIR`
to the folder with the original pickle datasets, then follow the
[reproduction instructions](docs/REPRODUCIBILITY.md).

The two architecture/workflow diagrams and dataset-composition plot need no waveforms:

```powershell
.\.venv\Scripts\python.exe generate_thesis_diagrams.py
.\.venv\Scripts\python.exe tools\generate_dataset_composition.py
```

The composition plot excludes the unlabeled NASA file and uses the recorded inventory.

## Repository Layout

```text
.
|-- cold_heads_monitor_gui.py     Qt application
|-- cold_heads_monitor.py         TCP instrument interface
|-- plotter.py                    Acquisition worker and model inference
|-- cold_head_status_model.py     Five-feature K-means classifier
|-- random_forest_model_candidate.pkl
|-- training_notebooks/           Main comparison and export notebook
|-- fw/sketch/                    Main Arduino sketch
|-- docs/                         Methods, results and model documentation
|-- datasets/inventory.json       Metadata only; no raw waveforms
|-- reports/                      Recorded results and artifact hashes
|-- thesis_figures/               Available diagrams and inventory plot
|-- tools/                       Offline verification and figure generation
|-- archive/                     Historical notebooks and acquisition experiments
`-- dark/                        Qt stylesheet and image assets
```

## Attribution and Use

Related work: Cabras, A.; Ortu, P.; Pisanu, T.; Maxia, P.; Caocci, R.
*Incremental Clustering for Predictive Maintenance in Cryogenics for Radio Astronomy*,
Sensors (2024). See [AUTHORS.md](AUTHORS.md) for the published contribution statement.
When referring to this software snapshot, record its Git commit or release tag as
well as the paper citation. The review revision will be tagged `thesis-review-v1`.

Project-wide reuse licensing has not been assigned in this review snapshot.
Third-party notices are preserved; see [NOTICE.md](NOTICE.md).
Instructions to create a public repository are in [PUBLISHING.md](PUBLISHING.md).
