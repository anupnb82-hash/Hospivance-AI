"""Model definitions and fallback ensemble for Hospivance AI."""

import numpy as np

class SimpleDecisionTree:
    """Fast, lightweight regression tree implementation for fallback."""
    def __init__(self, max_depth=8, min_samples_split=10):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.tree = self._build_tree(X, y, depth=0)
        return self

    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int):
        n_samples, n_features = X.shape
        if depth >= self.max_depth or n_samples < self.min_samples_split or np.std(y) < 1e-4:
            return {"leaf": True, "value": float(np.mean(y))}

        feature_indices = np.random.choice(n_features, max(1, int(np.sqrt(n_features))), replace=False)
        best_feat, best_thresh, best_score = None, None, float("inf")

        for f_idx in feature_indices:
            values = np.unique(X[:, f_idx])
            if len(values) <= 1:
                continue
            thresholds = np.percentile(values, [20, 40, 50, 60, 80])
            for thresh in thresholds:
                left_mask = X[:, f_idx] <= thresh
                right_mask = ~left_mask
                if np.sum(left_mask) < 4 or np.sum(right_mask) < 4:
                    continue
                score = np.var(y[left_mask]) * np.sum(left_mask) + np.var(y[right_mask]) * np.sum(right_mask)
                if score < best_score:
                    best_score = score
                    best_feat = f_idx
                    best_thresh = thresh

        if best_feat is None:
            return {"leaf": True, "value": float(np.mean(y))}

        left_mask = X[:, best_feat] <= best_thresh
        left_subtree = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_subtree = self._build_tree(X[~left_mask], y[~left_mask], depth + 1)
        return {
            "leaf": False,
            "feature": best_feat,
            "threshold": best_thresh,
            "left": left_subtree,
            "right": right_subtree,
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([self._predict_row(row, self.tree) for row in X])

    def _predict_row(self, row: np.ndarray, node: dict) -> float:
        if node["leaf"]:
            return node["value"]
        if row[node["feature"]] <= node["threshold"]:
            return self._predict_row(row, node["left"])
        return self._predict_row(row, node["right"])


class FallbackRandomForest:
    """Ensemble of decision trees matching scikit-learn API."""
    def __init__(self, n_estimators=25, max_depth=8, min_samples_split=8):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees = []
        self.feature_importances_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        n_samples, n_features = X.shape
        self.trees = []
        for _ in range(self.n_estimators):
            boot_idx = np.random.choice(n_samples, n_samples, replace=True)
            tree = SimpleDecisionTree(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            tree.fit(X[boot_idx], y[boot_idx])
            self.trees.append(tree)

        self.feature_importances_ = np.ones(n_features) / n_features
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = np.array([tree.predict(X) for tree in self.trees])
        return np.mean(preds, axis=0)
