"""R20 Ingest Service (ISP S6) — validate + pivot + DML INSERT + batch_id.

AP DD-R20-07: DML INSERT only (no streaming). Rollback via DELETE works immediately.
AP DD-R20-10: optional strings stored NULL, not "".
AP S13 gotcha #5: strip in-memory-only fields before write.
"""
from typing import Optional
from datetime import datetime, timezone
from fastapi import HTTPException
from google.cloud import bigquery
from models.R20_record_model import R20RecordModel, R20IngestResponse
from models.R20_table_registry import r20_resolve_table_name
from services.R20_bq_client import get_bq_client
from services.R20_validation_service import r20_validate
from services.R20_batch_manager import new_batch_id, log_batch
from services.R20_aggregate_service import r20_refresh_aggregate_view


# Fields stored in BQ (from AP S1.3, 46 cols)
BQ_COLUMNS = [
    "input_id", "so_row_id", "session_id", "plan_type", "zblock_string", "io",
    "kr_type", "kr1", "kr2", "kr3", "kr4", "kr5", "kr6", "kr7", "kr8",
    "kr_code", "kr_name",
    "cdt1", "cdt2", "cdt3", "cdt4",
    "pt1", "pt2", "du", "pt1_prev", "pt2_prev", "du_prev",
    "own_type", "fu1_code", "fu2_code",
    "egt1", "egt2", "egt3", "egt4", "egt5",
    "hr1", "hr2", "hr3",
    "sec", "le1", "le2",
    "period", "value", "scenario", "role_source",
    "ppr_file_id", "track_variant",
    "alloc_znumber", "forecast_frequency", "noem_grade",
    "upload_batch_id", "created_by", "created_at",
]


def _record_to_row(r: R20RecordModel, batch_id: str, user_email: str) -> dict:
    """Serialize record to BQ-insertable dict. NULL convention enforced (DD-R20-10)."""
    out: dict = {}
    for f in BQ_COLUMNS:
        if f == "upload_batch_id":
            out[f] = batch_id
            continue
        if f == "created_by":
            out[f] = r.created_by or user_email
            continue
        if f == "created_at":
            out[f] = r.created_at.isoformat() if r.created_at else datetime.now(timezone.utc).isoformat()
            continue
        v = getattr(r, f, None)
        # NULL convention: empty string → None
        if isinstance(v, str) and v == "":
            v = None
        out[f] = v
    return out


def r20_ingest_submit(
    role: str,
    records: list[R20RecordModel],
    user_email: str,
    variant: Optional[str] = None,
) -> R20IngestResponse:
    # Empty input handling (AP S18)
    if not records:
        return R20IngestResponse(batch_id=None, ingested_count=0, status="SKIPPED")
    # Validate
    result = r20_validate(role, records)
    if not result.valid:
        raise HTTPException(422, detail={"errors": [e.model_dump() for e in result.errors]})
    # Resolve target table
    try:
        table = r20_resolve_table_name(role, variant)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    # Generate batch id
    batch_id = new_batch_id()
    rows = [_record_to_row(r, batch_id, user_email) for r in records]
    # DML INSERT (strongly consistent — DD-R20-07)
    cols_list = ", ".join(BQ_COLUMNS)
    placeholders = ", ".join(f"@p_{i}_{f}" for i in range(len(rows)) for f in BQ_COLUMNS)
    # Build multi-VALUES INSERT with one param set per row
    values_rows = []
    params: list[bigquery.ScalarQueryParameter] = []
    for i, row in enumerate(rows):
        tuple_params = []
        for f in BQ_COLUMNS:
            pname = f"p_{i}_{f}"
            tuple_params.append(f"@{pname}")
            bq_type = "FLOAT64" if f == "value" else "TIMESTAMP" if f == "created_at" else "STRING"
            params.append(bigquery.ScalarQueryParameter(pname, bq_type, row[f]))
        values_rows.append(f"({', '.join(tuple_params)})")
    sql = f"INSERT INTO `{table}` ({cols_list}) VALUES {', '.join(values_rows)}"
    get_bq_client().query(
        sql, job_config=bigquery.QueryJobConfig(query_parameters=params)
    ).result()
    # Log + refresh view
    log_batch(batch_id, role, variant, table, len(rows), user_email)
    r20_refresh_aggregate_view()
    return R20IngestResponse(batch_id=batch_id, ingested_count=len(rows), status="INGESTED")
