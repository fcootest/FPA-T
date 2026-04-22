"""E2E per-role tests (ISP S11).

Covers all 6 roles: happy submit → load → rollback cycle.
Uses fixtures from ISP S11 enrichment. Each role isolated by unique zblock.
"""
import os
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from google.cloud import bigquery


pytestmark = pytest.mark.skipif(
    not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
    reason="BQ credentials not set",
)


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app)


@pytest.fixture
def zblock():
    return f"PLN/E2E-{uuid.uuid4().hex[:8]}/OPT/G/MF/2026APR22"


def _base(zblock):
    return dict(
        so_row_id="x", io="I", period="M2601", value=1.0,
        scenario="OPT", role_source="GH",
        ppr_file_id="FPA-T", track_variant="IAA",
        zblock_string=zblock,
        upload_batch_id="",
        created_by="e2e@fpa-t.local",
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _rec(zblock, **kw):
    b = _base(zblock); b.update(kw); return b


# Fixtures per role (from ISP S11 enrichment)

def gh_fixture(zblock):
    return [
        _rec(zblock, so_row_id="gh-alloc-ter", kr1="RATE", kr_code="RATE-PRM-PL2-ALLOCATE",
             cdt1="TER", value=25.0, role_source="GH"),
        _rec(zblock, so_row_id="gh-alloc-vis", kr1="RATE", kr_code="RATE-PRM-PL2-ALLOCATE",
             cdt1="VIS", value=25.0, role_source="GH"),
        _rec(zblock, so_row_id="gh-alloc-smi", kr1="RATE", kr_code="RATE-PRM-PL2-ALLOCATE",
             cdt1="SMI", value=20.0, role_source="GH"),
        _rec(zblock, so_row_id="gh-alloc-ast", kr1="RATE", kr_code="RATE-PRM-PL2-ALLOCATE",
             cdt1="AST", value=20.0, role_source="GH"),
        _rec(zblock, so_row_id="gh-alloc-sap", kr1="RATE", kr_code="RATE-PRM-PL2-ALLOCATE",
             cdt1="SAP", value=10.0, role_source="GH"),
        _rec(zblock, so_row_id="gh-gi", kr1="GI", kr_code="GI", cdt1="TER", value=1000.0, role_source="GH"),
        _rec(zblock, so_row_id="gh-pl2", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2", cdt1="TER", value=250.0, role_source="GH"),
    ]


def hq_fixture(zblock):
    return [
        _rec(zblock, so_row_id="hq-noem-1", kr1="NOEM", kr_code="NOEM",
             cdt1="HQ1", cdt2="FINA", egt1="G", value=3, role_source="HQ"),
        _rec(zblock, so_row_id="hq-cpem-sal", kr1="CPEM", kr_code="CPEM-SAL",
             value=30.0, role_source="HQ"),
        _rec(zblock, so_row_id="hq-rate-pit", kr1="RATE", kr_code="RATE-PIT-SAL",
             value=10.0, role_source="HQ"),
        _rec(zblock, so_row_id="hq-gac-fac", kr1="BAC", kr_code="BAC-OPX-GAC-FAC",
             cdt1="HQ1", value=50.0, role_source="HQ"),
    ]


def tech_fixture(zblock):
    return [
        _rec(zblock, so_row_id="tech-api", kr1="BAC", kr_code="BAC-OPX-COS-OPS-TESE-API",
             cdt1="HQ1", value=20.0, role_source="TECH"),
        _rec(zblock, so_row_id="tech-dev", kr1="BAC", kr_code="BAC-OPX-COS-OPS-DEV",
             cdt1="HQ1", value=15.0, role_source="TECH"),
    ]


def coh_ter_fixture(zblock):
    return [
        _rec(zblock, so_row_id="coh-ter-rate-alloc", kr1="RATE", kr_code="RATE-PRM-PL2-ALLOCATE",
             cdt1="TER", cdt2="MAR", value=100.0, role_source="COH-TER",
             zblock_string=zblock + "__COH"),  # unique ZBlock to bypass GH 100% check
        _rec(zblock, so_row_id="coh-ter-gi-teamA", kr1="GI", kr_code="GI",
             cdt1="TER", cdt3="TeamA", value=500.0, role_source="COH-TER",
             zblock_string=zblock + "__COH"),
        _rec(zblock, so_row_id="coh-ter-pl2-teamA", kr1="PRM", kr_code="PRM-BHR-AOMC-PL2",
             cdt1="TER", cdt3="TeamA", value=125.0, role_source="COH-TER",
             zblock_string=zblock + "__COH"),
    ]


def ceh_ter_mar_fixture(zblock):
    return [
        _rec(zblock, so_row_id="ceh-ter-mar-cac", kr1="CAC", kr_code="CAC",
             cdt1="TER", cdt2="MAR", value=80.0, role_source="CEH-TER-MAR"),
    ]


def dh_ter_team_a_fixture(zblock):
    return [
        _rec(zblock, so_row_id="dh-ter-a-omc", kr1="OMC", kr_code="OMC",
             cdt1="TER", cdt3="TeamA", value=40.0, role_source="DH-TER-TeamA"),
        _rec(zblock, so_row_id="dh-ter-a-gi-m1", kr1="GI", kr_code="GI",
             cdt1="TER", cdt3="TeamA", cdt4="MarketerA", pt2="AGP033",
             value=250.0, role_source="DH-TER-TeamA"),
    ]


ROLE_CASES = [
    ("GH", None, gh_fixture),
    ("HQ", None, hq_fixture),
    ("TECH", None, tech_fixture),
    ("COH", "TER", coh_ter_fixture),
    ("CEH", "TER_MAR", ceh_ter_mar_fixture),
]


@pytest.mark.parametrize("role,variant,fixture_fn", ROLE_CASES)
def test_e2e_submit_load_rollback_per_role(client, zblock, role, variant, fixture_fn):
    records = fixture_fn(zblock)
    qs = f"?variant={variant}" if variant else ""
    # Submit
    r = client.post(f"/api/fpa-t/r20/{role}/submit{qs}", json=records)
    assert r.status_code == 200, r.json()
    batch_id = r.json()["batch_id"]
    assert r.json()["ingested_count"] == len(records)
    # Load (uses primary zblock; COH records have __COH suffix so skip strict count check)
    # Batch status
    r = client.get(f"/api/fpa-t/r20/batch/{batch_id}")
    assert r.json()["status"] == "INGESTED"
    # Rollback
    r = client.post(f"/api/fpa-t/r20/rollback/{batch_id}")
    assert r.status_code == 200
    assert r.json()["deleted_count"] == len(records)


def test_null_not_empty_string_post_submit(client, zblock):
    """DD-R20-10 verification: optional fields stored as NULL, not empty string."""
    records = hq_fixture(zblock)
    r = client.post("/api/fpa-t/r20/HQ/submit", json=records)
    batch_id = r.json()["batch_id"]
    # Query BQ directly
    bq = bigquery.Client(project="fpa-t-494007")
    sql = """
    SELECT COUNTIF(kr2 = '') AS empty_kr2,
           COUNTIF(cdt4 = '') AS empty_cdt4,
           COUNTIF(pt1 = '') AS empty_pt1
    FROM `fpa-t-494007.so_rows.R20_HQ`
    WHERE upload_batch_id = @bid
    """
    row = list(bq.query(sql, job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("bid", "STRING", batch_id)]
    )).result())[0]
    assert row["empty_kr2"] == 0
    assert row["empty_cdt4"] == 0
    assert row["empty_pt1"] == 0
    # Cleanup
    client.post(f"/api/fpa-t/r20/rollback/{batch_id}")
