"""
tests/test_analyze.py — Tests unitaires pour les calculs statistiques.
"""

import geopandas as gpd
import pytest
from shapely.geometry import box

from src.analyze import compute_area_stats


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def projected_gdf():
    """
    GeoDataFrame avec des polygones en EPSG:32198 (mètres).
    Chaque carré fait 1000m × 1000m = 1 km².
    """
    polys = [
        box(0, 0, 1000, 1000),        # 1 km²
        box(2000, 0, 4000, 1000),     # 2 km²
        box(5000, 0, 8000, 1000),     # 3 km²
    ]
    return gpd.GeoDataFrame(
        {"nom": ["Zone A", "Zone B", "Zone C"]},
        geometry=polys,
        crs="EPSG:32198",
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_area_column_created(projected_gdf):
    """La colonne aire_km2 doit être ajoutée au GeoDataFrame."""
    result_gdf, _ = compute_area_stats(projected_gdf, name_col="nom")
    assert "aire_km2" in result_gdf.columns


def test_area_values_correct(projected_gdf):
    """Les superficies calculées doivent correspondre aux polygones."""
    result_gdf, _ = compute_area_stats(projected_gdf, name_col="nom")
    areas = sorted(result_gdf["aire_km2"].tolist())
    assert areas == pytest.approx([1.0, 2.0, 3.0], rel=1e-3)


def test_stats_sorted_descending(projected_gdf):
    """Le tableau de stats doit être trié par superficie décroissante."""
    _, stats = compute_area_stats(projected_gdf, name_col="nom")
    areas = stats["aire_km2"].tolist()
    assert areas == sorted(areas, reverse=True)


def test_missing_name_column_raises(projected_gdf):
    """Une colonne inexistante doit lever une KeyError."""
    with pytest.raises(KeyError):
        compute_area_stats(projected_gdf, name_col="colonne_inexistante")


def test_stats_contains_all_rows(projected_gdf):
    """Le tableau de stats doit contenir autant de lignes que le GeoDataFrame."""
    _, stats = compute_area_stats(projected_gdf, name_col="nom")
    assert len(stats) == len(projected_gdf)
