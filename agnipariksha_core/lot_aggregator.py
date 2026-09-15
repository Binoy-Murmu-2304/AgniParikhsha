"""
Lot-level aggregation for AGNI_PARIKSHA screening decisions.

MIL-STD-883 Method 1015 operates at the lot level: a sample of parts
is tested, and the lot is accepted/rejected based on the sample.
This module aggregates part-level predictions into lot-level decisions.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any


class LotDecision(str, Enum):
    LOT_PASS = "LOT_PASS"
    LOT_EXTENDED = "LOT_EXTENDED"
    LOT_REJECT = "LOT_REJECT"


@dataclass
class LotScreeningResult:
    lot_id: str
    family_id: str
    n_parts_tested: int
    n_parts_in_lot: int
    n_green: int
    n_yellow: int
    n_red: int
    worst_part_prediction: float
    worst_part_upper_bound: float
    lot_decision: LotDecision
    lot_confidence: str  # "HIGH", "MEDIUM", "LOW"


def aggregate_lot_decisions(
    part_results: List[Dict[str, Any]],
    lot_id: str,
    family_id: str,
    n_parts_in_lot: int,
    reject_lot_if_any_red: bool = True,
    extend_lot_if_any_yellow: bool = True,
) -> LotScreeningResult:
    """
    Aggregate part-level triage results into a lot-level decision.

    Decision logic:
    - LOT_REJECT:   Any single part is RED, OR >= 20% of parts are YELLOW.
    - LOT_EXTENDED: Any part is YELLOW (but no RED, and < 20% YELLOW).
    - LOT_PASS:     All parts are GREEN.

    Args:
        part_results: List of dicts with keys 'triage', 'y_hat', 'y_upper_95'.
        lot_id: Unique lot identifier.
        family_id: Device family key.
        n_parts_in_lot: Total parts in the lot (including untested).
        reject_lot_if_any_red: If True, any RED part rejects the lot.
        extend_lot_if_any_yellow: If True, any YELLOW part extends the lot.

    Returns:
        LotScreeningResult with aggregated decision.
    """
    df = pd.DataFrame(part_results)

    n_green = int((df["triage"] == "GREEN").sum()) if "triage" in df.columns else 0
    n_yellow = int((df["triage"] == "YELLOW").sum()) if "triage" in df.columns else 0
    n_red = int((df["triage"] == "RED").sum()) if "triage" in df.columns else 0
    n_tested = len(df)

    worst_y_hat = float(df["y_hat"].max()) if "y_hat" in df.columns and len(df) > 0 else 0.0
    worst_upper = float(df["y_upper_95"].max()) if "y_upper_95" in df.columns and len(df) > 0 else 0.0

    if reject_lot_if_any_red and n_red > 0:
        decision = LotDecision.LOT_REJECT
    elif n_yellow > 0 and (n_yellow / n_tested) >= 0.20:
        decision = LotDecision.LOT_REJECT
    elif extend_lot_if_any_yellow and n_yellow > 0:
        decision = LotDecision.LOT_EXTENDED
    else:
        decision = LotDecision.LOT_PASS

    sample_fraction = n_tested / max(1, n_parts_in_lot)
    if sample_fraction >= 0.20:
        confidence = "HIGH"
    elif sample_fraction >= 0.10:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    return LotScreeningResult(
        lot_id=lot_id,
        family_id=family_id,
        n_parts_tested=n_tested,
        n_parts_in_lot=n_parts_in_lot,
        n_green=n_green,
        n_yellow=n_yellow,
        n_red=n_red,
        worst_part_prediction=worst_y_hat,
        worst_part_upper_bound=worst_upper,
        lot_decision=decision,
        lot_confidence=confidence,
    )
