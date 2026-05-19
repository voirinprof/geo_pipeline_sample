"""
src/analyze.py — Étape 3 : calculs et statistiques géospatiales.

Responsabilité : produire des métriques à partir des données traitées.
Les résultats enrichissent le GeoDataFrame ou sont retournés séparément.
"""

import logging

import geopandas as gpd
import pandas as pd

log = logging.getLogger(__name__)

# Facteur de conversion m² → km²
M2_TO_KM2 = 1e-6


def compute_area_stats(
    gdf: gpd.GeoDataFrame,
    name_col: str,
) -> tuple[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Calcule la superficie de chaque entité et produit un tableau récapitulatif.

    La projection doit être en mètres (ex: EPSG:32198) pour que
    les superficies soient correctes. Un avertissement est émis sinon.

    Args:
        gdf: GeoDataFrame reprojeté (unités en mètres)
        name_col: colonne contenant le nom des entités

    Returns:
        Tuple (gdf enrichi avec colonne 'aire_km2', DataFrame de statistiques)

    Raises:
        KeyError: si name_col n'existe pas dans le GeoDataFrame
    """
    if name_col not in gdf.columns:
        raise KeyError(f"Colonne '{name_col}' introuvable. Colonnes : {list(gdf.columns)}")

    # Avertissement si la projection n'est pas en mètres
    if gdf.crs and gdf.crs.axis_info[0].unit_name not in ("metre", "meter"):
        log.warning(
            f"  La projection ({gdf.crs.name}) n'est pas en mètres. "
            "Les superficies calculées seront incorrectes !"
        )

    # Calcul des aires
    gdf = gdf.copy()
    gdf["aire_km2"] = (gdf.geometry.area * M2_TO_KM2).round(2)

    # Statistiques descriptives
    stats = (
        gdf[[name_col, "aire_km2"]]
        .sort_values("aire_km2", ascending=False)
        .reset_index(drop=True)
    )

    log.debug(
        f"  Superficie totale : {gdf['aire_km2'].sum():,.0f} km² | "
        f"Moyenne : {gdf['aire_km2'].mean():,.0f} km² | "
        f"Max : {gdf['aire_km2'].max():,.0f} km²"
    )

    return gdf, stats
