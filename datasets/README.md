# Dataset Availability

The full acquisition datasets are external to this repository. The paper states
that data are available on request from the corresponding author; this snapshot
does not introduce a new data-distribution permission.

The notebook accepts one folder containing the original `.pkl` and `.pklp` files.
Set `EXTERNAL_DATASET_DIR` in its configuration cell, or place authorized local
copies in this folder. Waveform files are ignored by Git.

`inventory.json` records the sizes reported during dataset inspection. They count
128-point windows per selected channel, not individual ADC conversions. Original
observations have shape `(N, 3, 128)`; the main analysis selects channel index 1.
File-to-label assignments are filename-based and are not independently verified
physical fault diagnoses. File names do not certify distinct devices or sessions.

Pickle loading executes Python deserialization. Use only the original, trusted
project datasets. No waveform has been fabricated for the review snapshot.
