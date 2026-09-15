"""
K-Fold cross-validation for AGNI_PARIKSHA champion model.
Reports R², MAE, and Defect Recall with mean ± std across folds.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import RepeatedKFold
from sklearn.metrics import r2_score, mean_absolute_error, recall_score
import xgboost as xgb
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class CVReport:
    r2_mean: float
    r2_std: float
    mae_mean: float
    mae_std: float
    recall_mean: float
    recall_std: float
    n_folds: int
    n_repeats: int
    n_samples: int

    def __str__(self) -> str:
        return (
            f"=== AGNI_PARIKSHA Cross-Validation Report ===\n"
            f"Samples: {self.n_samples} | Folds: {self.n_folds}x{self.n_repeats}\n"
            f"R²:     {self.r2_mean:.4f} ± {self.r2_std:.4f}\n"
            f"MAE:    {self.mae_mean:.4f} ± {self.mae_std:.4f} µA\n"
            f"Recall: {self.recall_mean:.4f} ± {self.recall_std:.4f}\n"
            f"=============================================="
        )


def run_cross_validation(
    X: np.ndarray,
    y: np.ndarray,
    defect_labels: np.ndarray,
    xgb_params: Optional[Dict[str, Any]] = None,
    n_folds: int = 5,
    n_repeats: int = 3,
    random_state: int = 42,
) -> CVReport:
    """
    Run Repeated K-Fold CV on the AgniPariksha XGBoost champion.

    Args:
        X: Feature matrix (N x 33).
        y: Continuous target (168h predicted value).
        defect_labels: Binary labels (1 = defective, 0 = pass) for recall calc.
        xgb_params: Override XGBoost hyperparams. Defaults to champion config.
        n_folds: Number of folds per repeat.
        n_repeats: Number of repeats.
        random_state: Reproducibility seed.

    Returns:
        CVReport with mean ± std for R², MAE, and Defect Recall.
    """
    if xgb_params is None:
        xgb_params = {
            "n_estimators": 500,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": random_state,
            "objective": "reg:squarederror",
        }

    rkf = RepeatedKFold(
        n_splits=n_folds, n_repeats=n_repeats, random_state=random_state
    )

    r2_scores: List[float] = []
    mae_scores: List[float] = []
    recall_scores: List[float] = []

    for train_idx, test_idx in rkf.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        labels_test = defect_labels[test_idx]

        model = xgb.XGBRegressor(**xgb_params)
        model.fit(X_train, y_train, verbose=False)

        y_pred = model.predict(X_test)

        r2_scores.append(r2_score(y_test, y_pred))
        mae_scores.append(mean_absolute_error(y_test, y_pred))

        defect_pred = (y_pred >= 45.0).astype(int)
        if labels_test.sum() > 0:
            recall_scores.append(recall_score(labels_test, defect_pred))
        else:
            recall_scores.append(1.0)

    return CVReport(
        r2_mean=float(np.mean(r2_scores)),
        r2_std=float(np.std(r2_scores)),
        mae_mean=float(np.mean(mae_scores)),
        mae_std=float(np.std(mae_scores)),
        recall_mean=float(np.mean(recall_scores)),
        recall_std=float(np.std(recall_scores)),
        n_folds=n_folds,
        n_repeats=n_repeats,
        n_samples=len(X),
    )
