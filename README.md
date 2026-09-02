# Glasgow Blatchford Bleeding Score

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Glasgow-Blatchford Score (GBS) for Upper GI Bleeding
Full implementation with pre-endoscopy risk stratification and 30-day mortality prediction.

The GBS identifies patients safe for outpatient management (score 0) vs those
requiring urgent intervention (score >= 6).

Score range: 0-23 points.

References:
  - Blatchford O, et al. A score to predict need for treatment for upper-
    gastrointestinal haemorrhage. Lancet 2000;356:1318-21.
  - Stanley AJ, et al. Lancet 2009;373:42-47 (validation & mortality data).

Author: Dr. Abu Suraih Sakhri
License: MIT

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`calculate_gbs()`**: Calculate Glasgow-Blatchford Score for upper GI bleed risk stratification.

Parameters:
    bun_mmol_l: Blood urea nitrogen in mmol/L
    hemoglobin_g_dl: Hemoglobin in g/dL
    sex: 'male' or 'female' (affects hemoglobin scoring thresholds)
    sbp_mmhg: Systolic blood pressure in mmHg
    heart_rate: Heart rate in beats per minute
    melena: Presence of melena (black tarry stool)
    syncope: History of syncope at presentation
    hepatic_disease: Known liver disease history
    cardiac_failure: Known cardiac failure history

Returns:
    Dict with total_score, component breakdown, risk category, recommendation,
    and estimated 30-day mortality.
- **`calculate_gbs_from_dict()`**: Calculate GBS from a dictionary of parameters (for batch/CLI use).
- **`process_batch()`**: Process a CSV file of patients and write GBS results.
- **`main()`** — calculates and validates main parameters.

---

## 📐 Mathematical Formulation & Logic

```text
  Calculate Glasgow-Blatchford Score for upper GI bleed risk stratification.
  risk = "Very Low"
  risk = "Low"
  risk = "Moderate"
  risk = "High"
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --input data.csv
```

### Parameter Reference
- `--interactive`: Launch guided terminal interactive wizard.
- `--input <path>`: Evaluate input from JSON or CSV specification.
- `--json`: Output deterministic structured results in JSON format.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `Patient_ID` | Parameter / observation metric | Required |
| `v1` | Parameter / observation metric | Required |
| `v2` | Parameter / observation metric | Required |
| `v3` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t glasgow-blatchford-bleeding-score .
docker run -p 8000:8000 glasgow-blatchford-bleeding-score
```
