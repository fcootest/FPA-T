"""R20 Batch Manager (ISP S7) — batch_id gen, audit, rollback.

AP DD-R20-07: DML-only (no streaming). DELETE works immediately.
"""
import secrets
from datetime import datetime, timezone
from fastapi import HTTPException
from google.cloud import bigquery
from config.settings import settings
from services.R20_bq_client import get_bq_client


AUDIT_TABLE = f"{settings.gcp_project}.{settings.bq_dataset_so_rows}.R20_batch_audit"


def new_batch_id() -> str:
    return "batch_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_") + secrets.token_hex(3)


def log_batch(batch_id: str, role: str, variant: str | None, table_name: str,
              ingested_count: int, user_email: str) -> None:
    sql = f"""
    INSERT INTO `{AUDIT_TABLE}`
    (batch_id, role, variant, table_name, ingested_count, status, user_email, created_at)
    VALUES (@bid, @role, @variant, @table, @cnt, 'INGESTED', @user, CURRENT_TIMESTAMP())
    """
    params = [
        bigquery.ScalarQueryParameter("bid", "STRING", batch_id),
        bigquery.ScalarQueryParameter("role", "STRING", role),
        bigquery.ScalarQueryParameter("variant", "STRING", variant),
        bigquery.ScalarQueryParameter("table", "STRING", table_name),
        bigquery.ScalarQueryParameter("cnt", "INT64", ingested_count),
        bigquery.ScalarQueryParameter("user", "STRING", user_email),
    ]
    get_bq_client().query(sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()


def get_batch_status(batch_id: str) -> dict:
    sql = f"SELECT * FROM `{AUDIT_TABLE}` WHERE batch_id = @bid LIMIT 1"
    params = [bigquery.ScalarQueryParameter("bid", "STRING", batch_id)]
    rows = list(get_bq_client().query(
        sql, job_config=bigquery.QueryJobConfig(query_parameters=params)
    ).result())
    if not rows:
        raise HTTPException(404, detail=f"batch {batch_id} not found")
    r = dict(rows[0])
    # Serialize timestamps
    for k in ("created_at", "rolled_back_at"):
        if r.get(k):
            r[k] = r[k].isoformat()
    return r


def r20_rollback_batch(batch_id: str, user_email: str) -> dict:
    meta = get_batch_status(batch_id)
    if meta["status"] == "ROLLED_BACK":
        raise HTTPException(409, detail=f"batch {batch_id} already rolled back")
    table = meta["table_name"]
    client = get_bq_client()
    # DELETE data rows (DML, strongly consistent — DD-R20-07)
    del_sql = f"DELETE FROM `{table}` WHERE upload_batch_id = @bid"
    params = [bigquery.ScalarQueryParameter("bid", "STRING", batch_id)]
    job = client.query(del_sql, job_config=bigquery.QueryJobConfig(query_parameters=params))
    job.result()
    deleted = job.num_dml_affected_rows or 0
    # Update audit status
    upd_sql = f"""
    UPDATE `{AUDIT_TABLE}`
    SET status = 'ROLLED_BACK', rolled_back_at = CURRENT_TIMESTAMP()
    WHERE batch_id = @bid
    """
    client.query(upd_sql, job_config=bigquery.QueryJobConfig(query_parameters=params)).result()
    return {"batch_id": batch_id, "deleted_count": deleted, "status": "ROLLED_BACK"}
