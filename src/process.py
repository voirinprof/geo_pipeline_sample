"""
src/process.py — Étape 2 : transformations géospatiales.

Responsabilité : nettoyer, reprojeter, filtrer les données.
Chaque fonction fait une seule chose et retourne un nouveau GeoDataFrame.
"""

import logging

import geopandas as gpd

log = logging.getLogger(__name__)


def clean_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Supprime les lignes avec géométries nulles ou invalides.

    Args:
        gdf: GeoDataFrame brut

    Returns:
        GeoDataFrame nettoyé
    """
    initial_count = len(gdf)

    # Supprimer les géométries nulles
    gdf = gdf[gdf.geometry.notna()].copy()

    # Corriger les géométries invalides (self-intersections, etc.)
    invalid_mask = ~gdf.geometry.is_valid
    if invalid_mask.any():
        log.warning(f"  {invalid_mask.sum()} géométries invalides corrigées avec buffer(0)")
        gdf.loc[invalid_mask, "geometry"] = gdf.loc[invalid_mask, "geometry"].buffer(0)

    removed = initial_count - len(gdf)
    if removed > 0:
        log.warning(f"  {removed} entités supprimées (géométries nulles)")

    return gdf


def reproject(gdf: gpd.GeoDataFrame, epsg: int) -> gpd.GeoDataFrame:
    """
    Reprojette le GeoDataFrame vers un système de coordonnées cible.

    Args:
        gdf: GeoDataFrame source
        epsg: code EPSG de la projection cible

    Returns:
        GeoDataFrame reprojeté

    Raises:
        ValueError: si le code EPSG est invalide
    """
    if epsg <= 0:
        raise ValueError(f"Code EPSG invalide : {epsg}")

    source_crs = gdf.crs
    gdf = gdf.to_crs(epsg=epsg)
    log.debug(f"  Reprojection : {source_crs} → EPSG:{epsg}")
    return gdf


def filter_by_region(gdf: gpd.GeoDataFrame, column: str, value: str) -> gpd.GeoDataFrame:
    """
    Filtre les entités selon la valeur d'une colonne attributaire.

    Args:
        gdf: GeoDataFrame source
        column: nom de la colonne de filtrage
        value: valeur à conserver (insensible à la casse)

    Returns:
        GeoDataFrame filtré

    Raises:
        KeyError: si la colonne n'existe pas
        ValueError: si aucune entité ne correspond au filtre
    """
    if column not in gdf.columns:
        raise KeyError(f"Colonne '{column}' absente du GeoDataFrame. Colonnes disponibles : {list(gdf.columns)}")

    filtered = gdf[gdf[column].str.lower() == value.lower()].copy()

    if filtered.empty:
        available = gdf[column].unique().tolist()
        raise ValueError(
            f"Aucune entité trouvée pour '{value}' dans la colonne '{column}'.\n"
            f"Valeurs disponibles : {available}"
        )

    return filtered
