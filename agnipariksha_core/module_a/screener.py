"""
AGNI_PARIKSHA 3.0 — Module A Dynamic Outlier & Multi-Parametric Screener
========================================================================
Implements population-level anomaly screening at 0h and 24h checkpoints prior to ML forecasting.

Screening Modes:
  1. Single-Parametric: Robust Z-Score using Median Absolute Deviation (MAD).
  2. Multi-Parametric: Mahalanobis Distance & Isolation Forest for correlated vector drift.

Equations:
  MAD = median(|X - median(X)|)
  Robust Z = 0.6745 * (X - median(X)) / MAD
  Mahalanobis D^2 = (X - μ)^T Σ^(-1) (X - μ)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sklearn.covariance import MinCovDet
from sklearn.ensemble import IsolationForest


class ModuleAScreener:
    """Dynamic anomaly screener supporting single & multi-parametric screening."""

    def __init__(self, z_threshold: float = 3.5, contamination: float = 0.05):
        """
        Args:
            z_threshold: Robust Z-score threshold for single-variable screening (default 3.5).
            contamination: Expected anomaly ratio for multi-parametric isolation forest (default 0.05).
        """
        self.z_threshold = z_threshold
        self.contamination = contamination

    @staticmethod
    def compute_robust_z(series: pd.Series) -> pd.Series:
        """Compute Robust Z-score for a pandas Series using MAD."""
        median = series.median()
        mad = (series - median).abs().median()
        if mad == 0 or np.isnan(mad):
            mad = 1e-9
        return 0.6745 * (series - median) / mad

    @staticmethod
    def compute_mahalanobis_distance(df_features: pd.DataFrame) -> np.ndarray:
        """
        Compute Robust Mahalanobis Distance for multi-parametric vectors
        using Minimum Covariance Determinant (MCD) estimator.
        """
        data = df_features.select_dtypes(include=[np.number]).dropna()
        if data.shape[0] < data.shape[1] + 2:
            cov = np.cov(data.values, rowvar=False)
            inv_cov = np.linalg.pinv(cov)
            mean = np.mean(data.values, axis=0)
            diff = data.values - mean
            md = np.sqrt(np.sum(diff @ inv_cov * diff, axis=1))
        else:
            try:
                mcd = MinCovDet(random_state=42).fit(data.values)
                md = np.sqrt(mcd.dist_)
            except Exception:
                mean = np.mean(data.values, axis=0)
                diff = data.values - mean
                cov = np.cov(data.values, rowvar=False)
                inv_cov = np.linalg.pinv(cov)
                md = np.sqrt(np.sum(diff @ inv_cov * diff, axis=1))

        result = pd.Series(md, index=data.index)
        return result.reindex(df_features.index, fill_value=0.0).values

    def screen_population(
        self,
        df: pd.DataFrame,
        value_col: str = "value_24h",
        profile_col: str = "failure_mode_gt",
        multi_param_cols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Screen a population (lot) of components at a specific test checkpoint.
        
        Returns:
          Dictionary containing anomaly counts, Z-scores, multi-parametric distances,
          and performance metrics.
        """
        values = df[value_col] if value_col in df.columns else df.iloc[:, 0]
        robust_z = self.compute_robust_z(values)
        is_flagged_single = robust_z.abs() > self.z_threshold

        mahalanobis_d = np.zeros(len(df))
        is_flagged_multi = pd.Series(False, index=df.index)

        if multi_param_cols and all(col in df.columns for col in multi_param_cols):
            feature_matrix = df[multi_param_cols]
            mahalanobis_d = self.compute_mahalanobis_distance(feature_matrix)

            iso = IsolationForest(contamination=self.contamination, random_state=42)
            iso_pred = iso.fit_predict(feature_matrix.fillna(0))
            is_flagged_multi = pd.Series(iso_pred == -1, index=df.index)

        is_flagged = is_flagged_single | is_flagged_multi

        metrics = {
            "total_components": len(df),
            "flagged_anomalies": int(is_flagged.sum()),
            "flagged_rate_pct": float(100.0 * is_flagged.sum() / len(df)),
            "robust_z_scores": robust_z,
            "mahalanobis_distances": pd.Series(mahalanobis_d, index=df.index),
            "is_flagged_single": is_flagged_single,
            "is_flagged_multi": is_flagged_multi,
            "is_flagged": is_flagged
        }

        if profile_col in df.columns:
            is_anomaly_gt = df[profile_col] != "NOMINAL"
            is_nominal_gt = df[profile_col] == "NOMINAL"

            tp = (is_flagged & is_anomaly_gt).sum()
            fp = (is_flagged & is_nominal_gt).sum()
            tn = (~is_flagged & is_nominal_gt).sum()
            fn = (~is_flagged & is_anomaly_gt).sum()

            ddr = float(100.0 * tp / (tp + fn)) if (tp + fn) > 0 else 100.0
            far = float(100.0 * fp / (fp + tn)) if (fp + tn) > 0 else 0.0

            metrics.update({
                "true_positives": int(tp),
                "false_positives": int(fp),
                "true_negatives": int(tn),
                "false_negatives": int(fn),
                "defect_detection_rate_pct": ddr,
                "false_alarm_rate_pct": far,
            })

        return metrics
