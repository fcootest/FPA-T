"""R20 render service (ISP S3) — returns layout config per role."""
from fastapi import HTTPException
from config.R20_layout_config import LAYOUTS, compute_period_cols


def r20_get_schema(role: str, ff: str = "MF") -> dict:
    role = role.upper()
    if role not in LAYOUTS:
        raise HTTPException(status_code=404, detail=f"unknown role {role}")
    layout = LAYOUTS[role]
    kr_list = sorted({kr for s in layout["sections"] for kr in s["kr_codes"]})
    return {
        "role": role,
        "metadata_fields": layout["metadata_fields"],
        "scenario_blocks": layout["scenario_blocks"],
        "sections": layout["sections"],
        "kr_list": kr_list,
        "period_cols": compute_period_cols(ff),
    }
