# Guide for Thesis Reviewers

## Evidence Map

| Topic | Primary material | What can be checked locally |
| --- | --- | --- |
| Acquisition | `fw/sketch/`, `cold_heads_monitor.py` | Buffer size, channel order, TCP commands, ADC configuration |
| GUI | `cold_heads_monitor_gui.py`, `plotter.py` | Layout without hardware; live acquisition requires the CHM |
| Main re-evaluation | `training_notebooks/cold_head_model_comparison_and_export.ipynb` | Source is readable; full execution requires external datasets |
| Supplied model | `random_forest_model_candidate.pkl`, `reports/model_metadata.json` | Hash, pipeline, parameters, input shape and classes |
| Recorded results | `reports/reference_results.json`, `docs/RESULTS.md` | Author-provided scores, with their protocol and limits |
| Dataset composition | `datasets/inventory.json` | Recorded counts and labels; NASA is unlabeled |
| Diagrams | `generate_thesis_diagrams.py`, `thesis_figures/` | Direct regeneration without waveforms |
| Earlier experiments | `archive/` | Historical source, with execution output removed |

The main entry point for the analysis is the consolidated notebook, not the
archived files. Modules remain at repository root to preserve GUI imports and
pickle compatibility. The original working repository and its remote/history
are not copied into this independently initialized review repository.

## Reproducibility Boundaries

The source and supplied candidate are inspectable. The raw data, a full historical
environment lockfile, original sample indices and acquisition session log are not
present. Recorded results have not been recomputed when preparing this snapshot.
The offline verifier establishes integrity and software loading, not scientific
accuracy or instrument calibration.

Notebook outputs were removed from public copies to omit large embedded images,
machine-specific logs and stale execution results. Cell source is retained.
The preparation manifest records the source and exported hashes.

See `REPRODUCIBILITY.md` before executing the analysis, and `RESULTS.md` before
comparing metrics from the published and later experiments.
