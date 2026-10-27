# Recorded Experimental Results

The re-evaluation numbers below were supplied as notebook console outputs by the
author. They are transcribed in `reports/reference_results.json`; they were not
recomputed while preparing this repository. The full waveform datasets are external.

## Published Stage

The paper reported silhouette 0.7848, Calinski-Harabasz 8.1762e6,
Davies-Bouldin 0.2163 and ARI 0.98. These belong to the published experiment.
Its documented workstation and Jetson inference timing must not be attributed
automatically to the later re-evaluation.

## Exploratory Clustering Re-evaluation

Eight waveform statistics, StandardScaler, two-component PCA, then clustering.
The code includes unlabeled NASA observations in this exploratory set.

| Method | Fit seconds | Clusters | Noise | Silhouette | ARI |
| --- | ---: | ---: | ---: | ---: | ---: |
| K-means-3 | 2.278682 | 3 | 0 | 0.566372 | 0.264671 |
| DBSCAN | 58.507852 | 2 | 0 | 0.745235 | 0.393194 |
| OPTICS | 524.496805 | 4 | 70 | 0.270895 | 0.879163 |

Scores refer to different partitions and do not identify a universal winner.
DBSCAN's strongest silhouette yielded only two groups. Hardware and complete
package versions for this run were not recorded. Fit times exclude preprocessing
and metric calculation. These numbers describe one configuration per method,
not an exhaustive hyperparameter search.

## Five-Feature K-Means Classifier

On the 125,000 labeled training windows, reported accuracy was approximately 0.60.
Rows/columns below are ordered Maintenance, Normal, Compressor Down:

```text
[[25133, 24864,     3],
 [24846, 25154,     0],
 [    0,     0, 25000]]
```

The threshold was 1.881988390350367 and no training window was rejected.
This is a fitted-training diagnostic; it is distinct from the PCA clustering table.

## Random Forest

The stratified random 25% holdout contained 31,250 windows and accuracy was
0.999968. The per-file table previously obtained using all sampled observations
also includes training windows and is not independent validation.

| File held out entirely | Windows tested | Accuracy |
| --- | ---: | ---: |
| dataset_1020.pkl | 16,642 | 1.00000 |
| dataset_arcetri_head.pkl | 25,000 | 1.00000 |
| dataset_k_receiver.pkl | 16,663 | 0.99982 |
| head_30k_ore.pkl | 16,695 | 0.99976 |
| head_new.pkl | 25,000 | 0.85408 |
| dataset_no_comp.pkl | -- | Skipped: class absent from remaining training files |

LOFO tests file separation. Distinct devices and independent sessions cannot be
certified from filenames alone. The weaker `head_new.pkl` fold suggests limited
transfer but does not establish its physical cause.

## Unlabeled NASA Data

| Model | Maintenance | Normal | Compressor Down |
| --- | ---: | ---: | ---: |
| K-means health classifier | 1,157 | 1,171 | 15 |
| RF candidate | 3 | 2,325 | 15 |

All 2,343 windows were excluded from supervised training and from fitting the
five-feature K-means health classifier. They were included in the separate
exploratory clustering comparison. No accuracy can be calculated without verified
reference labels. Equal Down counts do not prove identical selected windows.

## Figures Included Here

Architecture/workflow diagrams and the inventory-derived composition plot are
available in `thesis_figures/`. Data-dependent waveform, PCA and evaluation figures
can be regenerated with the main notebook when the original data are available.
No missing waveform plot is replaced with synthetic measurements.
