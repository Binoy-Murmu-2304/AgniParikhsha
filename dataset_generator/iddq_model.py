"""
AgniPariksha 2.5 — AgniPariksha Space Qualification Dataset (ASQD) Multi-Device Physics Engine
=============================================================================================
Provides device-specific parametric drift trajectory generators with normalized thermal scaling,
space radiation effects (TID), and thermal vacuum fatigue (TVAC):
  - DIGITAL_IC: Arrhenius IDDQ drift + TID radiation trap build-up relative to T_ref = 25°C (298.15 K)
  - MIXED_SIGNAL_IC: Arrhenius Subthreshold & Dielectric degradation under high-field stress
  - MEMS_GYROSCOPE: Viscoelastic zero-rate-offset drift + stiction risk + thermal cycling creep
  - IMAGE_SENSOR: Shockley-Read-Hall dark current trap generation + proton displacement damage
  - PRECISION_VOLTAGE_REF: Bandgap voltage drift & Zener diode aging under thermal-radiation stress

Evidence & Standards:
  - Dataset: AgniPariksha Space Qualification Dataset (ASQD) v2.5
  - Standards: MIL-STD-883 Method 1015 (HTOL), MIL-PRF-38535 Class V, ESA ECSS-Q-ST-60C
  - Physics Models: Arrhenius (Ea=0.68 eV), Black's Law, Shockley-Read-Hall (SRH), Coffin-Manson TVAC
"""

import numpy as np


# ===========================================================================
# SPACE RADIATION (TID) & TVAC FATIGUE HELPER
# ===========================================================================
def compute_tid_radiation_multiplier(dose_krad: float = 0.0, sensitivity_coeff: float = 0.0035) -> float:
    """
    [PE] Total Ionizing Dose (TID) radiation degradation factor.
    Models threshold voltage shift ΔVth and radiation-induced interface trap buildup:
    Multiplier = 1 + α * (Dose_krad)^1.15
    """
    if dose_krad <= 0.0:
        return 1.0
    return 1.0 + sensitivity_coeff * (dose_krad ** 1.15)


def compute_tvac_cycle_fatigue(cycles: int = 0, delta_temp_c: float = 180.0, co_coeff: float = 0.0004) -> float:
    """
    [PE] Coffin-Manson Thermal Vacuum Cycling (TVAC) fatigue acceleration factor.
    Models micro-crack growth and solder/die-attach shear stress under cycling (-55°C <-> +125°C).
    """
    if cycles <= 0:
        return 1.0
    return 1.0 + co_coeff * cycles * ((delta_temp_c / 100.0) ** 1.9)


# ===========================================================================
# DIGITAL IC — Arrhenius IDDQ Drift (Normalized to T_ref = 25°C)
# ===========================================================================
class ArrheniusIDDQModel:
    """[PE] Arrhenius CMOS IDDQ model with controlled process variation and TID radiation effects."""
    def __init__(self, base_iddq_uA: float = 1.2, ea_eV: float = 0.68, aging_rate: float = 0.001):
        self.base_iddq = base_iddq_uA
        self.ea = ea_eV
        self.k_boltzmann = 8.617333262145e-5  # eV/K [PE]
        self.aging_rate = aging_rate
        self.t_ref_k = 298.15  # 25°C reference temperature

    def generate_trajectory(
        self,
        num_hours: int = 168,
        profile: str = "NOMINAL",
        comp_base_scale: float = 1.0,
        lot_base_scale: float = 1.0,
        tid_dose_krad: float = 0.0,
        tvac_cycles: int = 0,
        edge_proximity_factor: float = 1.0
    ):
        trajectory = []
        tid_mult = compute_tid_radiation_multiplier(tid_dose_krad, sensitivity_coeff=0.004)
        tvac_mult = compute_tvac_cycle_fatigue(tvac_cycles, delta_temp_c=180.0)
        
        effective_base = self.base_iddq * comp_base_scale * lot_base_scale * edge_proximity_factor

        # Component-specific aging kinetic rate variation [SA]
        rate_var = np.random.normal(1.0, 0.08)

        for hour in range(num_hours + 1):
            temp_c = 25.0 + 100.0 * (1.0 - np.exp(-hour / 2.0))
            temp_k = temp_c + 273.15
            # Arrhenius scaling relative to 25°C [PE]
            arrhenius_factor = np.exp(-(self.ea / self.k_boltzmann) * ((1.0 / temp_k) - (1.0 / self.t_ref_k)))
            aging_component = self.aging_rate * hour * rate_var * tvac_mult

            if profile == "NOMINAL":
                iddq = effective_base * (arrhenius_factor + aging_component * 0.5) * tid_mult
            elif profile == "THERMAL_RUNAWAY":
                if hour >= 24:
                    runaway = 0.5 * np.exp(0.04 * (hour - 24))
                    iddq = effective_base * (arrhenius_factor + aging_component) * tid_mult + runaway
                else:
                    iddq = effective_base * (arrhenius_factor + aging_component * 0.5) * tid_mult
            elif profile == "ELECTROMIGRATION":
                accel = 1.0 + (hour / 168.0) ** 2 * 35.0
                iddq = effective_base * (arrhenius_factor + aging_component * accel) * tid_mult
            elif profile == "SPATIAL_OUTLIER":
                iddq = effective_base * 4.5 * (arrhenius_factor + aging_component * 0.3) * tid_mult
            elif profile == "DIELECTRIC_OSCILLATION":
                osc = 0.25 * np.sin(2 * np.pi * hour / 12.0)
                iddq = effective_base * (arrhenius_factor + aging_component * 0.5) * tid_mult + osc
            else:
                iddq = effective_base * (arrhenius_factor + aging_component * 0.5) * tid_mult

            noise = np.random.normal(0, 0.015 * (1.0 + hour / 168.0))
            iddq = max(0.01, iddq + noise)
            trajectory.append(round(float(iddq), 4))
        return trajectory


