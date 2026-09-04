#!/usr/bin/env python3
"""
Tests for Glasgow-Blatchford Score (GBS) - Full implementation.
"""
import json
import sys
import os
import csv
import pytest

sys.path.insert(0, os.path.dirname(__file__))

from glasgow_blatchford import calculate_gbs, calculate_gbs_from_dict, process_batch, main


# =============================================================================
# BUN Scoring Tests
# =============================================================================

class TestBUNScoring:
    def test_bun_below_threshold(self):
        result = calculate_gbs(bun_mmol_l=5.0)
        assert result["components"]["bun"] == 0

    def test_bun_6_5(self):
        result = calculate_gbs(bun_mmol_l=6.5)
        assert result["components"]["bun"] == 2

    def test_bun_7_9(self):
        result = calculate_gbs(bun_mmol_l=7.9)
        assert result["components"]["bun"] == 2

    def test_bun_8_0(self):
        result = calculate_gbs(bun_mmol_l=8.0)
        assert result["components"]["bun"] == 3

    def test_bun_9_9(self):
        result = calculate_gbs(bun_mmol_l=9.9)
        assert result["components"]["bun"] == 3

    def test_bun_10_0(self):
        result = calculate_gbs(bun_mmol_l=10.0)
        assert result["components"]["bun"] == 4

    def test_bun_24_9(self):
        result = calculate_gbs(bun_mmol_l=24.9)
        assert result["components"]["bun"] == 4

    def test_bun_25(self):
        result = calculate_gbs(bun_mmol_l=25.0)
        assert result["components"]["bun"] == 6


# =============================================================================
# Hemoglobin Scoring Tests
# =============================================================================

class TestHemoglobinScoring:
    def test_male_hgb_normal(self):
        result = calculate_gbs(hemoglobin_g_dl=14.0, sex="male")
        assert result["components"]["hemoglobin"] == 0

    def test_male_hgb_12_to_12_9(self):
        result = calculate_gbs(hemoglobin_g_dl=12.5, sex="male")
        assert result["components"]["hemoglobin"] == 1

    def test_male_hgb_10_to_11_9(self):
        result = calculate_gbs(hemoglobin_g_dl=11.0, sex="male")
        assert result["components"]["hemoglobin"] == 3

    def test_male_hgb_below_10(self):
        result = calculate_gbs(hemoglobin_g_dl=9.0, sex="male")
        assert result["components"]["hemoglobin"] == 6

    def test_female_hgb_normal(self):
        result = calculate_gbs(hemoglobin_g_dl=13.0, sex="female")
        assert result["components"]["hemoglobin"] == 0

    def test_female_hgb_10_to_11_9(self):
        result = calculate_gbs(hemoglobin_g_dl=11.0, sex="female")
        assert result["components"]["hemoglobin"] == 1

    def test_female_hgb_below_10(self):
        result = calculate_gbs(hemoglobin_g_dl=8.5, sex="female")
        assert result["components"]["hemoglobin"] == 6


# =============================================================================
# SBP Scoring Tests
# =============================================================================

class TestSBPScoring:
    def test_sbp_normal(self):
        result = calculate_gbs(sbp_mmhg=120)
        assert result["components"]["sbp"] == 0

    def test_sbp_100_to_109(self):
        result = calculate_gbs(sbp_mmhg=105)
        assert result["components"]["sbp"] == 1

    def test_sbp_90_to_99(self):
        result = calculate_gbs(sbp_mmhg=95)
        assert result["components"]["sbp"] == 2

    def test_sbp_below_90(self):
        result = calculate_gbs(sbp_mmhg=80)
        assert result["components"]["sbp"] == 3


# =============================================================================
# Clinical Feature Tests
# =============================================================================

