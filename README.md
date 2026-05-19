# geo-pipeline — Exemple de pipeline géomatique en Python

Ce repo illustre les bases d'un **pipeline géomatique bien structuré** en Python.  
L'exemple concret : télécharger des communes québécoises, les filtrer, calculer une statistique, et exporter une carte.

---

## Structure du projet

```
geo_pipeline/
│
├── data/
│   ├── raw/          ← données brutes téléchargées (ne pas modifier)
│   └── processed/    ← données transformées par le pipeline
│
├── src/
│   ├── __init__.py
│   ├── ingest.py     ← étape 1 : chargement des données
│   ├── process.py    ← étape 2 : transformations géospatiales
│   ├── analyze.py    ← étape 3 : calculs et statistiques
│   └── export.py     ← étape 4 : sorties (fichiers, cartes)
│
├── tests/
│   ├── test_ingest.py
│   ├── test_process.py
│   └── test_analyze.py
│
├── outputs/          ← cartes et fichiers générés
├── main.py           ← point d'entrée du pipeline
├── config.yaml       ← paramètres configurables
├── requirements.txt
└── README.md
```

---

## Installation

```bash
# Cloner le repo
git clone https://github.com/VOTRE_NOM/geo-pipeline.git
cd geo-pipeline

# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

---

## Lancer le pipeline

```bash
python main.py
```

Options disponibles :

```bash
python main.py --region "Estrie"       # filtrer par région
python main.py --epsg 32198            # changer la projection
python main.py --verbose               # afficher les logs détaillés
```

---

## Les 4 étapes du pipeline

```
[ingest] → [process] → [analyze] → [export]
   ↓            ↓           ↓          ↓
Charger      Reprojeter  Calculer   Sauvegarder
les données  Filtrer     l'aire     carte + CSV
             Nettoyer    moyenne
```

---

## Lancer les tests

```bash
pytest tests/ -v
```

---

## Dépendances principales

| Bibliothèque | Rôle |
|---|---|
| `geopandas` | manipulation de données vectorielles |
| `shapely` | géométries |
| `matplotlib` | visualisation statique |
| `contextily` | fonds de carte |
| `pyproj` | projections |
| `pyyaml` | lecture de la configuration |
| `pytest` | tests unitaires |

