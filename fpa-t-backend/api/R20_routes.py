"""R20 API routes (ISP S2-S8 fully wired)."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from models.R20_record_model import R20RecordModel, R20ValidationResult, R20IngestResponse
from services.auth_service import UserContext, get_current_user
from services.R20_render_service import r20_get_schema
from services.R20_query_builder import r20_load
from services.R20_validation_service import r20_validate
from services.R20_ingest_service import r20_ingest_submit
from services.R20_batch_manager import get_batch_status, r20_rollback_batch
from services.R20_aggregate_service import r20_refresh_aggregate_view


router = APIRouter(prefix="/api/fpa-t/r20", tags=["R20"])


@router.get("/schema/{role}")
async def get_schema(role: str, ff: str = Query(default="MF")):
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
    return r20_load(role=role, variant=variant, zblock_string=zblock_string, run=run, scenario=scenario)


@router.post("/{role}/save-draft")
async def post_save_draft(role: str):
    # MVP: draft stored in FE localStorage (S10). Future V1.1: persist BE-side.
    raise HTTPException(501, detail="draft stored in FE localStorage (S10 MVP)")


@router.post("/{role}/submit")
async def post_submit(
    role: str,
    records: list[R20RecordModel],
    variant: Optional[str] = Query(default=None),
    user: UserContext = Depends(get_current_user),
) -> R20IngestResponse:
    return r20_ingest_submit(role=role, records=records, user_email=user.email, variant=variant)


@router.post("/{role}/validate")
async def post_validate(role: str, records: list[R20RecordModel]) -> R20ValidationResult:
    return r20_validate(role, records)


@router.get("/batch/{batch_id}")
async def get_batch(batch_id: str):
    return get_batch_status(batch_id)


@router.post("/rollback/{batch_id}")
async def post_rollback(
    batch_id: str,
    user: UserContext = Depends(get_current_user),
):
    return r20_rollback_batch(batch_id, user.email)


@router.post("/refresh-view")
async def post_refresh_view():
    return r20_refresh_aggregate_view()