class TestClinicalFeatures:
    def test_hr_elevated(self):
        result = calculate_gbs(heart_rate=100)
        assert result["components"]["heart_rate"] == 1

    def test_hr_normal(self):
        result = calculate_gbs(heart_rate=99)
        assert result["components"]["heart_rate"] == 0

    def test_melena_present(self):
        result = calculate_gbs(melena=True)
        assert result["components"]["melena"] == 1

    def test_syncope_present(self):
        result = calculate_gbs(syncope=True)
        assert result["components"]["syncope"] == 2

    def test_hepatic_disease(self):
        result = calculate_gbs(hepatic_disease=True)
        assert result["components"]["hepatic_disease"] == 2

    def test_cardiac_failure(self):
        result = calculate_gbs(cardiac_failure=True)
        assert result["components"]["cardiac_failure"] == 2


# =============================================================================
# Risk Stratification Tests
# =============================================================================

class TestRiskStratification:
    def test_score_zero_outpatient(self):
        result = calculate_gbs(bun_mmol_l=4.0, hemoglobin_g_dl=15.0,
                               sex="male", sbp_mmhg=130, heart_rate=72)
        assert result["total_score"] == 0
        assert result["safe_for_outpatient"] is True
        assert result["risk_category"] == "Very Low"
        assert result["needs_intervention"] is False

    def test_score_low_risk(self):
        result = calculate_gbs(melena=True, heart_rate=105)
        assert result["total_score"] == 2
        assert result["risk_category"] == "Low"

    def test_score_moderate_risk(self):
        result = calculate_gbs(bun_mmol_l=9.0, sbp_mmhg=105, melena=True)
        assert result["total_score"] == 5
        assert result["risk_category"] == "Moderate"
        assert result["needs_intervention"] is True

    def test_score_high_risk(self):
        result = calculate_gbs(bun_mmol_l=15.0, hemoglobin_g_dl=11.0,
                               sex="male", sbp_mmhg=95, heart_rate=110,
                               melena=True)
        assert result["total_score"] >= 6
        assert result["risk_category"] in ("High", "Very High")

    def test_max_score_23(self):
        result = calculate_gbs(
            bun_mmol_l=30.0, hemoglobin_g_dl=8.0, sex="male",
            sbp_mmhg=80, heart_rate=120,
            melena=True, syncope=True,
            hepatic_disease=True, cardiac_failure=True,
        )
        assert result["total_score"] == 23
        assert result["max_possible_score"] == 23


# =============================================================================
# 30-Day Mortality Tests
# =============================================================================

class TestMortality:
    def test_mortality_zero_score(self):
        result = calculate_gbs()
        assert result["estimated_30d_mortality_percent"] == 0.0

    def test_mortality_low_score(self):
        result = calculate_gbs(melena=True)
        assert result["estimated_30d_mortality_percent"] == 0.5

    def test_mortality_high_score(self):
        result = calculate_gbs(
            bun_mmol_l=30.0, hemoglobin_g_dl=8.0, sex="male",
            sbp_mmhg=80, heart_rate=120,
            melena=True, syncope=True,
            hepatic_disease=True, cardiac_failure=True,
        )
        assert result["estimated_30d_mortality_percent"] == 20.0


# =============================================================================
# Batch Processing Tests
# =============================================================================

