"""
src/ingest.py — Étape 1 : chargement des données géospatiales.

Responsabilité unique : obtenir les données brutes et les retourner
sous forme de GeoDataFrame. Aucune transformation ici.
"""

import logging
import os
from pathlib import Path

import geopandas as gpd
import requests

log = logging.getLogger(__name__)


def load_data(url: str, cache_path: str) -> gpd.GeoDataFrame:
    """
    Charge un fichier GeoJSON depuis une URL, avec mise en cache locale.

    Si le fichier existe déjà dans cache_path, il est lu localement
    (évite de re-télécharger à chaque exécution).

    Args:
        url: URL du fichier GeoJSON distant
        cache_path: chemin local pour stocker/lire le fichier

    Returns:
        GeoDataFrame contenant les données brutes

    Raises:
        requests.HTTPError: si le téléchargement échoue
        ValueError: si le fichier ne contient pas de géométries valides
    """
    cache = Path(cache_path)

    if cache.exists():
        log.debug(f"Cache trouvé, lecture locale : {cache}")
        return gpd.read_file(cache)

    log.debug(f"Téléchargement depuis : {url}")
    _download_file(url, cache)
    return gpd.read_file(cache)


def _download_file(url: str, destination: Path) -> None:
    """
    Télécharge un fichier et le sauvegarde localement.

    Args:
        url: URL source
        destination: chemin de destination
    """
    destination.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=30)
    response.raise_for_status()  # lève une exception si erreur HTTP

    with open(destination, "wb") as f:
        f.write(response.content)

    log.debug(f"Fichier sauvegardé : {destination} ({os.path.getsize(destination) / 1024:.1f} Ko)")
