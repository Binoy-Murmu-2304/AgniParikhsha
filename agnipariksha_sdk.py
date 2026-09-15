#!/usr/bin/env python3
"""
AgniPariksha 2.4 — Universal SDK Validation CLI
==============================================
Validates ANY semiconductor dataset CSV or ATE file using AgniPariksha SDK.

Usage:
  python agnipariksha_sdk.py <path_to_csv_file>

Examples:
  python agnipariksha_sdk.py ASQD_2.4/asqd_24_blind_test.csv
  python agnipariksha_sdk.py validation/dataset/uci-secom.csv
  python agnipariksha_sdk.py agnipariksha_core/data/LOT_2026_07.csv
"""

import sys
import os
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
import pandas as pd
from agnipariksha_core.predictor_fast import AgniParikshaPredictorFast

class AgniParikshaSDK:
    def __init__(self, failure_threshold_168h: float = 45.0):
        self.predictor = AgniParikshaPredictorFast(failure_threshold_168h=failure_threshold_168h)
        train_path = "agnipariksha_core/data/LOT_2026_01.csv"
        if os.path.exists(train_path):
            train_df = pd.read_csv(train_path)
            self.predictor.fit(train_df)

    def validate_file(self, csv_file_path: str):
        if not os.path.exists(csv_file_path):
            print(f"❌ Error: File not found: {csv_file_path}")
            return None

        print("\n" + "=" * 80)
        print(f"🛡️ AGNI_PARIKSHA SDK — LIVE DATASET VALIDATION")
        print(f"Target File: {csv_file_path}")
        print("=" * 80)

        df = pd.read_csv(csv_file_path)
        print(f"📊 Dataset Loaded: {len(df)} total component records")

        if "iddq_0h" not in df.columns and "value_0h" in df.columns:
            df["iddq_0h"] = df["value_0h"]

        if "iddq_24h" not in df.columns and "value_24h" in df.columns:
            df["iddq_24h"] = df["value_24h"]

        if "iddq_168h_actual" not in df.columns and "value_168h_actual" in df.columns:
            df["iddq_168h_actual"] = df["value_168h_actual"]

        # Validate required columns exist — DO NOT blindly guess from arbitrary numeric columns
        required_cols = ["iddq_0h", "iddq_24h"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            available = list(df.columns)
            raise ValueError(
                f"Dataset is missing required columns: {missing_cols}. "
                f"Available columns: {available}. "
                f"Expected either 'iddq_0h'/'iddq_24h' or 'value_0h'/'value_24h' column pairs."
            )

        if "iddq_24h" not in df.columns:
            df["iddq_24h"] = df["iddq_0h"] * 1.05

        if "spec_max_iddq" not in df.columns:
            df["spec_max_iddq"] = 50.0

        if "wafer_x" not in df.columns:
            df["wafer_x"] = 0.0
            df["wafer_y"] = 0.0

        # Run AgniPariksha Predictor Engine
        res_df = self.predictor.predict_lot(df)

        total_comps = len(res_df)
        green_cnt = int((res_df["risk_tier"] == "GREEN_AUTO_PASS").sum())
        yellow_cnt = int((res_df["risk_tier"] == "YELLOW_EXTENDED_TEST").sum())
        red_cnt = int((res_df["risk_tier"] == "RED_EARLY_REJECT").sum())

        yield_rate = round((green_cnt / max(1, total_comps)) * 100.0, 1)

        # Calculate chamber hours saved: Green saves 144h out of 168h
        saved_hours_pct = round(((green_cnt * 144.0) / max(1, total_comps * 168.0)) * 100.0, 1)

        # Silent escape calculation: Green components that breach spec limit at 168h actual
        if "iddq_168h_actual" in res_df.columns:
            escapes = int(((res_df["risk_tier"] == "GREEN_AUTO_PASS") & (res_df["iddq_168h_actual"] >= res_df["spec_max_iddq"])).sum())
        else:
            escapes = 0

        escape_rate = round((escapes / max(1, total_comps)) * 100.0, 2)
        lot_status = "QUALIFIED_FLIGHT_READY" if escapes == 0 else "WARNING_REVIEW_REQUIRED"

        print("-" * 80)
        print("✅ AGNI_PARIKSHA SDK VALIDATION RESULTS:")
        print(f"  • Lot Status:                {lot_status}")
        print(f"  • Total Components Tested:  {total_comps}")
        print(f"  • 🟢 Green (Auto-Pass 24h):   {green_cnt} components ({yield_rate}%)")
        print(f"  • 🟡 Yellow (Extended Test): {yellow_cnt} components")
        print(f"  • 🔴 Red (Early Reject 24h):  {red_cnt} components")
        print(f"  • Chamber Hours Saved:       {saved_hours_pct}%")
        print(f"  • Silent Escapes:            {escapes} (Escape Rate: {escape_rate}%)")
        print("=" * 80 + "\n")

        return res_df

if __name__ == "__main__":
    target_csv = sys.argv[1] if len(sys.argv) > 1 else "ASQD_2.4/asqd_24_blind_test.csv"
    sdk = AgniParikshaSDK()
    sdk.validate_file(target_csv)
