#!/usr/bin/env python3
"""
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
"""

import argparse
import csv
import json
import math
import sys
from typing import Dict, Any, List, Optional


def calculate_gbs(
    bun_mmol_l: Optional[float] = None,
    hemoglobin_g_dl: Optional[float] = None,
    sex: str = "male",
    sbp_mmhg: Optional[float] = None,
    heart_rate: Optional[float] = None,
    melena: bool = False,
    syncope: bool = False,
    hepatic_disease: bool = False,
    cardiac_failure: bool = False,
) -> Dict[str, Any]:
    """
    Calculate Glasgow-Blatchford Score for upper GI bleed risk stratification.

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
    """
    components = {}
    total = 0

    # --- BUN scoring (mmol/L) ---
    if bun_mmol_l is not None:
        if bun_mmol_l >= 25.0:
            components["bun"] = 6
        elif bun_mmol_l >= 10.0:
            components["bun"] = 4
        elif bun_mmol_l >= 8.0:
            components["bun"] = 3
        elif bun_mmol_l >= 6.5:
            components["bun"] = 2
        else:
            components["bun"] = 0
        total += components["bun"]

    # --- Hemoglobin scoring (sex-dependent) ---
    if hemoglobin_g_dl is not None:
        if sex.lower() == "male":
            if hemoglobin_g_dl < 10.0:
                components["hemoglobin"] = 6
            elif hemoglobin_g_dl < 12.0:
                components["hemoglobin"] = 3
            elif hemoglobin_g_dl <= 12.9:
                components["hemoglobin"] = 1
            else:
                components["hemoglobin"] = 0
        else:  # female
            if hemoglobin_g_dl < 10.0:
                components["hemoglobin"] = 6
            elif hemoglobin_g_dl < 12.0:
                components["hemoglobin"] = 1
            else:
                components["hemoglobin"] = 0
        total += components["hemoglobin"]

    # --- SBP scoring ---
    if sbp_mmhg is not None:
        if sbp_mmhg < 90:
            components["sbp"] = 3
        elif sbp_mmhg < 100:
            components["sbp"] = 2
        elif sbp_mmhg <= 109:
            components["sbp"] = 1
        else:
            components["sbp"] = 0
        total += components["sbp"]

    # --- Heart rate scoring ---
    if heart_rate is not None:
        components["heart_rate"] = 1 if heart_rate >= 100 else 0
        total += components["heart_rate"]

    # --- Clinical features ---
    components["melena"] = 1 if melena else 0
    total += components["melena"]

    components["syncope"] = 2 if syncope else 0
    total += components["syncope"]

    components["hepatic_disease"] = 2 if hepatic_disease else 0
    total += components["hepatic_disease"]

    components["cardiac_failure"] = 2 if cardiac_failure else 0
    total += components["cardiac_failure"]

    # --- Risk stratification ---
    if total == 0:
        risk = "Very Low"
        recommendation = "Consider outpatient management. Outpatient endoscopy if clinically indicated."
        needs_intervention = False
    elif total <= 3:
        risk = "Low"
        recommendation = "Low risk. Consider outpatient management with close follow-up or short observation."
        needs_intervention = False
    elif total <= 5:
        risk = "Moderate"
        recommendation = "Moderate risk. Inpatient admission recommended. Urgent endoscopy within 24 hours."
        needs_intervention = True
    elif total <= 8:
        risk = "High"
        recommendation = "High risk. Inpatient care with urgent endoscopy. Consider ICU if hemodynamically unstable."
        needs_intervention = True
    else:
        risk = "Very High"
        recommendation = "Very high risk. ICU admission. Immediate resuscitation and urgent endoscopy."
        needs_intervention = True

    # --- 30-day mortality estimation (Stanley et al. 2009) ---
    if total == 0:
        mortality_30d = 0.0
    elif total <= 3:
        mortality_30d = 0.5
    elif total <= 5:
        mortality_30d = 2.0
    elif total <= 8:
        mortality_30d = 5.0
    elif total <= 11:
        mortality_30d = 10.0
    else:
        mortality_30d = 20.0

    return {
        "tool": "glasgow-blatchford-score",
        "total_score": total,
        "max_possible_score": 23,
        "components": components,
        "risk_category": risk,
        "recommendation": recommendation,
        "safe_for_outpatient": total == 0,
        "needs_intervention": needs_intervention,
        "estimated_30d_mortality_percent": mortality_30d,
    }


