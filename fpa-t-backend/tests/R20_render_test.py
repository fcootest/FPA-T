import pytest
from fastapi import HTTPException
from services.R20_render_service import r20_get_schema
from config.R20_layout_config import compute_period_cols


def test_schema_gh_full_template():
    s = r20_get_schema("GH")
    section_ids = {sec["id"] for sec in s["sections"]}
    assert {"r20_mix", "pl_tang", "nhom_chi_so", "chi_so_cau_thanh", "r100_noem"} <= section_ids


def test_schema_hq_omits_gi_pl():
    s = r20_get_schema("HQ")
    all_krs = [kr for sec in s["sections"] for kr in sec["kr_codes"]]
    assert "GI" not in all_krs
    assert "PL3" not in all_krs
    assert "NOEM" in all_krs


def test_schema_tech_cos_ops_only():
    s = r20_get_schema("TECH")
    all_krs = [kr for sec in s["sections"] for kr in sec["kr_codes"]]
    assert all(kr.startswith("BAC-OPX-COS-OPS") for kr in all_krs)


def test_schema_unknown_role_404():
    with pytest.raises(HTTPException) as exc:
        r20_get_schema("UNKNOWN")
    assert exc.value.status_code == 404


def test_schema_role_normalized_uppercase():
    s_lower = r20_get_schema("gh")
    s_upper = r20_get_schema("GH")
    assert s_lower == s_upper


def test_period_cols_mf_12_months():
    cols = compute_period_cols("MF")
    assert cols == [f"M26{m:02d}" for m in range(1, 13)]


def test_period_cols_yf_single():
    assert compute_period_cols("YF") == ["Y26"]


def test_period_cols_qf_4_quarters():
    assert compute_period_cols("QF") == ["Q2601", "Q2602", "Q2603", "Q2604"]
