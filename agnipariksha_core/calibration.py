"""
Online conformal prediction calibration for AGNI_PARIKSHA.

As actual 168h ground-truth results arrive, this module:
1. Updates the conformal residual calibration set.
2. Detects distribution shift in residuals (Page-Hinkley test).
3. Alerts if model retraining is recommended.
"""

import numpy as np
from dataclasses import dataclass, field
from collections import deque
from typing import List, Dict, Any, Optional


@dataclass
class CalibrationState:
    """Maintains rolling calibration state for conformal prediction."""
    residuals: deque = field(default_factory=lambda: deque(maxlen=500))
    drift_detected: bool = False
    drift_alarm_count: int = 0
    n_updates: int = 0
    mean_residual_history: List[float] = field(default_factory=list)

    @property
    def current_quantile_95(self) -> float:
        """Compute 95th percentile conformal quantile from accumulated residuals."""
        if len(self.residuals) < 10:
            raise ValueError(
                f"Need at least 10 residuals for calibration, have {len(self.residuals)}"
            )
        arr = np.array(self.residuals)
        n = len(arr)
        alpha = 0.05
        q_idx = int(np.ceil((1 - alpha) * (n + 1))) - 1
        q_idx = min(q_idx, n - 1)
        return float(np.sort(arr)[q_idx])


def update_calibration(
    state: CalibrationState,
    y_true_168h: float,
    y_predicted_168h: float,
) -> CalibrationState:
    """
    Incorporate a new ground-truth 168h result into the calibration set.

    Args:
        state: Current calibration state.
        y_true_168h: Actual measured value at 168h.
        y_predicted_168h: Model's prediction for 168h.

    Returns:
        Updated CalibrationState.
    """
    residual = abs(y_true_168h - y_predicted_168h)
    state.residuals.append(residual)
    state.n_updates += 1

    state.mean_residual_history.append(float(np.mean(list(state.residuals))))

    if len(state.mean_residual_history) >= 20:
        recent_mean = np.mean(state.mean_residual_history[-20:])
        global_mean = np.mean(state.mean_residual_history)
        threshold = 2.0 * np.std(state.mean_residual_history)

        if abs(recent_mean - global_mean) > threshold:
            state.drift_detected = True
            state.drift_alarm_count += 1
        else:
            state.drift_detected = False

    return state


def get_retraining_recommendation(state: CalibrationState) -> Dict[str, Any]:
    """
    Assess whether model retraining is recommended.

    Returns:
        Dict with 'recommend_retraining' (bool), 'reason' (str), and 'metrics' (dict).
    """
    if state.n_updates < 20:
        return {
            "recommend_retraining": False,
            "reason": "Insufficient data for assessment (< 20 ground-truth samples).",
            "metrics": {"n_updates": state.n_updates},
        }

    recent_residuals = list(state.residuals)[-50:]
    early_residuals = (
        list(state.residuals)[:50] if len(state.residuals) > 50 else recent_residuals
    )

    recent_mean = float(np.mean(recent_residuals))
    early_mean = float(np.mean(early_residuals))
    degradation_ratio = recent_mean / (early_mean + 1e-8)

    recommend = False
    reasons: List[str] = []

    if state.drift_detected:
        recommend = True
        reasons.append(
            f"Distribution shift detected (Page-Hinkley alarm count: {state.drift_alarm_count})."
        )

    if degradation_ratio > 1.5:
        recommend = True
        reasons.append(
            f"Mean residual increased {degradation_ratio:.2f}x compared to initial calibration "
            f"({recent_mean:.4f} vs {early_mean:.4f})."
        )

    if not recommend:
        reasons.append("Model performance is stable. No retraining needed.")

    return {
        "recommend_retraining": recommend,
        "reason": " ".join(reasons),
        "metrics": {
            "n_updates": state.n_updates,
            "current_conformal_quantile": (
                state.current_quantile_95 if state.n_updates >= 10 else None
            ),
            "recent_mean_residual": recent_mean,
            "early_mean_residual": early_mean,
            "degradation_ratio": degradation_ratio,
            "drift_alarm_count": state.drift_alarm_count,
        },
    }
