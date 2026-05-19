"""
tests/test_process.py — Tests unitaires pour les transformations géospatiales.
"""

import geopandas as gpd
import pytest
from shapely.geometry import Point, Polygon

from src.process import clean_geometries, filter_by_region, reproject


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def simple_gdf():
    """GeoDataFrame simple avec 3 polygones valides."""
    polys = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
        Polygon([(2, 2), (3, 2), (3, 3), (2, 3)]),
    ]
    return gpd.GeoDataFrame(
        {"region": ["Estrie", "Montérégie", "Estrie"], "nom": ["A", "B", "C"]},
        geometry=polys,
        crs="EPSG:4326",
    )


@pytest.fixture
def gdf_with_nulls(simple_gdf):
    """GeoDataFrame avec une géométrie nulle."""
    gdf = simple_gdf.copy()
    gdf.loc[1, "geometry"] = None
    return gdf


# ── Tests : clean_geometries ─────────────────────────────────────────────────

def test_clean_removes_null_geometries(gdf_with_nulls):
    result = clean_geometries(gdf_with_nulls)
    assert len(result) == 2
    assert result.geometry.notna().all()


def test_clean_keeps_valid_geometries(simple_gdf):
    result = clean_geometries(simple_gdf)
    assert len(result) == 3


# ── Tests : reproject ────────────────────────────────────────────────────────

def test_reproject_changes_crs(simple_gdf):
    result = reproject(simple_gdf, epsg=32198)
    assert result.crs.to_epsg() == 32198


def test_reproject_invalid_epsg(simple_gdf):
    with pytest.raises(ValueError, match="invalide"):
        reproject(simple_gdf, epsg=-1)


def test_reproject_preserves_count(simple_gdf):
    result = reproject(simple_gdf, epsg=32198)
    assert len(result) == len(simple_gdf)


# ── Tests : filter_by_region ─────────────────────────────────────────────────

def test_filter_returns_matching_rows(simple_gdf):
    result = filter_by_region(simple_gdf, column="region", value="Estrie")
    assert len(result) == 2
    assert (result["region"] == "Estrie").all()


def test_filter_is_case_insensitive(simple_gdf):
    result = filter_by_region(simple_gdf, column="region", value="estrie")
    assert len(result) == 2


def test_filter_raises_on_missing_column(simple_gdf):
    with pytest.raises(KeyError, match="inexistante"):
        filter_by_region(simple_gdf, column="inexistante", value="Estrie")


def test_filter_raises_on_no_match(simple_gdf):
    with pytest.raises(ValueError, match="Laurentides"):
        filter_by_region(simple_gdf, column="region", value="Laurentides")
