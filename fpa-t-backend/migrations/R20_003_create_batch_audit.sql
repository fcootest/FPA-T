-- R20 batch audit table (ISP S7) — tracks INGESTED / ROLLED_BACK batches
CREATE TABLE IF NOT EXISTS `fpa-t-494007.so_rows.R20_batch_audit` (
  batch_id STRING NOT NULL,
  role STRING NOT NULL,
  variant STRING,
  table_name STRING NOT NULL,
  ingested_count INT64,
  status STRING NOT NULL,
  user_email STRING NOT NULL,
  created_at TIMESTAMP NOT NULL,
  rolled_back_at TIMESTAMP
)
PARTITION BY DATE(created_at)
CLUSTER BY status, role;