class TestBatch:
    def test_batch_processing(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text(
            "patient_id,bun,hemoglobin,sex,sbp,heart_rate,melena,syncope,hepatic_disease,cardiac_failure\n"
            "P001,4.0,14.0,male,130,72,false,false,false,false\n"
            "P002,15.0,9.0,male,85,110,true,true,true,true\n",
            encoding="utf-8",
        )
        count = process_batch(str(csv_in), str(csv_out))
        assert count == 2
        assert csv_out.exists()
        content = csv_out.read_text(encoding="utf-8")
        assert "gbs_total_score" in content
        assert "risk_category" in content


# =============================================================================
# CLI Tests
# =============================================================================

class TestCLI:
    def test_cli_single(self):
        ret = main(["single", "--bun", "10.0", "--hemoglobin", "9.0",
                     "--sex", "male", "--sbp", "95", "--melena"])
        assert ret == 0

    def test_cli_single_minimal(self):
        ret = main(["single"])
        assert ret == 0

    def test_cli_batch(self, tmp_path):
        csv_in = tmp_path / "in.csv"
        csv_out = tmp_path / "out.csv"
        csv_in.write_text("bun,hemoglobin\n10.0,14.0\n", encoding="utf-8")
        ret = main(["batch", "-i", str(csv_in), "-o", str(csv_out)])
        assert ret == 0
        assert csv_out.exists()


# =============================================================================
# From Dict Tests
# =============================================================================

class TestFromDict:
    def test_from_dict_basic(self):
        params = {"bun": "10.0", "hemoglobin": "9.0", "sex": "male", "sbp": "95"}
        result = calculate_gbs_from_dict(params)
        assert result["total_score"] > 0
        assert "risk_category" in result

    def test_from_dict_empty(self):
        result = calculate_gbs_from_dict({})
        assert result["total_score"] == 0


# =============================================================================
# Input Validation Tests
# =============================================================================

class TestInputValidation:
    def test_negative_bun_raises(self):
        with pytest.raises(ValueError, match="bun_mmol_l.*outside plausible range"):
            calculate_gbs(bun_mmol_l=-5.0)

    def test_extreme_bun_raises(self):
        with pytest.raises(ValueError, match="bun_mmol_l.*outside plausible range"):
            calculate_gbs(bun_mmol_l=150.0)

    def test_negative_hemoglobin_raises(self):
        with pytest.raises(ValueError, match="hemoglobin_g_dl.*outside plausible range"):
            calculate_gbs(hemoglobin_g_dl=-1.0)

    def test_extreme_hemoglobin_raises(self):
        with pytest.raises(ValueError, match="hemoglobin_g_dl.*outside plausible range"):
            calculate_gbs(hemoglobin_g_dl=50.0)

    def test_negative_sbp_raises(self):
        with pytest.raises(ValueError, match="sbp_mmhg.*outside plausible range"):
            calculate_gbs(sbp_mmhg=-10.0)

    def test_extreme_sbp_raises(self):
        with pytest.raises(ValueError, match="sbp_mmhg.*outside plausible range"):
            calculate_gbs(sbp_mmhg=400.0)

    def test_negative_heart_rate_raises(self):
        with pytest.raises(ValueError, match="heart_rate.*outside plausible range"):
            calculate_gbs(heart_rate=-5.0)

    def test_extreme_heart_rate_raises(self):
        with pytest.raises(ValueError, match="heart_rate.*outside plausible range"):
            calculate_gbs(heart_rate=500.0)

    def test_invalid_sex_raises(self):
        with pytest.raises(ValueError, match="sex must be"):
            calculate_gbs(sex="unknown")

    def test_nan_input_raises(self):
        with pytest.raises(ValueError, match="must be a finite number"):
            calculate_gbs(bun_mmol_l=float("nan"))

    def test_inf_input_raises(self):
        with pytest.raises(ValueError, match="must be a finite number"):
            calculate_gbs(hemoglobin_g_dl=float("inf"))

    def test_valid_boundary_values(self):
        result = calculate_gbs(bun_mmol_l=0.0, hemoglobin_g_dl=30.0, sbp_mmhg=300.0, heart_rate=300.0)
        assert result["total_score"] > 0

    def test_none_values_accepted(self):
        result = calculate_gbs(bun_mmol_l=None, hemoglobin_g_dl=None)
        assert result["total_score"] == 0


# =============================================================================
# Extended CLI Tests
# =============================================================================

class TestExtendedCLI:
    def test_cli_audit(self):
        ret = main(["audit", "--task-id", "TEST-001"])
        assert ret == 0

    def test_cli_audit_critical(self):
        ret = main(["audit", "--task-id", "TEST-002", "--critical"])
        assert ret == 0

    def test_cli_chat(self):
        ret = main(["chat", "Explain", "scoring"])
        assert ret == 0

    def test_cli_chat_empty(self):
        ret = main(["chat"])
        assert ret == 0

    def test_cli_verify_audit(self):
        ret = main(["verify-audit"])
        assert ret == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