def calculate_gbs_from_dict(params: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate GBS from a dictionary of parameters (for batch/CLI use)."""
    return calculate_gbs(
        bun_mmol_l=_float_or_none(params.get("bun") or params.get("bun_mmol_l")),
        hemoglobin_g_dl=_float_or_none(params.get("hemoglobin") or params.get("hemoglobin_g_dl")),
        sex=str(params.get("sex", "male")),
        sbp_mmhg=_float_or_none(params.get("sbp") or params.get("sbp_mmhg")),
        heart_rate=_float_or_none(params.get("heart_rate") or params.get("hr")),
        melena=_bool_str(params.get("melena")),
        syncope=_bool_str(params.get("syncope")),
        hepatic_disease=_bool_str(params.get("hepatic_disease")),
        cardiac_failure=_bool_str(params.get("cardiac_failure")),
    )


def process_batch(input_csv: str, output_csv: str) -> int:
    """Process a CSV file of patients and write GBS results."""
    with open(input_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    out_fields = fieldnames + [
        "gbs_total_score", "risk_category", "safe_for_outpatient",
        "needs_intervention", "estimated_30d_mortality_percent", "recommendation",
    ]
    out_rows = []
    for r in rows:
        result = calculate_gbs_from_dict(r)
        row_dict = dict(r)
        row_dict["gbs_total_score"] = result["total_score"]
        row_dict["risk_category"] = result["risk_category"]
        row_dict["safe_for_outpatient"] = result["safe_for_outpatient"]
        row_dict["needs_intervention"] = result["needs_intervention"]
        row_dict["estimated_30d_mortality_percent"] = result["estimated_30d_mortality_percent"]
        row_dict["recommendation"] = result["recommendation"]
        out_rows.append(row_dict)

    with open(output_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Processed {len(out_rows)} records -> {output_csv}")
    return len(out_rows)


# =============================================================================
# CLI
# =============================================================================

def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="glasgow-blatchford-score",
        description="Glasgow-Blatchford Score (GBS) - Pre-endoscopy risk stratification for upper GI bleeding",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single calculation
    p_single = subparsers.add_parser("single", help="Calculate GBS for a single patient")
    p_single.add_argument("--bun", type=float, help="BUN in mmol/L")
    p_single.add_argument("--hemoglobin", type=float, help="Hemoglobin in g/dL")
    p_single.add_argument("--sex", choices=["male", "female"], default="male",
                          help="Patient sex (affects hemoglobin thresholds)")
    p_single.add_argument("--sbp", type=float, help="Systolic blood pressure in mmHg")
    p_single.add_argument("--heart-rate", type=float, help="Heart rate in bpm")
    p_single.add_argument("--melena", action="store_true", help="Presence of melena")
    p_single.add_argument("--syncope", action="store_true", help="History of syncope")
    p_single.add_argument("--hepatic-disease", action="store_true", help="Known liver disease")
    p_single.add_argument("--cardiac-failure", action="store_true", help="Known cardiac failure")

    # Batch processing
    p_batch = subparsers.add_parser("batch", help="Batch process CSV file")
    p_batch.add_argument("-i", "--input", required=True, help="Input CSV file")
    p_batch.add_argument("-o", "--output", default="results.csv", help="Output CSV file")

    args = parser.parse_args(argv)

    if args.command == "single":
        result = calculate_gbs(
            bun_mmol_l=args.bun, hemoglobin_g_dl=args.hemoglobin,
            sex=args.sex, sbp_mmhg=args.sbp, heart_rate=args.heart_rate,
            melena=args.melena, syncope=args.syncope,
            hepatic_disease=args.hepatic_disease, cardiac_failure=args.cardiac_failure,
        )
        print(json.dumps(result, indent=2))

    elif args.command == "batch":
        process_batch(args.input, args.output)

    return 0


# =============================================================================
# Helpers
# =============================================================================

def _float_or_none(val) -> Optional[float]:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _bool_str(val) -> bool:
    if val is None:
        return False
    return str(val).lower().strip() in ("true", "1", "yes", "y")


if __name__ == "__main__":
    main()
