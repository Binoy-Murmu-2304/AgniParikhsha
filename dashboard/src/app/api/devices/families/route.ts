import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    device_families: {
      digital_ic_74hc: { family_id: "digital_ic_74hc", family_name: "Digital ICs (74HC/54HC)", parametric_name: "IDDQ_quiescent_leakage_uA", unit: "µA", spec_limit_upper: 45.0, source: "MIL-STD-883", chamber_temp: 125.0, stress_voltage: 5.0 },
      mixed_signal_adc_dac_pll: { family_id: "mixed_signal_adc_dac_pll", family_name: "Mixed-Signal ICs (ADC/DAC/PLL)", parametric_name: "ICC_active_supply_drift_uA", unit: "µA", spec_limit_upper: 80.0, source: "MIL-STD-883", chamber_temp: 125.0, stress_voltage: 5.0 },
      mems_gyroscope: { family_id: "mems_gyroscope", family_name: "MEMS Gyroscopes (IMU/Angular Rate)", parametric_name: "ZRO_bias_offset_drift_deg_per_hr", unit: "deg/hr", spec_limit_upper: 10.0, source: "JEDEC JESD211", chamber_temp: 125.0, stress_voltage: 5.0 },
      image_sensor_cmos_ccd: { family_id: "image_sensor_cmos_ccd", family_name: "Image Sensors (CMOS/CCD)", parametric_name: "dark_current_density_nA_per_cm2", unit: "nA/cm²", spec_limit_upper: 50.0, source: "ISRO SAC Internal Spec", chamber_temp: 125.0, stress_voltage: 5.0 },
      voltage_reference_bandgap: { family_id: "voltage_reference_bandgap", family_name: "Precision Voltage References (Bandgap)", parametric_name: "VREF_output_drift_mV", unit: "mV", spec_limit_upper: 5.0, source: "JEDEC JESD25", chamber_temp: 125.0, stress_voltage: 5.0 },
    }
  });
}
