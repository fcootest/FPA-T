"""Tests for R20_validation_service (ISP S5)."""
from datetime import datetime, timezone
from models.R20_record_model import R20RecordModel
from services.R20_validation_service import r20_validate


def _rec(**kw):
    base = dict(
        so_row_id="x", io="I", period="M2601", value=1.0,
        scenario="OPT", role_source="GH",
        ppr_file_id="FPA-T", track_variant="IAA",
        created_by="u", created_at=datetime.now(timezone.utc),
    )
    base.update(kw)
    return R20RecordModel(**base)


def _zb(s="PLN/T/OPT/G/MF/2026"):
    return s


# --- Rule 2: Rate Alloc sum = 100% ---

def _rate_set(total=100.0, zblock=None):
    """Build 5 RATE-PRM-PL2-ALLOCATE rows summing to `total`."""
    zblock = zblock or _zb()
    parts = [total * f for f in (0.25, 0.25, 0.20, 0.20, 0.10)]
    ventures = ("TER", "VIS", "SMI", "AST", "SAP")
    return [
        _rec(so_row_id=f"a-{v}", kr1="RATE", kr_code="RATE-PRM-PL2-ALLOCATE",
             cdt1=v, value=round(p, 4), zblock_string=zblock)
        for v, p in zip(ventures, parts)
    ]


def test_rate_sum_exact_100_valid():
    r = r20_validate("GH", _rate_set(100.0))
    errs = [e for e in r.errors if e.code == "rate_sum_violation"]
    assert not errs


def test_rate_sum_99_5_invalid():
    r = r20_validate("GH", _rate_set(99.5))
    assert any(e.code == "rate_sum_violation" for e in r.errors)


def test_rate_sum_100_005_within_tolerance():
    r = r20_validate("GH", _rate_set(100.005))
    assert not any(e.code == "rate_sum_violation" for e in r.errors)


def test_rate_sum_100_02_over_tolerance():
    r = r20_validate("GH", _rate_set(100.02))
    assert any(e.code == "rate_sum_violation" for e in r.errors)


# --- Rule 1: R20↔R100 sum ---

def test_r20_r100_sum_match_valid():
    records = [
        # R20 row (no cdt2/3/4)
        _rec(so_row_id="r20", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2",
             cdt1="TER", period="M2601", value=100.0),
        # R100 rows (with cdt3 teams summing to 100)
        _rec(so_row_id="r100a", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2",
             cdt1="TER", cdt3="TeamA", period="M2601", value=60.0),
        _rec(so_row_id="r100b", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2",
             cdt1="TER", cdt3="TeamB", period="M2601", value=40.0),
    ]
    r = r20_validate("COH-TER", records)
    assert not any(e.code == "r20_r100_mismatch" for e in r.errors)


def test_r20_r100_sum_mismatch_invalid():
    records = [
        _rec(so_row_id="r20", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2",
             cdt1="TER", period="M2601", value=100.0),
        _rec(so_row_id="r100a", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2",
             cdt1="TER", cdt3="TeamA", period="M2601", value=50.0),
    ]
    r = r20_validate("COH-TER", records)
    assert any(e.code == "r20_r100_mismatch" for e in r.errors)


# --- Rule 3: NOEM sourcing contract ---

def test_gh_submits_noem_rejected():
    records = [_rec(so_row_id="gh-noem", kr1="NOEM", kr_code="NOEM", value=3)]
    r = r20_validate("GH", records)
    assert any(e.code == "noem_contract_violation" for e in r.errors)


def test_hq_submits_noem_valid():
    records = [_rec(so_row_id="hq-noem", kr1="NOEM", kr_code="NOEM",
                    cdt1="HQ1", cdt2="FINA", egt1="G", value=3, role_source="HQ")]
    r = r20_validate("HQ", records)
    assert not any(e.code == "noem_contract_violation" for e in r.errors)


def test_ceh_submits_noem_rejected():
    records = [_rec(so_row_id="ceh-noem", kr1="NOEM", kr_code="NOEM", value=3)]
    r = r20_validate("CEH-TER-MAR", records)
    assert any(e.code == "noem_contract_violation" for e in r.errors)


# --- Rule 4: GH Mode A/B over-determined ---

def test_gh_mode_a_valid():
    """Mode A: GI + PL2 only."""
    records = _rate_set(100.0) + [
        _rec(so_row_id="gi", kr1="GI", kr_code="GI", cdt1="TER", value=1000.0),
        _rec(so_row_id="pl2", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2", cdt1="TER", value=250.0),
    ]
    r = r20_validate("GH", records)
    assert not any(e.code.startswith("mode_") for e in r.errors)


def test_gh_mode_b_valid():
    """Mode B: PL2 + Rate only."""
    records = _rate_set(100.0) + [
        _rec(so_row_id="pl2", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2", cdt1="TER", value=250.0),
        _rec(so_row_id="rate", kr1="RATE", kr_code="RATE-PRM-PL2-PER-GI", cdt1="TER", value=25.0),
    ]
    r = r20_validate("GH", records)
    assert not any(e.code.startswith("mode_") for e in r.errors)


def test_gh_over_determined_rejected():
    """GI + PL2 + Rate all present → REJECT."""
    records = _rate_set(100.0) + [
        _rec(so_row_id="gi", kr1="GI", kr_code="GI", cdt1="TER", value=1000.0),
        _rec(so_row_id="pl2", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2", cdt1="TER", value=250.0),
        _rec(so_row_id="rate", kr1="RATE", kr_code="RATE-PRM-PL2-PER-GI", cdt1="TER", value=25.0),
    ]
    r = r20_validate("GH", records)
    assert any(e.code == "mode_over_determined" for e in r.errors)


# --- V5.6 Match strategy audit: PL2 filter must exclude RATE-PL2 ---

def test_pl2_filter_excludes_rate_rows():
    """Rate-PL2 row (0-100%) must NOT be treated as monetary PL2 (thousands bVND)."""
    records = [
        # Real PL2 R20
        _rec(so_row_id="pl2-r20", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2",
             cdt1="TER", period="M2601", value=100.0),
        # R100 breakdown sums to 100 (valid)
        _rec(so_row_id="pl2-r100", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2",
             cdt1="TER", cdt3="TeamA", period="M2601", value=100.0),
        # RATE-PRM-PL2-ALLOCATE row — MUST NOT pollute sum rule
        _rec(so_row_id="rate-pl2", kr1="RATE", kr_code="RATE-PRM-PL2-ALLOCATE",
             cdt1="TER", period="M2601", value=25.0),
    ]
    r = r20_validate("COH-TER", records)
    assert not any(e.code == "r20_r100_mismatch" for e in r.errors)


# --- Happy path complete ---

def test_empty_records_valid():
    r = r20_validate("GH", [])
    assert r.valid
    assert r.errors == []
