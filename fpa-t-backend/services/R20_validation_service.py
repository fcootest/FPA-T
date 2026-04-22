"""R20 Validation Service (ISP S5, AP S5.1-5.4).

4 invariants:
  1. R20↔R100 sum rule (tolerance 0.01 absolute)
  2. Rate Alloc PL2 sum = 100% per ZBlock (GH only)
  3. NOEM sourcing contract (HQ/TECH/COH only)
  4. GH Mode A/B over-determined check

V5.6 Match Strategy audit: PL2 filter uses kr1 check (not endswith/contains)
to avoid RATE-PL2 contamination (rate rows 0-100 vs monetary PL2 thousands).
"""
from collections import defaultdict
from typing import Iterable
from models.R20_record_model import R20RecordModel, R20ValidationError, R20ValidationResult


TOLERANCE = 0.01  # absolute, AP DD-R20-11


def _is_r20_row(r: R20RecordModel) -> bool:
    """R20 row: aggregate level (cdt2/cdt3/cdt4 all NULL)."""
    return all(getattr(r, f) is None for f in ("cdt2", "cdt3", "cdt4"))


def _is_r100_row(r: R20RecordModel) -> bool:
    """R100 row: detail level (any of cdt2/cdt3/cdt4 non-NULL)."""
    return any(getattr(r, f) is not None for f in ("cdt2", "cdt3", "cdt4"))


def _is_monetary_pl2(r: R20RecordModel) -> bool:
    """Match strategy: kr1='PRM' AND kr_code endswith '-PL2'. Excludes RATE-* rows."""
    return r.kr1 == "PRM" and (r.kr_code or "").endswith("-PL2")


def r20_validate_sum_rule(records: list[R20RecordModel]) -> list[R20ValidationError]:
    """Rule 1: SUM(R100 per cdt1/period/pt) = R20 per cdt1/period/pt."""
    errors: list[R20ValidationError] = []
    r20s = [r for r in records if _is_r20_row(r) and _is_monetary_pl2(r)]
    r100s = [r for r in records if _is_r100_row(r) and _is_monetary_pl2(r)]
    for r20 in r20s:
        key = (r20.kr_code, r20.cdt1, r20.period, r20.pt1, r20.pt2)
        total = sum(
            r.value for r in r100s
            if (r.kr_code, r.cdt1, r.period, r.pt1, r.pt2) == key
        )
        if total > 0 and abs(total - r20.value) > TOLERANCE:
            errors.append(R20ValidationError(
                code="r20_r100_mismatch",
                message=f"R20↔R100 mismatch at {key}: R20={r20.value} R100_sum={total}",
                ref_so_row_ids=[r20.so_row_id],
            ))
    return errors


def r20_validate_rate_alloc(records: list[R20RecordModel]) -> list[R20ValidationError]:
    """Rule 2: SUM(RATE-PRM-PL2-ALLOCATE per ZBlock) = 100.00% (tolerance 0.01)."""
    errors: list[R20ValidationError] = []
    alloc_rows = [r for r in records if r.kr_code == "RATE-PRM-PL2-ALLOCATE"]
    groups: dict[tuple, list[R20RecordModel]] = defaultdict(list)
    for r in alloc_rows:
        groups[(r.zblock_string, r.period, r.scenario)].append(r)
    for key, rows in groups.items():
        total = sum(r.value for r in rows)
        if abs(total - 100.0) > TOLERANCE:
            errors.append(R20ValidationError(
                code="rate_sum_violation",
                message=f"Rate Alloc PL2 sum = {total:.4f}% ≠ 100% at {key}",
                ref_so_row_ids=[r.so_row_id for r in rows],
            ))
    return errors


def r20_validate_noem_contract(role: str, records: list[R20RecordModel]) -> list[R20ValidationError]:
    """Rule 3: NOEM input only at HQ/TECH/COH. GH/CEH/DH submitting NOEM → REJECT."""
    errors: list[R20ValidationError] = []
    role_upper = role.upper()
    # Accept either exact role or role-with-variant prefix (e.g. "COH-TER", "CEH-TER-MAR")
    role_base = role_upper.split("-")[0]
    forbidden = {"GH", "CEH", "DH"}
    if role_base in forbidden:
        noem_rows = [r for r in records if r.kr1 == "NOEM"]
        if noem_rows:
            errors.append(R20ValidationError(
                code="noem_contract_violation",
                message=f"Role {role_base} cannot submit NOEM (AP S5.3)",
                ref_so_row_ids=[r.so_row_id for r in noem_rows],
            ))
    return errors


def _is_rate_pl2_per_gi(r: R20RecordModel) -> bool:
    return r.kr_code == "RATE-PRM-PL2-PER-GI"


def _is_gi(r: R20RecordModel) -> bool:
    return r.kr1 == "GI"


def r20_validate_mode(records: list[R20RecordModel]) -> list[R20ValidationError]:
    """Rule 4 (GH only): Mode A (GI+PL2) xor Mode B (PL2+Rate). Over-determined → REJECT."""
    errors: list[R20ValidationError] = []
    groups: dict[tuple, dict[str, list[R20RecordModel]]] = defaultdict(
        lambda: {"gi": [], "pl2": [], "rate": []}
    )
    for r in records:
        key = (r.zblock_string, r.cdt1, r.period, r.scenario)
        if _is_gi(r):
            groups[key]["gi"].append(r)
        elif _is_monetary_pl2(r):
            groups[key]["pl2"].append(r)
        elif _is_rate_pl2_per_gi(r):
            groups[key]["rate"].append(r)
    for key, g in groups.items():
        has = {k: bool(v) for k, v in g.items()}
        count = sum(has.values())
        if count == 3:
            errors.append(R20ValidationError(
                code="mode_over_determined",
                message=f"GH Mode: GI+PL2+Rate all present at {key} — choose Mode A or B",
                ref_so_row_ids=[r.so_row_id for r in g["gi"] + g["pl2"] + g["rate"]],
            ))
        elif count < 2 and count > 0:
            errors.append(R20ValidationError(
                code="mode_under_specified",
                message=f"GH Mode: need 2 of (GI, PL2, Rate) at {key}, only {count} present",
                ref_so_row_ids=[r.so_row_id for r in g["gi"] + g["pl2"] + g["rate"]],
            ))
    return errors


def r20_validate(role: str, records: Iterable[R20RecordModel]) -> R20ValidationResult:
    """Run all 4 rules. Returns accumulated errors."""
    records = list(records)
    errors: list[R20ValidationError] = []
    errors.extend(r20_validate_sum_rule(records))
    errors.extend(r20_validate_noem_contract(role, records))
    role_base = role.upper().split("-")[0]
    if role_base == "GH":
        errors.extend(r20_validate_rate_alloc(records))
        errors.extend(r20_validate_mode(records))
    return R20ValidationResult(valid=not errors, errors=errors)
