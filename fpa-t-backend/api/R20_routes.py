"""R20 API routes (ISP S2 scaffold + S3 schema + S4 load)."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from models.R20_record_model import R20ValidationResult, R20IngestResponse, R20RecordModel
from services.auth_service import UserContext, get_current_user
from services.R20_render_service import r20_get_schema
from services.R20_query_builder import r20_load


router = APIRouter(prefix="/api/fpa-t/r20", tags=["R20"])


@router.get("/schema/{role}")
async def get_schema(role: str, ff: str = Query(default="MF")):
    """S3 — layout config per role."""
    return r20_get_schema(role, ff=ff)


@router.get("/{role}/load")
async def get_load(
    role: str,
    zblock_string: str = Query(...),
    run: Optional[str] = Query(default=None),
    scenario: Optional[str] = Query(default=None),
    variant: Optional[str] = Query(default=None),
    user: UserContext = Depends(get_current_user),
) -> list[dict]:
    """S4 — load existing records by scope."""
    return r20_load(role=role, variant=variant, zblock_string=zblock_string, run=run, scenario=scenario)


@router.post("/{role}/save-draft")
async def post_save_draft(role: str):
    raise HTTPException(501, detail="not implemented (S10 FE-side localStorage MVP)")


@router.post("/{role}/submit")
async def post_submit(role: str, variant: Optional[str] = Query(default=None)):
    raise HTTPException(501, detail="not implemented (Wave 4 S6)")


@router.post("/{role}/validate")
async def post_validate(role: str):
    raise HTTPException(501, detail="not implemented (Wave 3 S5)")


@router.get("/batch/{batch_id}")
async def get_batch(batch_id: str):
    raise HTTPException(501, detail="not implemented (Wave 4 S7)")


@router.post("/rollback/{batch_id}")
async def post_rollback(batch_id: str):
    raise HTTPException(501, detail="not implemented (Wave 4 S7)")


@router.post("/refresh-view")
async def post_refresh_view():
    raise HTTPException(501, detail="not implemented (Wave 4 S8)")
