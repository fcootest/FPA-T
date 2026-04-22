"""Per-role → BQ table resolver (ISP S6, AP DD-R20-02).

Fully-qualified paths (AP S13 gotcha #6).
"""
from config.settings import settings


FIXED_ROLES = {"GH", "HQ", "TECH"}
VARIANT_ROLES = {"COH", "CEH", "DH"}


def r20_resolve_table_name(role: str, variant: str | None = None) -> str:
    """Return fully-qualified BQ table name for a given role.

    GH/HQ/TECH: variant must be None.
    COH: variant = venture code (TER/VIS/SMI/AST/SAP).
    CEH: variant = "{V}_{C}" e.g. "TER_MAR".
    DH:  variant = "{V}_{T}" e.g. "TER_TeamA".
    """
    role = role.upper()
    dataset = f"{settings.gcp_project}.{settings.bq_dataset_so_rows}"
    if role in FIXED_ROLES:
        if variant:
            raise ValueError(f"role {role} does not accept variant")
        return f"{dataset}.R20_{role}"
    if role not in VARIANT_ROLES:
        raise ValueError(f"unknown role {role}")
    if not variant:
        raise ValueError(f"role {role} requires variant")
    return f"{dataset}.R20_{role}_{variant.upper()}"
