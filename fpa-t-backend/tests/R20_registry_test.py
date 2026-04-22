import pytest
from models.R20_table_registry import r20_resolve_table_name


def test_gh_no_variant():
    assert r20_resolve_table_name("GH").endswith(".so_rows.R20_GH")


def test_hq_no_variant():
    assert r20_resolve_table_name("HQ").endswith(".so_rows.R20_HQ")


def test_coh_with_variant():
    assert r20_resolve_table_name("COH", "TER").endswith(".so_rows.R20_COH_TER")


def test_ceh_with_compound_variant():
    assert r20_resolve_table_name("CEH", "TER_MAR").endswith(".so_rows.R20_CEH_TER_MAR")


def test_dh_with_variant():
    assert r20_resolve_table_name("DH", "TER_TeamA").endswith(".so_rows.R20_DH_TER_TEAMA")


def test_gh_rejects_variant():
    with pytest.raises(ValueError, match="does not accept variant"):
        r20_resolve_table_name("GH", "TER")


def test_coh_requires_variant():
    with pytest.raises(ValueError, match="requires variant"):
        r20_resolve_table_name("COH")


def test_unknown_role():
    with pytest.raises(ValueError, match="unknown role"):
        r20_resolve_table_name("XYZ")


def test_role_normalized_uppercase():
    assert r20_resolve_table_name("gh") == r20_resolve_table_name("GH")
