"""
src/export.py — Étape 4 : sauvegarde des résultats.

Responsabilité : écrire les fichiers de sortie (GeoJSON, CSV, carte PNG).
Toutes les fonctions créent les dossiers parents si nécessaire.
"""

import logging
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

log = logging.getLogger(__name__)


def save_geodata(gdf: gpd.GeoDataFrame, path: str) -> None:
    """
    Sauvegarde un GeoDataFrame en GeoJSON.

    Args:
        gdf: GeoDataFrame à sauvegarder
        path: chemin de destination (ex: "data/processed/mrc.geojson")
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out, driver="GeoJSON")
    log.debug(f"  GeoJSON sauvegardé : {out}")


def save_stats(df: pd.DataFrame, path: str) -> None:
    """
    Sauvegarde un DataFrame de statistiques en CSV.

    Args:
        df: DataFrame à sauvegarder
        path: chemin de destination (ex: "outputs/stats.csv")
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    log.debug(f"  CSV sauvegardé : {out}")


def save_map(
    gdf: gpd.GeoDataFrame,
    column: str,
    path: str,
    title: str = "",
    cmap: str = "YlOrRd",
    figsize: tuple = (12, 10),
) -> None:
    """
    Génère et sauvegarde une carte choroplèthe.

    Args:
        gdf: GeoDataFrame contenant la colonne à visualiser
        column: colonne numérique à représenter
        path: chemin de sortie de l'image (PNG)
        title: titre de la carte
        cmap: palette de couleurs matplotlib
        figsize: taille de la figure en pouces
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=figsize)

    gdf.plot(
        column=column,
        ax=ax,
        cmap=cmap,
        legend=True,
        legend_kwds={"label": column, "orientation": "horizontal"},
        edgecolor="white",
        linewidth=0.3,
    )

    ax.set_title(title, fontsize=14, pad=12)
    ax.set_axis_off()
    plt.tight_layout()

    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.debug(f"  Carte sauvegardée : {out}")
