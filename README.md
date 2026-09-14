# 🔥 AGNI_PARIKSHA (अग्नि परीक्षा) 3.0 — Physics-Informed Semiconductor Reliability & Conformal Prognostic Platform

> **ISRO Space Applications Centre (SAC) Submission** | **Problem Statement #26170**  
> *Physics-Informed Semiconductor Qualification Screening, Joint Multi-Parametric Anomaly Detection & Conformal Degradation Forecasting Engine*

[![Python Version](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.0-black.svg)](https://nextjs.org)
[![ISRO PS Compliance](https://img.shields.io/badge/ISRO%20PS-%2326170-orange.svg)]()
[![Conformal Coverage](https://img.shields.io/badge/Conformal%20Coverage-95%25%20CI-brightgreen.svg)]()

---

## 📖 Executive Summary & Core Philosophy

**AGNI_PARIKSHA (Trial by Fire)** is an aerospace-grade reliability and prognostic platform designed for early screening and degradation forecasting during semiconductor qualification and high-temperature burn-in testing (MIL-STD-883 Method 1015, AEC-Q100).

Conventional qualification procedures require 168+ hours of thermal stress testing at 125°C, consuming significant energy and chamber capacity. **AGNI_PARIKSHA** replaces static threshold limits with a **Multi-Layer Staged Prognostic Engine**:

* **Module A (Joint Multi-Parametric Screener)**: Combines Robust Median Absolute Deviation (MAD) Z-score screening with **Mahalanobis Distance** and **Isolation Forest** vector anomaly detection to catch subtle multi-variable drift.
* **Module B (Conformal Prognostic Engine)**: Employs physics-informed kinetic features ($dI/dt$, $d^2I/dt^2$, Arrhenius activation energy $E_a$) alongside non-parametric **95% Conformal Prediction Bounds** (`predicted_168h_lower_95`, `predicted_168h_upper_95`) to quantify forecast uncertainty.
* **Decision Fusion & Safety Interlock**: Synthesizes Module A & B outputs into 3 risk tiers: **GREEN** (early pass), **YELLOW** (extended testing / operator review), and **RED** (early reject). If a component's 95% upper bound breaches safety thresholds, it is automatically escalated.
* **Multi-Model Benchmark Matrix**: Evaluates and compares XGBoost, LightGBM/Random Forest, Ridge Linear Physics Baseline, and Physics-Informed Neural Networks (PINN MLP).
* **ISRO QA Qualification Certificate Generator**: Generates downloadable MIL-STD-883 Spaceflight Component Qualification Certificates with SHAP feature attributions and QA inspector sign-off blocks.

---

## 🏗️ System Architecture

```text
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                      AGNI_PARIKSHA 3.0 SYSTEM ARCHITECTURE                  │
 └─────────────────────────────────────────────────────────────────────────────┘

    [ATE Hardware Telemetry / Data Ingestion]
                     │
                     ▼
    [AgniPariksha SDK Data Integrity Validator] ──▶ (Detect SMU / Channel Faults)
                     │
                     ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ STAGE A (0h + 24h): Population & Multi-Parametric Screening               │
  │ • Robust Median / MAD Z-Score Screener (Z >= 3.5)                         │
  │ • Mahalanobis Distance & Isolation Forest Vector Anomaly Screener         │
  └─────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ STAGE B (0h + 24h): Physics-Informed 168h Forecast & Conformal Engine     │
  │ • Kinetic Velocity & Acceleration Extraction (dI/dt, d²I/dt²)            │
  │ • 95% Conformal Prediction Intervals [Lower_95 , Upper_95]                │
  │ • Multi-Model Benchmark (XGBoost vs LightGBM vs PINN Neural Net)          │
  └─────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                                        ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │ 3-TIER CONFORMAL RISK FUSION & SAFETY INTERLOCK                           │
  │  🟢 GREEN (Auto-Pass at 24h)   -> Exit Chamber Early (Save Testing Hours) │
  │  🟡 YELLOW (Extend to 168h)    -> Upper 95% CI Breach / Marginal Drift     │
  │  🔴 RED (Early Reject at 24h)  -> Malfunctioning / Latent Defect Spikes   │
  └─────────────────────────────────────┬─────────────────────────────────────┘
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             ▼                                                     ▼
    [Game-Theoretic SHAP Engine]                       [FastAPI REST & WS Server]
    (Physics Mechanism Attribution)                    (Port 8000)
             │                                                     │
             └──────────────────────────┬──────────────────────────┘
                                        ▼
                           [Next.js Operator Dashboard]
                           (Port 3000 - Live Streaming UI & PDF Certs)
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites & Installation
Ensure **Python 3.11+** and **Node.js 18+** are installed.

```bash
# Clone the repository
git clone https://github.com/GRINDWUS/AGNI_PARIKSHA.git
cd AGNI_PARIKSHA

# Install Python dependencies
pip install -r requirements.txt

# Install AGNI_PARIKSHA SDK in editable mode
pip install -e .
```

### 2. Run the Unit Test Suite
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### 3. Launch FastAPI Backend Server
```bash
python server.py
```
*Interactive OpenAPI documentation: `http://127.0.0.1:8000/docs`*  
*Multi-Model Benchmark Endpoint: `http://127.0.0.1:8000/api/v2/model-comparison`*

### 4. Launch Next.js Operator Dashboard
```bash
cd dashboard
npm install
npm run dev
```
*Access the operator dashboard at: `http://localhost:3000`*

---

## 📄 Automated PDF Qualification Certificates

AGNI_PARIKSHA includes an automated PDF generator for ISRO MIL-STD-883 qualification certificates:

```bash
python generate_pdf.py
```
Outputs downloadable qualification certificates with complete SHAP attributions, conformal bounds, and sign-off blocks.
