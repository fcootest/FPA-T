"""Shared BQ client singleton + NaN sanitizer (ISP S2, AP S13 gotcha #1)."""
import math
from functools import lru_cache
from google.cloud import bigquery
from config.settings import settings


@lru_cache(maxsize=1)
def get_bq_client() -> bigquery.Client:
    return bigquery.Client(project=settings.gcp_project)


def sanitize_float(x):
    """Convert NaN/Inf → None (AP S13 row 1)."""
    if x is None:
        return None
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return None
    return x


def sanitize_row(row: dict) -> dict:
    """Apply NaN sanitizer to all float fields in a row dict."""
    return {k: sanitize_float(v) if isinstance(v, float) else v for k, v in row.items()}
