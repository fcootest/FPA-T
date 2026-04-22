"""R20 layout config per role (ISP S3, AP S3.3)."""
from typing import TypedDict, Literal


class R20Section(TypedDict):
    id: str
    title: str
    row_type: Literal["I", "O"]
    kr_codes: list[str]
    breakdown: list[str]
    unit: Literal["bVND", "mVND", "%", "person", "USD"]


class R20Layout(TypedDict):
    role: str
    metadata_fields: list[str]
    scenario_blocks: list[str]
    sections: list[R20Section]


_METADATA = [
    "io", "zblock1", "zblock2", "kr", "cdt", "pt_now", "pt_prev",
    "pt_fix", "pt_sub", "funnel", "employee", "hr", "sec", "period",
    "le", "unit", "tdbu",
]
_SCENARIOS = ["OPT", "REAL", "PESS", "ACTUAL", "DELTA"]


LAYOUTS: dict[str, R20Layout] = {
    "GH": {
        "role": "GH", "metadata_fields": _METADATA, "scenario_blocks": _SCENARIOS,
        "sections": [
            {"id": "r20_mix", "title": "102. R20-Mix (target input)",
             "row_type": "I", "unit": "mVND",
             "kr_codes": ["PRM-BHR-AOMC-PL2", "RATE-PRM-PL2-PER-GI", "RATE-PRM-PL2-ALLOCATE"],
             "breakdown": ["cdt1"]},
            {"id": "pl_tang", "title": "Các tầng PL (computed)",
             "row_type": "O", "unit": "bVND",
             "kr_codes": ["GI", "PRM-BHR-AOMC-PL2", "PL3", "PL4", "PL5", "PL6", "PL7", "PL8"],
             "breakdown": ["cdt1"]},
            {"id": "nhom_chi_so", "title": "Nhóm chỉ số chính (NHRC flag)",
             "row_type": "O", "unit": "bVND",
             "kr_codes": ["CAC", "COS", "GAC", "CPX", "ITX", "OTH"],
             "breakdown": ["cdt1"]},
            {"id": "chi_so_cau_thanh", "title": "Chỉ số cấu thành PL",
             "row_type": "O", "unit": "bVND",
             "kr_codes": ["OMC", "TESE", "PPS", "COMP"],
             "breakdown": ["cdt1"]},
            {"id": "r100_noem", "title": "103. R100 — NOEM + HR",
             "row_type": "I", "unit": "person",
             "kr_codes": ["NOEM", "BAC-OTH-COMP-HRC-SAL", "BAC-OTH-COMP-HRC-BON",
                          "BAC-OTH-COMP-HRC-INS", "BAC-OTH-COMP-HRC-PIT"],
             "breakdown": ["cdt1", "cdt2", "egt1", "hr1", "hr2"]},
        ],
    },
    "HQ": {
        "role": "HQ", "metadata_fields": _METADATA, "scenario_blocks": _SCENARIOS,
        "sections": [
            {"id": "hq_cost", "title": "HQ Cost Input", "row_type": "I", "unit": "bVND",
             "kr_codes": [
                 "BAC-OPX-GAC-FAC", "BAC-OPX-GAC-MGM", "BAC-OPX-GAC-DEV", "BAC-OPX-GAC-OTH",
                 "BAC-CPX-PAR", "BAC-CPX-INF", "BAC-CPX-BIZ", "BAC-CPX-DEV",
                 "BAC-ITX-INT", "BAC-ITX-TAX", "BAC-ITX-OTH",
                 "BAC-OTH-OTH-OTH", "MAC-OTH",
                 "BAC-OPX-COS-OPS-DEV", "BAC-OPX-COS-OPS-TESE-OTH",
             ],
             "breakdown": ["cdt1", "cdt2"]},
            {"id": "hq_noem", "title": "NOEM (66 rows: HQ1/HQ2/MGM × CDT2 × EGT1)",
             "row_type": "I", "unit": "person", "kr_codes": ["NOEM"],
             "breakdown": ["cdt1", "cdt2", "egt1"]},
            {"id": "hq_cpem", "title": "CPEM global", "row_type": "I", "unit": "mVND",
             "kr_codes": ["CPEM-SAL", "CPEM-CUL", "CPEM-REC", "CPEM-BON", "CPEM-INS", "CPEM-FAC"],
             "breakdown": []},
            {"id": "hq_rate", "title": "RATE-BON-* + RATE-PIT-SAL", "row_type": "I", "unit": "%",
             "kr_codes": ["RATE-BON-SAL", "RATE-BON-GI", "RATE-BON-PL2", "RATE-BON-PL3",
                          "RATE-BON-PL7", "RATE-PIT-SAL"],
             "breakdown": ["cdt1"]},
        ],
    },
    "TECH": {
        "role": "TECH", "metadata_fields": _METADATA, "scenario_blocks": _SCENARIOS,
        "sections": [
            {"id": "tech_cos_ops", "title": "COS-OPS-TESE + DEV", "row_type": "I", "unit": "bVND",
             "kr_codes": ["BAC-OPX-COS-OPS-TESE-API", "BAC-OPX-COS-OPS-TESE-SERV",
                          "BAC-OPX-COS-OPS-TESE-LIC", "BAC-OPX-COS-OPS-TESE-OTH",
                          "BAC-OPX-COS-OPS-DEV"],
             "breakdown": ["cdt1"]},
        ],
    },
    "COH": {
        "role": "COH", "metadata_fields": _METADATA, "scenario_blocks": _SCENARIOS,
        "sections": [
            {"id": "coh_target", "title": "COH Rate Target", "row_type": "I", "unit": "%",
             "kr_codes": ["RATE-PRM-PL2-ALLOCATE", "RATE-PRM-PL2-PER-GI", "RATE-COS-PPS-PER-PL3"],
             "breakdown": ["cdt1", "cdt2"]},
            {"id": "coh_gi_pl2", "title": "GI, PL2 Total + by Team (CDT3)",
             "row_type": "O", "unit": "bVND",
             "kr_codes": ["GI", "PRM-BHR-AOMC-PL2"],
             "breakdown": ["cdt1", "cdt3"]},
            {"id": "coh_nhom", "title": "Nhóm chỉ số chính", "row_type": "O", "unit": "bVND",
             "kr_codes": ["CAC", "COS", "GAC", "CPX", "ITX", "OTH"], "breakdown": ["cdt1"]},
            {"id": "coh_cau_thanh", "title": "Chỉ số cấu thành PL",
             "row_type": "O", "unit": "bVND",
             "kr_codes": ["OMC", "TESE", "PPS", "COMP"], "breakdown": ["cdt1"]},
            {"id": "coh_noem", "title": "NOEM venture × DEV/MAR/TECH × EGT1",
             "row_type": "I", "unit": "person", "kr_codes": ["NOEM"],
             "breakdown": ["cdt1", "cdt2", "egt1"]},
            {"id": "coh_comp", "title": "BAC-OTH-COMP by CDT2", "row_type": "I", "unit": "mVND",
             "kr_codes": ["BAC-OTH-COMP-HRC-SAL", "BAC-OTH-COMP-HRC-BON",
                          "BAC-OTH-COMP-HRC-INS", "BAC-OTH-COMP-HRC-PIT"],
             "breakdown": ["cdt1", "cdt2"]},
        ],
    },
    "CEH": {
        "role": "CEH", "metadata_fields": _METADATA, "scenario_blocks": _SCENARIOS,
        "sections": [
            {"id": "ceh_cac_cos_gac", "title": "CAC / COS / GAC per CDT1×CDT2",
             "row_type": "I", "unit": "bVND", "kr_codes": ["CAC", "COS", "GAC"],
             "breakdown": ["cdt1", "cdt2"]},
            {"id": "ceh_pl3", "title": "PL3 per center", "row_type": "O", "unit": "bVND",
             "kr_codes": ["PL3"], "breakdown": ["cdt1", "cdt2"]},
        ],
    },
    "DH": {
        "role": "DH", "metadata_fields": _METADATA, "scenario_blocks": _SCENARIOS,
        "sections": [
            {"id": "dh_team_cost", "title": "OMC / CAC per team (CDT3)",
             "row_type": "I", "unit": "bVND", "kr_codes": ["OMC", "CAC"],
             "breakdown": ["cdt1", "cdt3"]},
            {"id": "dh_noem", "title": "NOEM per team", "row_type": "I", "unit": "person",
             "kr_codes": ["NOEM"], "breakdown": ["cdt1", "cdt3", "egt1"]},
            {"id": "dh_r100", "title": "R100 Marketer × Product", "row_type": "I", "unit": "mVND",
             "kr_codes": ["GI", "PRM-BHR-AOMC-PL2"],
             "breakdown": ["cdt3", "cdt4", "pt2"]},
        ],
    },
}


def compute_period_cols(ff: str, plan_year: str = "26") -> list[str]:
    """AP S5.5 — period col count per Forecast Frequency."""
    ff = ff.upper()
    if ff == "YF":
        return [f"Y{plan_year}"]
    if ff == "QF":
        return [f"Q{plan_year}{q:02d}" for q in range(1, 5)]
    if ff == "MF":
        return [f"M{plan_year}{m:02d}" for m in range(1, 13)]
    if ff == "WF":
        return [f"W{plan_year}{w:02d}" for w in range(1, 53)]
    raise ValueError(f"unsupported FF={ff}")
