"""
AGNI_PARIKSHA 3.0 — Conformal Prediction Engine
===============================================
Computes non-parametric 95% prediction intervals (Conformal Prediction Bounds)
for 168h degradation forecasting under finite-sample distribution-free guarantees.

Equations:
  Residual: e_i = |y_i - y_hat_i|
  Conformal Quantile: q_alpha = Quantile_1-alpha(e_i * (1 + 1/N))
  Prediction Interval: [y_hat - q_alpha, y_hat + q_alpha]
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional


class ConformalPredictor:
    """Non-parametric Conformal Prediction Interval Engine."""

    def __init__(self, confidence_level: float = 0.95):
        """
        Args:
            confidence_level: Target coverage level (e.g. 0.95 for 95% prediction interval).
        """
        self.confidence_level = confidence_level
        self.alpha = 1.0 - confidence_level
        self.q_alpha = 1.96  # Default fallback standard error multiplier

    def calibrate(self, y_true: np.ndarray, y_pred: np.ndarray):
        """
        Calibrate prediction interval width on hold-out calibration dataset.
        """
        residuals = np.abs(y_true - y_pred)
        n = len(residuals)
        if n > 0:
            # Empirical quantile with finite sample correction
            quantile_idx = float(np.ceil((n + 1) * (1.0 - self.alpha)) / n)
            quantile_idx = min(1.0, max(0.0, quantile_idx))
            self.q_alpha = float(np.quantile(residuals, quantile_idx))
        else:
            self.q_alpha = 1.96

    def predict_interval(self, y_pred: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Compute lower bound, upper bound, and uncertainty span for predictions.
        
        Returns:
            Dict containing:
              - 'pred_lower_95': Lower bound array
              - 'pred_upper_95': Upper bound array
              - 'uncertainty_span': Bound difference (Upper - Lower)
        """
        y_pred = np.array(y_pred, dtype=float)
        lower_bounds = np.maximum(0.0, y_pred - self.q_alpha)
        upper_bounds = y_pred + self.q_alpha
        uncertainty_span = upper_bounds - lower_bounds

        return {
            "pred_lower_95": np.round(lower_bounds, 2),
            "pred_upper_95": np.round(upper_bounds, 2),
            "uncertainty_span": np.round(uncertainty_span, 2),
            "margin_of_error": float(np.round(self.q_alpha, 2))
        }
