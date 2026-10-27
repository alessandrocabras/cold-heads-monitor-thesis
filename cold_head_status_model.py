import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import StandardScaler


class KMeansHealthClassifier(BaseEstimator, ClassifierMixin):
    """K-Means classifier compatible with the CHM GUI raw waveform input."""

    def __init__(
        self,
        n_clusters=3,
        random_state=42,
        n_init=20,
        anomaly_margin=0.5,
        anomaly_label=3,
    ):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.n_init = n_init
        self.anomaly_margin = anomaly_margin
        self.anomaly_label = anomaly_label

    def fit(self, X, y):
        features = extract_waveform_features(X)
        self.scaler_ = StandardScaler()
        scaled_features = self.scaler_.fit_transform(features)

        self.kmeans_ = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=self.n_init,
        )
        cluster_labels = self.kmeans_.fit_predict(scaled_features)
        self.cluster_to_label_ = self._map_clusters_to_labels(cluster_labels, np.asarray(y))

        distances = self.kmeans_.transform(scaled_features)
        min_distances = np.min(distances, axis=1)
        self.distance_threshold_ = float(np.max(min_distances) + self.anomaly_margin)
        self.classes_ = np.unique(y)
        return self

    def predict(self, X):
        cluster_labels, min_distances = self.predict_clusters(X)
        status_labels = np.array(
            [self.cluster_to_label_.get(int(cluster), self.anomaly_label) for cluster in cluster_labels],
            dtype=int,
        )

        if self.distance_threshold_ is not None:
            status_labels[min_distances > self.distance_threshold_] = self.anomaly_label

        return status_labels

    def predict_clusters(self, X):
        self._check_is_fitted()
        features = extract_waveform_features(X)
        scaled_features = self.scaler_.transform(features)
        cluster_labels = self.kmeans_.predict(scaled_features)
        distances = self.kmeans_.transform(scaled_features)
        min_distances = np.min(distances, axis=1)
        return cluster_labels, min_distances

    def transform(self, X):
        self._check_is_fitted()
        features = extract_waveform_features(X)
        scaled_features = self.scaler_.transform(features)
        return self.kmeans_.transform(scaled_features)

    def _map_clusters_to_labels(self, cluster_labels, y):
        mapping = {}
        for cluster in np.unique(cluster_labels):
            cluster_y = y[cluster_labels == cluster]
            labels, counts = np.unique(cluster_y, return_counts=True)
            mapping[int(cluster)] = int(labels[np.argmax(counts)])
        return mapping

    def _check_is_fitted(self):
        if not hasattr(self, "kmeans_") or not hasattr(self, "scaler_"):
            raise RuntimeError("KMeansHealthClassifier is not fitted yet.")


def extract_waveform_features(X):
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X.reshape(1, -1)
    if X.ndim == 3:
        X = X[:, 1, :]
    if X.ndim != 2:
        raise ValueError(f"Expected waveform array with 1, 2 or 3 dimensions, got {X.shape}.")

    mean = X.mean(axis=1)
    std = X.std(axis=1)
    maximum = X.max(axis=1)
    minimum = X.min(axis=1)
    peak_to_peak = maximum - minimum

    return np.column_stack([mean, std, maximum, minimum, peak_to_peak])
