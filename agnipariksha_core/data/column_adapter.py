"""
AgniPariksha — Column Name Adapter
=================================
Single source of truth for mapping between canonical and legacy column names.

Canonical names: value_0h, value_24h, value_96h, value_168h_actual
Legacy names:    iddq_0h,  iddq_24h,  iddq_96h,  iddq_168h_actual

All modules should use to_canonical() at ingestion and to_legacy() only when
interfacing with legacy endpoints or display layers.
"""

import pandas as pd
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Bidirectional mapping: canonical ↔ legacy
CANONICAL_TO_LEGACY: Dict[str, str] = {
    "value_0h": "iddq_0h",
    "value_24h": "iddq_24h",
    "value_96h": "iddq_96h",
    "value_168h": "iddq_168h",
    "value_168h_actual": "iddq_168h_actual",
}

LEGACY_TO_CANONICAL: Dict[str, str] = {v: k for k, v in CANONICAL_TO_LEGACY.items()}


def to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    """Rename legacy iddq_* columns to canonical value_* names.
    
    If canonical columns already exist, no renaming is performed.
    If neither canonical nor legacy columns exist, the DataFrame is returned unchanged.
    """
    rename_map = {}
    for legacy_name, canonical_name in LEGACY_TO_CANONICAL.items():
        if legacy_name in df.columns and canonical_name not in df.columns:
            rename_map[legacy_name] = canonical_name
    
    if rename_map:
        logger.debug("Column adapter: renaming %s to canonical format", list(rename_map.keys()))
        return df.rename(columns=rename_map)
    return df


def to_legacy(df: pd.DataFrame) -> pd.DataFrame:
    """Add legacy iddq_* alias columns alongside canonical value_* columns.
    
    Does NOT remove canonical columns — both formats coexist for backward compatibility.
    """
    for canonical_name, legacy_name in CANONICAL_TO_LEGACY.items():
        if canonical_name in df.columns and legacy_name not in df.columns:
            df[legacy_name] = df[canonical_name]
    return df


def ensure_both_formats(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure both canonical and legacy column names are present.
    
    Detects which format is present and adds the missing aliases.
    """
    # Check if we have canonical or legacy format
    has_canonical = "value_0h" in df.columns
    has_legacy = "iddq_0h" in df.columns
    
    if has_canonical and not has_legacy:
        return to_legacy(df)
    elif has_legacy and not has_canonical:
        # Add canonical columns
        for legacy_name, canonical_name in LEGACY_TO_CANONICAL.items():
            if legacy_name in df.columns and canonical_name not in df.columns:
                df[canonical_name] = df[legacy_name]
        return df
    # Both exist already or neither exists
    return df
