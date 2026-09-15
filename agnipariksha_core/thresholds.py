"""
Device-family-specific specification limits for AGNI_PARIKSHA triage.
Each family maps to:
  - parametric_name: the primary parametric being screened
  - unit: measurement unit
  - spec_limit_upper: upper spec limit
  - spec_limit_lower: lower spec limit (if two-sided)
  - source: JEDEC/MIL-STD/ISRO spec reference
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class DeviceFamilySpec:
    family_id: str
    family_name: str
    parametric_name: str
    unit: str
    spec_limit_upper: float
    spec_limit_lower: Optional[float]
    source: str


DEVICE_FAMILY_SPECS: Dict[str, DeviceFamilySpec] = {
    "digital_ic_74hc": DeviceFamilySpec(
        family_id="digital_ic_74hc",
        family_name="Digital ICs (74HC/54HC)",
        parametric_name="IDDQ_quiescent_leakage_uA",
        unit="µA",
        spec_limit_upper=45.0,
        spec_limit_lower=None,
        source="MIL-STD-883 Method 1015 / AEC-Q100",
    ),
    "mixed_signal_adc_dac_pll": DeviceFamilySpec(
        family_id="mixed_signal_adc_dac_pll",
        family_name="Mixed-Signal ICs (ADC/DAC/PLL)",
        parametric_name="ICC_active_supply_drift_uA",
        unit="µA",
        spec_limit_upper=80.0,
        spec_limit_lower=None,
        source="MIL-STD-883 Method 1015",
    ),
    "mems_gyroscope": DeviceFamilySpec(
        family_id="mems_gyroscope",
        family_name="MEMS Gyroscopes (IMU/Angular Rate)",
        parametric_name="ZRO_bias_offset_drift_deg_per_hr",
        unit="deg/hr",
        spec_limit_upper=10.0,
        spec_limit_lower=-10.0,
        source="JEDEC JESD211",
    ),
    "image_sensor_cmos_ccd": DeviceFamilySpec(
        family_id="image_sensor_cmos_ccd",
        family_name="Image Sensors (CMOS/CCD)",
        parametric_name="dark_current_density_nA_per_cm2",
        unit="nA/cm²",
        spec_limit_upper=50.0,
        spec_limit_lower=None,
        source="ISRO SAC Internal Spec",
    ),
    "voltage_reference_bandgap": DeviceFamilySpec(
        family_id="voltage_reference_bandgap",
        family_name="Precision Voltage References (Bandgap)",
        parametric_name="VREF_output_drift_mV",
        unit="mV",
        spec_limit_upper=5.0,
        spec_limit_lower=-5.0,
        source="JEDEC JESD25",
    ),
}


def get_spec(family_id: str) -> DeviceFamilySpec:
    """Retrieve the specification limit for a given device family."""
    if family_id not in DEVICE_FAMILY_SPECS:
        raise ValueError(
            f"Unknown device family '{family_id}'. "
            f"Valid families: {list(DEVICE_FAMILY_SPECS.keys())}"
        )
    return DEVICE_FAMILY_SPECS[family_id]


def triage(y_hat: float, y_upper_95: float, family_id: str) -> str:
    """
    3-tier decision triage.
    Returns: 'GREEN', 'YELLOW', or 'RED'
    Uses device-family-specific spec limit from thresholds.py.
    """
    spec = get_spec(family_id)
    limit = spec.spec_limit_upper

    if y_hat >= limit:
        return "RED"
    elif y_upper_95 >= limit:
        return "YELLOW"
    else:
        return "GREEN"
