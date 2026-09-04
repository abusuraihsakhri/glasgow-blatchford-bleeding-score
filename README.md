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

Glasgow-Blatchford Score (GBS) for Upper GI Bleeding.
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
  Validates all clinical parameters for physiological plausibility.

  Parameters:
    - `bun_mmol_l`: Blood urea nitrogen in mmol/L (0-100)
    - `hemoglobin_g_dl`: Hemoglobin in g/dL (0-30)
    - `sex`: 'male' or 'female' (affects hemoglobin scoring thresholds)
    - `sbp_mmhg`: Systolic blood pressure in mmHg (0-300)
    - `heart_rate`: Heart rate in beats per minute (0-300)
    - `melena`: Presence of melena (black tarry stool)
    - `syncope`: History of syncope at presentation
    - `hepatic_disease`: Known liver disease history
    - `cardiac_failure`: Known cardiac failure history

  Returns:
    Dict with total_score, component breakdown, risk category, recommendation,
    and estimated 30-day mortality.

- **`calculate_gbs_from_dict()`**: Calculate GBS from a dictionary of parameters (for batch/CLI use).
- **`process_batch()`**: Process a CSV file of patients and write GBS results.

---

## 📐 Scoring Components

| Component | Criteria | Points |
|-----------|----------|--------|
| BUN (mmol/L) | >= 25.0 | 6 |
| | 10.0-24.9 | 4 |
| | 8.0-9.9 | 3 |
| | 6.5-7.9 | 2 |
| | < 6.5 | 0 |
| Hemoglobin (male, g/dL) | < 10.0 | 6 |
| | 10.0-11.9 | 3 |
| | 12.0-12.9 | 1 |
| | >= 13.0 | 0 |
| Hemoglobin (female, g/dL) | < 10.0 | 6 |
| | 10.0-11.9 | 1 |
| | >= 12.0 | 0 |
| SBP (mmHg) | < 90 | 3 |
| | 90-99 | 2 |
| | 100-109 | 1 |
| | >= 110 | 0 |
| Heart rate | >= 100 bpm | 1 |
| Melena | Present | 1 |
| Syncope | Present | 2 |
| Hepatic disease | Present | 2 |
| Cardiac failure | Present | 2 |

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
pip install -e .
# Or for development:
pip install -e ".[dev]"
```

### 1. Single Patient Calculation
```bash
python cli.py single --bun 10.0 --hemoglobin 9.0 --sex male --sbp 95 --melena
```

### 2. Batch Processing
```bash
python cli.py batch -i patients.csv -o results.csv
```

### 3. Audit Task Processing
```bash
python cli.py audit --task-id TASK-001 --primary-metric 12.0 --status-descriptor NOMINAL
```

### 4. Supervisory Chat
```bash
python cli.py chat "Explain the scoring criteria"
```

### 5. Verify Audit Trail
```bash
python cli.py verify-audit
```

### 6. Start REST API Server
```bash
python cli.py serve --host 0.0.0.0 --port 8000
```

### Parameter Reference
- `single`: Calculate GBS for one patient (see parameters above)
- `batch`: Process CSV file with `-i` (input) and `-o` (output) options
- `audit`: Process task through multi-worker supervisor
- `chat`: Query the air-gapped supervisory assistant
- `verify-audit`: Verify HMAC-SHA256 audit trail integrity
- `serve`: Start FastAPI REST server

### Input Data Schema (Batch CSV)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `bun` | Blood urea nitrogen in mmol/L | Optional |
| `hemoglobin` | Hemoglobin in g/dL | Optional |
| `sex` | 'male' or 'female' | Optional (default: male) |
| `sbp` | Systolic blood pressure in mmHg | Optional |
| `heart_rate` | Heart rate in bpm | Optional |
| `melena` | Presence of melena (true/false) | Optional |
| `syncope` | History of syncope (true/false) | Optional |
| `hepatic_disease` | Known liver disease (true/false) | Optional |
| `cardiac_failure` | Known cardiac failure (true/false) | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC-SHA256 audit trail | Ephemeral (random per session) |
| `MODEL_PROVIDER` | LLM provider (`mock`, `ollama`, `claude`, `openai`) | `mock` |

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t glasgow-blatchford-bleeding-score .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key glasgow-blatchford-bleeding-score
```

Or using Docker Compose:

```bash
docker-compose up -d
```
