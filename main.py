"""
main.py — Point d'entrée du pipeline géomatique.

Usage:
    python main.py
    python main.py --region "Estrie"
    python main.py --epsg 32198 --verbose
"""

import argparse
import logging
import yaml

from src.ingest import load_data
from src.process import reproject, filter_by_region, clean_geometries
from src.analyze import compute_area_stats
from src.export import save_geodata, save_stats, save_map


def setup_logging(verbose: bool) -> None:
    """Configure le système de logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def load_config(path: str = "config.yaml") -> dict:
    """Charge la configuration depuis un fichier YAML."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_pipeline(config: dict, region: str | None = None, epsg: int | None = None) -> None:
    """
    Exécute le pipeline complet en 4 étapes.

    Args:
        config: dictionnaire de configuration
        region: filtre optionnel sur la région administrative
        epsg: projection cible optionnelle (remplace config)
    """
    log = logging.getLogger(__name__)

    # Surcharger la config avec les arguments CLI si fournis
    if region:
        config["processing"]["region_filter"] = region
    if epsg:
        config["processing"]["target_epsg"] = epsg

    # ── Étape 1 : Ingestion ──────────────────────────────────────────────────
    log.info("Étape 1/4 — Chargement des données...")
    gdf = load_data(
        url=config["data"]["url"],
        cache_path=config["data"]["raw_path"],
    )
    log.info(f"  {len(gdf)} entités chargées.")

    # ── Étape 2 : Traitement ─────────────────────────────────────────────────
    log.info("Étape 2/4 — Traitement géospatial...")
    gdf = clean_geometries(gdf)
    gdf = reproject(gdf, epsg=config["processing"]["target_epsg"])

    region_filter = config["processing"]["region_filter"]
    if region_filter:
        gdf = filter_by_region(
            gdf,
            column=config["analysis"]["region_column"],
            value=region_filter,
        )
        log.info(f"  Filtre appliqué sur '{region_filter}' → {len(gdf)} entités.")

    # ── Étape 3 : Analyse ────────────────────────────────────────────────────
    log.info("Étape 3/4 — Calcul des statistiques...")
    gdf, stats = compute_area_stats(gdf, name_col=config["analysis"]["name_column"])
    log.debug(f"\n{stats.to_string()}")

    # ── Étape 4 : Export ─────────────────────────────────────────────────────
    log.info("Étape 4/4 — Export des résultats...")
    save_geodata(gdf, path=config["export"]["processed_path"])
    save_stats(stats, path=config["export"]["stats_path"])
    save_map(
        gdf,
        column="aire_km2",
        path=config["export"]["map_path"],
        title=config["export"]["map_title"],
    )

    log.info("✅ Pipeline terminé avec succès.")
    log.info(f"   Carte     → {config['export']['map_path']}")
    log.info(f"   Stats     → {config['export']['stats_path']}")
    log.info(f"   GeoJSON   → {config['export']['processed_path']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline géomatique GMQ 580")
    parser.add_argument("--region", type=str, default=None, help="Filtrer par région administrative")
    parser.add_argument("--epsg", type=int, default=None, help="Code EPSG de la projection cible")
    parser.add_argument("--verbose", action="store_true", help="Afficher les logs détaillés")
    args = parser.parse_args()

    setup_logging(args.verbose)
    config = load_config()
    run_pipeline(config, region=args.region, epsg=args.epsg)
