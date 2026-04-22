"""R20 Aggregate Service (ISP S8) — refresh so_rows_ppr_view dynamically."""
from datetime import datetime, timezone
from config.settings import settings
from services.R20_bq_client import get_bq_client


VIEW_NAME = f"{settings.gcp_project}.{settings.bq_dataset_so_rows}.so_rows_ppr_view"


def _list_r20_tables() -> list[str]:
    client = get_bq_client()
    tables = client.list_tables(f"{settings.gcp_project}.{settings.bq_dataset_so_rows}")
    return sorted(
        t.table_id for t in tables
        if t.table_id.startswith("R20_") and t.table_id != "R20_batch_audit"
    )


def r20_refresh_aggregate_view() -> dict:
    tables = _list_r20_tables()
    if not tables:
        # Edge case: create trivial view with empty result but valid schema
        ddl = (
            f"CREATE OR REPLACE VIEW `{VIEW_NAME}` AS "
            f"SELECT *, CAST(NULL AS STRING) AS source_table "
            f"FROM `{settings.gcp_project}.{settings.bq_dataset_so_rows}.R20_GH` WHERE 1=0"
        )
    else:
        parts = [
            f"SELECT *, '{t}' AS source_table "
            f"FROM `{settings.gcp_project}.{settings.bq_dataset_so_rows}.{t}`"
            for t in tables
        ]
        ddl = f"CREATE OR REPLACE VIEW `{VIEW_NAME}` AS\n" + "\nUNION ALL\n".join(parts)
    get_bq_client().query(ddl).result()
    return {
        "refreshed_at": datetime.now(timezone.utc).isoformat(),
        "source_tables": tables,
    }
