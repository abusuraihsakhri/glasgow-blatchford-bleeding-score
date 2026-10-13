# Glasgow–Blatchford Bleeding Score

Pre-endoscopy Glasgow–Blatchford Score (GBS) calculator for adults with suspected upper gastrointestinal bleeding. The score ranges from **0 to 23** and uses blood urea, hemoglobin, sex-specific hemoglobin thresholds, systolic blood pressure, heart rate and four clinical features.

The repository provides a **standalone, browser-based calculator**, a Python scoring library and CLI, batch CSV processing, and a FastAPI endpoint. A separate demonstration audit/supervisor subsystem remains available for backward compatibility; its generic thresholds are **not** clinical GBS rules.

## Browser calculator

Open `web/index.html` locally or serve the repository's root with a static file server. The root `index.html` redirects to the calculator. The browser app is plain HTML, CSS and JavaScript: **no backend, Pyodide, or package installation is needed**.

The repository is configured with a GitHub Pages homepage, but the live endpoint was not independently verifiable during this audit; no public availability claim is made here.

Enter all four numerical measurements and the hemoglobin reference category, confirm which listed clinical features are present, then select **Calculate GBS**. The app displays the total and component points. **Unchecked checkboxes are treated as absent findings**; verify clinical history before interpreting the result.

- **Urea:** mmol/L, not BUN mg/dL (do not enter a mg/dL value without conversion).
- **Hemoglobin:** g/dL; **SBP:** mmHg; **heart rate:** beats/min.
- **GBS 0–1:** very-low-risk group; outpatient follow-up *may* be appropriate after clinical assessment.
- **GBS >1:** not in the very-low-risk group; admission, resuscitation, and endoscopy decisions require assessment of the whole patient.

**Safety:** GBS is not a calibrated individual mortality prediction or a substitute for urgent assessment in ongoing bleeding or hemodynamic instability. Incomplete clinical information should never support a low-risk discharge decision.

## Python and CLI

Python 3.10+.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
node --test web/gbs.test.cjs  # Node.js 22+; browser algorithm tests
python cli.py single --bun 10 --hemoglobin 9 --sex male --sbp 95 --heart-rate 104 --melena
python cli.py batch --input sample.csv --output results.csv
```

In Python, `calculate_gbs(...)` returns `total_score`, `components`, `is_complete`, `missing_fields`, `risk_category`, `safe_for_outpatient` and `recommendation`. Missing numerical values produce a **partial score labeled incomplete**, never a discharge-eligible result. The retained legacy keys `needs_intervention` and `estimated_30d_mortality_percent` are always null: the score alone cannot establish those individual outcomes. The legacy `safe_for_outpatient` flag (also exposed as `very_low_risk_criterion_met`) marks the GBS threshold, **not clearance for discharge**.

CSV columns: `bun` (urea mmol/L), `hemoglobin` (g/dL), `sex` (`male`/`female`), `sbp`, `heart_rate`, `melena`, `syncope`, `hepatic_disease`, `cardiac_failure`. Use `true`/`false` for all four clinical features. The batch result contains an `is_complete` field and semicolon-delimited `missing_fields`; missing sex or feature columns are never interpreted as confirmed negatives for disposition. Unexpected strings and impossible numerical values are rejected.

The CLI also retains `audit`, `chat`, `verify-audit` and `serve` commands. For API use:

```bash
python cli.py serve --host 127.0.0.1 --port 8000
# POST JSON clinical inputs to http://127.0.0.1:8000/api/gbs
# GET http://127.0.0.1:8000/docs for the OpenAPI interface
```

The `/api/gbs` endpoint requires all numerical inputs, the hemoglobin reference category and explicit true/false values for all four clinical features. It rejects unexpected extra fields, including identifiers.

## Privacy and security

The browser scoring interface sends no clinical values to a server and does not store them in local storage or cookies. No identifying data should be entered. The optional API and legacy demo supervisor run server-side and must not be exposed to public networks without appropriate security controls. The legacy regular-expression identifier screening is **not** a PHI de-identification or HIPAA compliance guarantee.

The audit ledger uses HMAC-SHA256 signatures with a linked chain and verifies each signature; by default its key is ephemeral and its in-memory trail is not persistent. For a persistent deployment, supply a strong private `AUDIT_SECRET_KEY` through the environment, not source control. Rotate any secrets previously committed to repository history.

```bash
# Set AUDIT_SECRET_KEY securely in the environment before starting Compose.
docker compose up --build
```

## Technology, verification and limitations

The static interface uses browser JavaScript and works in modern desktop/mobile browsers. Python functionality is available through the CLI or FastAPI; it does not execute in the static site. Tests run with `pytest` and Node's built-in test runner in GitHub Actions on Python 3.10, 3.11 and 3.12.

The calculation is a pre-endoscopy risk score; it is **not** an automated triage or treatment algorithm. The generic supervisor's warnings do not constitute a clinical protocol.

## Clinical references

- Blatchford O, et al. A risk score to predict need for treatment for upper-gastrointestinal haemorrhage. *Lancet*. 2000;356:1318–1321.
- [Laine L, et al. ACG Clinical Guideline: Upper Gastrointestinal and Ulcer Bleeding. *Am J Gastroenterol*. 2021.](https://pubmed.ncbi.nlm.nih.gov/33929377/)
- [Gralnek IM, et al. ESGE guideline update on nonvariceal upper gastrointestinal hemorrhage. *Endoscopy*. 2021.](https://pubmed.ncbi.nlm.nih.gov/33567467/)

## License

MIT. See [LICENSE](LICENSE).
