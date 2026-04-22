"""Integration tests for R20 ingest + batch + aggregate view (ISP S6-S8).

Requires live BQ access (GOOGLE_APPLICATION_CREDENTIALS set).
Each test uses a unique zblock_string for isolation.
"""
import os
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient


pytestmark = pytest.mark.skipif(
    not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
    reason="BQ credentials not set — integration test skipped",
)


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app)


@pytest.fixture
def zblock():
    return f"PLN/TEST-{uuid.uuid4().hex[:8]}/OPT/G/MF/2026APR22"


def _rec(zblock, **kw):
    base = dict(
        so_row_id="x", io="I", period="M2601", value=1.0,
        scenario="OPT", role_source="GH",
        ppr_file_id="FPA-T", track_variant="IAA",
        zblock_string=zblock,
        upload_batch_id="",
        created_by="pytest@fpa-t.local",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    base.update(kw)
    return base


def _rate_100(zblock, role_source="GH"):
    ventures = ("TER", "VIS", "SMI", "AST", "SAP")
    parts = (25.0, 25.0, 20.0, 20.0, 10.0)
    return [
        _rec(zblock, so_row_id=f"a-{v}", kr1="RATE", kr_code="RATE-PRM-PL2-ALLOCATE",
             cdt1=v, value=p, role_source=role_source)
        for v, p in zip(ventures, parts)
    ]


def test_empty_submit_skipped(client):
    r = client.post("/api/fpa-t/r20/GH/submit", json=[])
    assert r.status_code == 200
    assert r.json()["status"] == "SKIPPED"
    assert r.json()["batch_id"] is None


def test_invalid_submit_422(client, zblock):
    bad = _rate_100(zblock)
    bad[0]["value"] = 10.0  # sum = 85 — not 100
    r = client.post("/api/fpa-t/r20/GH/submit", json=bad)
    assert r.status_code == 422


def test_happy_path_submit_load_rollback(client, zblock):
    # Submit
    payload = _rate_100(zblock)
    r = client.post("/api/fpa-t/r20/GH/submit", json=payload)
    assert r.status_code == 200, r.json()
    batch_id = r.json()["batch_id"]
    assert r.json()["ingested_count"] == 5
    # Load
    r = client.get(f"/api/fpa-t/r20/GH/load?zblock_string={zblock}")
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) == 5
    assert all(row["upload_batch_id"] == batch_id for row in rows)
    # NULL convention verified
    for row in rows:
        assert row["kr2"] is None  # optional not sent → NULL (not "")
    # Batch status
    r = client.get(f"/api/fpa-t/r20/batch/{batch_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "INGESTED"
    assert r.json()["ingested_count"] == 5
    # Rollback
    r = client.post(f"/api/fpa-t/r20/rollback/{batch_id}")
    assert r.status_code == 200
    assert r.json()["deleted_count"] == 5
    # Load empty
    r = client.get(f"/api/fpa-t/r20/GH/load?zblock_string={zblock}")
    assert r.json() == []
    # Rollback twice → 409
    r = client.post(f"/api/fpa-t/r20/rollback/{batch_id}")
    assert r.status_code == 409


def test_refresh_view_endpoint(client):
    r = client.post("/api/fpa-t/r20/refresh-view")
    assert r.status_code == 200
    d = r.json()
    assert "refreshed_at" in d
    assert len(d["source_tables"]) >= 15  # 16 R20_* tables minus batch_audit


def test_variant_required_for_coh(client, zblock):
    payload = [_rec(zblock, so_row_id="x", kr1="GI", kr_code="GI",
                    cdt1="TER", cdt3="TeamA", value=100.0, role_source="COH-TER")]
    r = client.post("/api/fpa-t/r20/COH/submit", json=payload)
    # Missing variant → 400 from registry resolver
    assert r.status_code == 400
    assert "variant" in r.json()["detail"].lower()


def test_coh_variant_happy(client, zblock):
    payload = [_rec(zblock, so_row_id="x", kr1="GI", kr_code="GI",
                    cdt1="TER", cdt3="TeamA", value=100.0, role_source="COH-TER")]
    r = client.post("/api/fpa-t/r20/COH/submit?variant=TER", json=payload)
    assert r.status_code == 200
    batch_id = r.json()["batch_id"]
    # Cleanup
    client.post(f"/api/fpa-t/r20/rollback/{batch_id}")


def test_batch_not_found_404(client):
    r = client.get("/api/fpa-t/r20/batch/does-not-exist")
    assert r.status_code == 404
