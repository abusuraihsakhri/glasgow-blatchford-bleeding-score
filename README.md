# Glasgow-Blatchford Score (GBS)

> **Pre-endoscopy Risk Stratification for Upper GI Bleeding**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)

---

## Overview

The Glasgow-Blatchford Score (GBS) is a validated pre-endoscopy clinical scoring system that identifies patients with upper GI bleeding who are safe for outpatient management (score 0) versus those requiring urgent intervention (score ≥6).

**Score range: 0-23 points**

This implementation includes:
- Full GBS calculation with all components
- Sex-specific hemoglobin thresholds
- Risk stratification (Very Low → Very High)
- 30-day mortality estimation
- Batch CSV processing

---

## Scoring Components

| Component | Points |
|-----------|--------|
| **BUN (mmol/L)** | 6.5-7.9: **2**, 8.0-9.9: **3**, 10.0-24.9: **4**, ≥25: **6** |
| **Hemoglobin Male (g/dL)** | 12-12.9: **1**, 10-11.9: **3**, <10: **6** |
| **Hemoglobin Female (g/dL)** | 10-11.9: **1**, <10: **6** |
| **SBP (mmHg)** | 100-109: **1**, 90-99: **2**, <90: **3** |
| **Heart rate ≥100** | **1** |
| **Melena** | **1** |
| **Syncope** | **2** |
| **Hepatic disease** | **2** |
| **Cardiac failure** | **2** |

## Risk Categories

| Score | Risk | Action |
|-------|------|--------|
| 0 | Very Low | Safe for outpatient management |
| 1-3 | Low | Consider outpatient with follow-up |
| 4-5 | Moderate | Inpatient admission, urgent endoscopy within 24h |
| 6-8 | High | Inpatient care, urgent endoscopy, consider ICU |
| ≥9 | Very High | ICU admission, immediate resuscitation |

## 30-Day Mortality (Stanley et al. 2009)

| GBS Score | Estimated Mortality |
|-----------|-------------------|
| 0 | ~0% |
| 1-3 | ~0.5% |
| 4-5 | ~2% |
| 6-8 | ~5% |
| 9-11 | ~10% |
| ≥12 | ~20% |

---

## Quick Start

```bash
# Single patient
python glasgow_blatchford.py single --bun 12.0 --hemoglobin 9.5 --sex male --sbp 95 --heart-rate 110 --melena

# Minimal input (all optional)
python glasgow_blatchford.py single --melena --syncope

# Batch processing
python glasgow_blatchford.py batch -i patients.csv -o results.csv
```

## Python API

```python
from glasgow_blatchford import calculate_gbs

result = calculate_gbs(
    bun_mmol_l=12.0, hemoglobin_g_dl=9.5, sex="male",
    sbp_mmhg=95, heart_rate=110, melena=True, syncope=False,
    hepatic_disease=False, cardiac_failure=False,
)

print(f"Score: {result['total_score']}")
print(f"Risk: {result['risk_category']}")
print(f"Safe for outpatient: {result['safe_for_outpatient']}")
print(f"30-day mortality: {result['estimated_30d_mortality_percent']}%")
```

## Tests

```bash
python -m pytest test_glasgow_blatchford.py -v
```

## References

- Blatchford O, et al. A score to predict need for treatment for upper-gastrointestinal haemorrhage. *Lancet* 2000;356:1318-21.
- Stanley AJ, et al. Glasgow Blatchford bleeding score can select patients with upper GI bleeding who can be safely managed as outpatients. *Lancet* 2009;373:42-47.

## License

MIT License. See [LICENSE](LICENSE).