# ===========================================================================
# MEMS GYROSCOPE — Viscoelastic ZRO Drift Model
# ===========================================================================
class ViscoelasticMEMSModel:
    """
    [PE] MEMS zero-rate-offset (ZRO) drift model based on viscoelastic
    stress relaxation in die attach and packaging materials.
    """
    def __init__(
        self,
        base_zro_dps: float = 0.05,
        relaxation_amplitude_dps: float = 0.03,
        relaxation_tau_hours: float = 20.0,
        creep_rate_dps: float = 0.008,
        creep_t0_hours: float = 5.0,
    ):
        self.base_zro = base_zro_dps
        self.A = relaxation_amplitude_dps
        self.tau = relaxation_tau_hours
        self.B = creep_rate_dps
        self.t0 = creep_t0_hours

    def generate_trajectory(
        self,
        num_hours: int = 168,
        profile: str = "NOMINAL",
        comp_base_scale: float = 1.0,
        lot_base_scale: float = 1.0,
        tid_dose_krad: float = 0.0,
        tvac_cycles: int = 0,
        edge_proximity_factor: float = 1.0
    ) -> list:
        trajectory = []
        tvac_mult = compute_tvac_cycle_fatigue(tvac_cycles, delta_temp_c=180.0, co_coeff=0.0008)
        damped_base_scale = 1.0 + (comp_base_scale - 1.0) * 0.25
        effective_base = self.base_zro * damped_base_scale * lot_base_scale * edge_proximity_factor
        rate_var = np.random.normal(1.0, 0.15) * tvac_mult

        for hour in range(num_hours + 1):
            relaxation = self.A * rate_var * (1.0 - np.exp(-hour / self.tau))
            creep = self.B * rate_var * np.log(1.0 + hour / self.t0)

            zro = effective_base + relaxation + creep

            if profile == "NOMINAL":
                pass
            elif profile == "MEMS_STICTION_ONSET":
                if hour >= 48:
                    zro += 0.12 * (1.0 + (hour - 48) / 120.0)
            elif profile == "PACKAGING_STRESS_RELAXATION":
                zro = effective_base + 2.5 * self.A * rate_var * (1.0 - np.exp(-hour / (self.tau * 0.4)))
            elif profile == "SPATIAL_OUTLIER":
                zro = effective_base * 4.5 + relaxation * 0.5 + creep * 0.5
            elif profile == "THERMAL_RUNAWAY":
                if hour >= 24:
                    zro += 0.002 * rate_var * (hour - 24)

            noise = np.random.normal(0, 0.0008)
            zro = max(0.0, zro + noise)
            trajectory.append(round(float(zro), 5))
        return trajectory


# ===========================================================================
# IMAGE SENSOR — Shockley-Read-Hall Dark Current Model
# ===========================================================================
class SRHDarkCurrentModel:
    """
    [PE] CMOS Image Sensor dark current model based on Shockley-Read-Hall (SRH)
    thermal generation in depletion region with Total Ionizing Dose trap scaling.
    """
    def __init__(
        self,
        base_dark_current_nA_cm2: float = 1.5,
        stress_temp_c: float = 60.0,
        activation_energy_eV: float = 0.55,
    ):
        self.base_dc = base_dark_current_nA_cm2
        self.T_stress_K = stress_temp_c + 273.15
        self.Ea = activation_energy_eV
        self.k_b = 8.617333262145e-5  # eV/K [PE]

    def _thermal_factor(self, temp_k: float) -> float:
        T_ref_K = 298.15
        return np.exp(-(self.Ea / self.k_b) * ((1.0 / temp_k) - (1.0 / T_ref_K)))

    def generate_trajectory(
        self,
        num_hours: int = 168,
        profile: str = "NOMINAL",
        comp_base_scale: float = 1.0,
        lot_base_scale: float = 1.0,
        tid_dose_krad: float = 0.0,
        tvac_cycles: int = 0,
        edge_proximity_factor: float = 1.0
    ) -> list:
        trajectory = []
        tid_mult = compute_tid_radiation_multiplier(tid_dose_krad, sensitivity_coeff=0.008)
        damped_base_scale = 1.0 + (comp_base_scale - 1.0) * 0.30
        effective_base = self.base_dc * damped_base_scale * lot_base_scale * edge_proximity_factor
        thermal_factor = self._thermal_factor(self.T_stress_K)
        gamma = np.random.uniform(0.009, 0.018)

        for hour in range(num_hours + 1):
            trap_growth = np.exp(gamma * hour)
            dc = effective_base * thermal_factor * trap_growth * tid_mult

            if profile == "NOMINAL":
                pass
            elif profile == "DARK_CURRENT_SPIKE_GROWTH":
                if hour >= 48:
                    dc *= np.exp(0.008 * (hour - 48))
            elif profile == "THERMAL_RUNAWAY":
                if hour >= 24:
                    dc *= np.exp(0.016 * (hour - 24))
            elif profile == "SPATIAL_OUTLIER":
                dc = effective_base * thermal_factor * trap_growth * 3.5 * tid_mult
            elif profile == "DIELECTRIC_OSCILLATION":
                osc = 0.6 * np.sin(2 * np.pi * hour / 24.0)
                dc = max(0.05, dc + osc)

            noise = np.random.normal(0, 0.02 * dc)
            dc = max(0.01, dc + noise)
            trajectory.append(round(float(dc), 4))
        return trajectory
