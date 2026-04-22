"""R20Record Pydantic model (ISP S2, AP S1.3).

DD-R20-09: extra="forbid" — no silent field drop.
DD-R20-10: optional strings = None, never empty string.
"""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


IOType = Literal["I", "O"]
ScenarioType = Literal["OPT", "REAL", "PESS"]
R20Role = Literal["GH", "HQ", "TECH", "COH", "CEH", "DH"]


class R20RecordModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_id: Optional[str] = None
    so_row_id: str
    session_id: Optional[str] = None
    plan_type: Optional[str] = None
    zblock_string: Optional[str] = None
    io: IOType
    kr_type: Optional[str] = None
    kr1: Optional[str] = None
    kr2: Optional[str] = None
    kr3: Optional[str] = None
    kr4: Optional[str] = None
    kr5: Optional[str] = None
    kr6: Optional[str] = None
    kr7: Optional[str] = None
    kr8: Optional[str] = None
    kr_code: Optional[str] = None
    kr_name: Optional[str] = None
    cdt1: Optional[str] = None
    cdt2: Optional[str] = None
    cdt3: Optional[str] = None
    cdt4: Optional[str] = None
    pt1: Optional[str] = None
    pt2: Optional[str] = None
    du: Optional[str] = None
    pt1_prev: Optional[str] = None
    pt2_prev: Optional[str] = None
    du_prev: Optional[str] = None
    own_type: Optional[str] = None
    fu1_code: Optional[str] = None
    fu2_code: Optional[str] = None
    egt1: Optional[str] = None
    egt2: Optional[str] = None
    egt3: Optional[str] = None
    egt4: Optional[str] = None
    egt5: Optional[str] = None
    hr1: Optional[str] = None
    hr2: Optional[str] = None
    hr3: Optional[str] = None
    sec: Optional[str] = None
    le1: Optional[str] = None
    le2: Optional[str] = None
    period: str = Field(pattern=r"^(M\d{4}|Q\d{4}|Y\d{2}|W\d{4}|D\d{6}|H\d{8})$")
    value: float
    scenario: ScenarioType
    role_source: str
    ppr_file_id: str
    track_variant: str
    alloc_znumber: Optional[str] = None
    forecast_frequency: Optional[str] = None
    noem_grade: Optional[str] = None
    upload_batch_id: str = ""  # server-generated on submit
    created_by: str
    created_at: datetime


class R20ValidationError(BaseModel):
    code: str
    message: str
    ref_so_row_ids: list[str] = []


class R20ValidationResult(BaseModel):
    valid: bool
    errors: list[R20ValidationError] = []


class R20IngestResponse(BaseModel):
    batch_id: Optional[str]
    ingested_count: int
    status: Literal["INGESTED", "FAILED", "SKIPPED"]
