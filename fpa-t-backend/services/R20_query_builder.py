"""R20 query builder (ISP S4) — SELECT with scope keys.

Layer 2 V5.2 Query Scope Check: WHERE includes all unique keys.
AP S13 gotcha #1: NaN sanitizer on FLOAT reads.
AP S13 gotcha #6: fully-qualified table path.
"""
from typing import Optional
from fastapi import HTTPException
from google.cloud import bigquery
from models.R20_table_registry import r20_resolve_table_name
from services.R20_bq_client import get_bq_client, sanitize_row


def r20_load(
    role: str,
    variant: Optional[str] = None,
    zblock_string: Optional[str] = None,
    run: Optional[str] = None,
    scenario: Optional[str] = None,
) -> list[dict]:
    try:
        table = r20_resolve_table_name(role, variant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    where_clauses = []
    params: list[bigquery.ScalarQueryParameter] = []
    if zblock_string:
        where_clauses.append("zblock_string = @zblock")
        params.append(bigquery.ScalarQueryParameter("zblock", "STRING", zblock_string))
    if scenario:
        where_clauses.append("scenario = @scenario")
        params.append(bigquery.ScalarQueryParameter("scenario", "STRING", scenario))
    # Note: `run` has no dedicated column; encoded in zblock_string. Reserved for future.

    sql = f"SELECT * FROM `{table}`"
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    client = get_bq_client()
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    rows = list(client.query(sql, job_config=job_config).result())
    return [sanitize_row(dict(r)) for r in rows]
