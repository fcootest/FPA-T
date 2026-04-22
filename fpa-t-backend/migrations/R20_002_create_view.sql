-- R20 aggregate view (ISP S1 / S8)
-- Idempotent: CREATE OR REPLACE VIEW
-- Rebuilt dynamically by R20_aggregate_service.r20_refresh_aggregate_view()
-- This static DDL covers initial fixed set; service regenerates as new tables added.

CREATE OR REPLACE VIEW `fpa-t-494007.so_rows.so_rows_ppr_view` AS
SELECT *, 'R20_GH' AS source_table FROM `fpa-t-494007.so_rows.R20_GH`
UNION ALL SELECT *, 'R20_HQ' FROM `fpa-t-494007.so_rows.R20_HQ`
UNION ALL SELECT *, 'R20_TECH' FROM `fpa-t-494007.so_rows.R20_TECH`
UNION ALL SELECT *, 'R20_COH_TER' FROM `fpa-t-494007.so_rows.R20_COH_TER`
UNION ALL SELECT *, 'R20_COH_VIS' FROM `fpa-t-494007.so_rows.R20_COH_VIS`
UNION ALL SELECT *, 'R20_COH_SMI' FROM `fpa-t-494007.so_rows.R20_COH_SMI`
UNION ALL SELECT *, 'R20_COH_AST' FROM `fpa-t-494007.so_rows.R20_COH_AST`
UNION ALL SELECT *, 'R20_COH_SAP' FROM `fpa-t-494007.so_rows.R20_COH_SAP`
UNION ALL SELECT *, 'R20_CEH_TER_MAR' FROM `fpa-t-494007.so_rows.R20_CEH_TER_MAR`
UNION ALL SELECT *, 'R20_CEH_TER_DEV' FROM `fpa-t-494007.so_rows.R20_CEH_TER_DEV`
UNION ALL SELECT *, 'R20_CEH_TER_TECH' FROM `fpa-t-494007.so_rows.R20_CEH_TER_TECH`
UNION ALL SELECT *, 'R20_CEH_VIS_MAR' FROM `fpa-t-494007.so_rows.R20_CEH_VIS_MAR`
UNION ALL SELECT *, 'R20_CEH_VIS_DEV' FROM `fpa-t-494007.so_rows.R20_CEH_VIS_DEV`
UNION ALL SELECT *, 'R20_CEH_SMI_MAR' FROM `fpa-t-494007.so_rows.R20_CEH_SMI_MAR`
UNION ALL SELECT *, 'R20_CEH_SMI_DEV' FROM `fpa-t-494007.so_rows.R20_CEH_SMI_DEV`
UNION ALL SELECT *, 'R20_CEH_AST_MAR' FROM `fpa-t-494007.so_rows.R20_CEH_AST_MAR`;
