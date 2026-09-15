"""
Dataset provenance tracking for AGNI_PARIKSHA.

Generates a machine-readable provenance record for every trained model,
documenting data source, generation method, and validation split.
"""

import hashlib
import json
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any


@dataclass
class DataProvenance:
    """Tracks the origin and composition of a training dataset."""
    dataset_id: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    source_type: str = ""  # "synthetic_physics", "isro_htol_datalog", "jedec_public", "mixed"
    source_description: str = ""
    n_samples_total: int = 0
    n_samples_train: int = 0
    n_samples_test: int = 0
    n_defective: int = 0
    n_pass: int = 0
    device_families: List[str] = field(default_factory=list)
    noise_model: str = ""  # e.g., "gaussian_σ=0.15µA + arrhenius_temp_scatter"
    arrhenius_ea_eV: float = 0.0  # Activation energy used in synthetic generation
    temperature_K: float = 398.15  # 125°C in Kelvin
    validation_method: str = ""  # "holdout_80_20", "5fold_cv", "leave_one_lot_out"
    checksum_sha256: str = ""

    def compute_checksum(self, feature_matrix_bytes: bytes) -> str:
        """Compute SHA-256 checksum of the raw feature matrix for audit trail."""
        self.checksum_sha256 = hashlib.sha256(feature_matrix_bytes).hexdigest()
        return self.checksum_sha256

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)

    def summary_statement(self) -> str:
        """Generate a human-readable provenance statement for reports and certificates."""
        return (
            f"Dataset '{self.dataset_id}' created {self.created_at}. "
            f"Source: {self.source_type} — {self.source_description}. "
            f"Total samples: {self.n_samples_total} "
            f"(train: {self.n_samples_train}, test: {self.n_samples_test}). "
            f"Defective: {self.n_defective}, Pass: {self.n_pass}. "
            f"Device families: {', '.join(self.device_families)}. "
            f"Noise model: {self.noise_model}. "
            f"Arrhenius Ea: {self.arrhenius_ea_eV} eV at {self.temperature_K} K. "
            f"Validation: {self.validation_method}. "
            f"SHA-256: {self.checksum_sha256[:16]}..."
        )
