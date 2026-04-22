from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from models.R20_record_model import R20RecordModel


def _valid_record(**overrides):
    base = dict(
        so_row_id="x", io="I", period="M2601", value=1.0,
        scenario="OPT", role_source="GH",
        ppr_file_id="FPA-T", track_variant="IAA",
        created_by="u", created_at=datetime.now(timezone.utc),
    )
    base.update(overrides)
    return base


def test_happy_path_valid():
    m = R20RecordModel(**_valid_record())
    assert m.io == "I"
    assert m.kr2 is None  # default None, not ""


def test_extra_field_rejected():
    with pytest.raises(ValidationError):
        R20RecordModel(**_valid_record(), UNKNOWN_FIELD="x")


def test_invalid_scenario_rejected():
    with pytest.raises(ValidationError):
        R20RecordModel(**_valid_record(scenario="MAYBE"))


def test_invalid_io_rejected():
    with pytest.raises(ValidationError):
        R20RecordModel(**_valid_record(io="X"))


def test_invalid_period_rejected():
    with pytest.raises(ValidationError):
        R20RecordModel(**_valid_record(period="JAN26"))


def test_null_convention_defaults():
    m = R20RecordModel(**_valid_record())
    # Optional strings default to None (DD-R20-10)
    for f in ["kr2", "cdt2", "pt1", "fu1_code", "egt1", "hr1", "sec"]:
        assert getattr(m, f) is None, f"{f} should default to None"
