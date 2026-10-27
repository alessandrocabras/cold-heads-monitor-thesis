# Historical Experiments

These files are kept for traceability, not as the main reproduction path.
Notebook cell source is preserved, while output, execution counts and transient
metadata are removed. They may contain Colab paths, unseeded shuffles, differing
window lengths, older APIs and provisional interpretations.

- `training_notebooks/`: earlier K-means, DBSCAN, OPTICS, inference and RF experiments.
- `notebooks/`: additional notebooks from the original working repository.
- `firmware/`: independent phase-timing experiments.
- `acquisition/`: historical recording/reading scripts with installation-specific paths.

The two historical recording scripts expect `cold_heads_monitor` at the root.
They are not standalone tools in this archive location. Execute only after
reviewing/adapting them for the available instrument and output paths.
They do not record device/session identifiers or per-window timestamps.

Repeated loading and preprocessing blocks are retained as historical evidence.
Use `training_notebooks/cold_head_model_comparison_and_export.ipynb` at repository
root for the consolidated analysis. The legacy `random_forest_model.pkl` is omitted;
the supplied 300-tree candidate is the documented review artifact.
