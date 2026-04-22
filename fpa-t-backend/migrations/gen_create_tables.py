"""Generate CREATE TABLE IF NOT EXISTS DDL for all R20_* tables (ISP S1).

Output written to R20_001_create_tables.sql. Re-run to regenerate.
"""
from pathlib import Path

PROJECT = "fpa-t-494007"
DATASET = "so_rows"

SCHEMA = """(
  input_id STRING,
  so_row_id STRING NOT NULL,
  session_id STRING,
  plan_type STRING,
  zblock_string STRING,
  io STRING NOT NULL,
  kr_type STRING,
  kr1 STRING, kr2 STRING, kr3 STRING, kr4 STRING,
  kr5 STRING, kr6 STRING, kr7 STRING, kr8 STRING,
  kr_code STRING, kr_name STRING,
  cdt1 STRING, cdt2 STRING, cdt3 STRING, cdt4 STRING,
  pt1 STRING, pt2 STRING, du STRING,
  pt1_prev STRING, pt2_prev STRING, du_prev STRING,
  own_type STRING,
  fu1_code STRING, fu2_code STRING,
  egt1 STRING, egt2 STRING, egt3 STRING, egt4 STRING, egt5 STRING,
  hr1 STRING, hr2 STRING, hr3 STRING,
  sec STRING, le1 STRING, le2 STRING,
  period STRING NOT NULL,
  value FLOAT64 NOT NULL,
  scenario STRING NOT NULL,
  role_source STRING NOT NULL,
  ppr_file_id STRING NOT NULL,
  track_variant STRING NOT NULL,
  alloc_znumber STRING,
  forecast_frequency STRING,
  noem_grade STRING,
  upload_batch_id STRING NOT NULL,
  created_by STRING NOT NULL,
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY scenario, role_source, upload_batch_id"""

TABLES = (
    ["GH", "HQ", "TECH"]
    + [f"COH_{v}" for v in ("TER", "VIS", "SMI", "AST", "SAP")]
    + [
        "CEH_TER_MAR", "CEH_TER_DEV", "CEH_TER_TECH",
        "CEH_VIS_MAR", "CEH_VIS_DEV",
        "CEH_SMI_MAR", "CEH_SMI_DEV",
        "CEH_AST_MAR",
    ]
)


def gen() -> str:
    header = (
        "-- R20 per-role tables migration (generated from gen_create_tables.py)\n"
        "-- Idempotent: CREATE TABLE IF NOT EXISTS. DO NOT edit by hand.\n\n"
    )
    stmts = [f"CREATE TABLE IF NOT EXISTS `{PROJECT}.{DATASET}.R20_{t}` {SCHEMA};" for t in TABLES]
    return header + "\n\n".join(stmts) + "\n"


if __name__ == "__main__":
    out = Path(__file__).parent / "R20_001_create_tables.sql"
    out.write_text(gen(), encoding="utf-8")
    print(f"Wrote {out} ({len(TABLES)} tables)")
