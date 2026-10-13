"""Static deployment checks that require no browser or network."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_root_entry_points_to_browser_app():
    root = (ROOT / "index.html").read_text(encoding="utf-8")
    assert "./web/index.html" in root


def test_browser_calculator_fields_and_script():
    page = (ROOT / "web/index.html").read_text(encoding="utf-8")
    assert '<form id="gbs-form">' in page
    for name in ("urea", "hemoglobin", "sex", "sbp", "pulse",
                 "melena", "syncope", "hepaticDisease", "cardiacFailure"):
        assert f'id="{name}"' in page
    assert '<script src="./gbs.js"></script>' in page
    assert "fetch('/api/audit'" not in page
    assert "HMAC_SHA256_e83f9a72" not in page
