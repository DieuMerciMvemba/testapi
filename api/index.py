# ============================================================================
# MAZISHARK API v2.0.0 - Backend scientifique pour habitats de requins
# ============================================================================

import os
import json
import logging
import datetime
import io
from typing import Optional
from pathlib import Path

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import StreamingResponse, JSONResponse

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="MaziShark API",
    description="API scientifique pour la visualisation des habitats de requins",
    version="2.0.0"
)

# Répertoire des données NetCDF
PROCESSED_DATA_DIR = Path("processed_data")

# Cache en mémoire pour les datasets (évite de recharger à chaque requête)
_DATASET_CACHE = {}

# Colormaps valides pour les cartes
VALID_COLORMAPS = [
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd',
    'afmhot', 'autumn', 'bone', 'cool', 'copper', 'flag', 'gray', 'hot', 'hsv', 'jet', 'pink', 'prism', 'spring', 'summer', 'winter'
]

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_data_path(filename: str) -> Path:
    """Retourne le chemin complet vers un fichier de données."""
    return PROCESSED_DATA_DIR / filename

def load_metadata() -> dict:
    """Charge le fichier metadata.json qui liste les couches disponibles."""
    try:
        path = get_data_path("metadata.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chargement metadata.json: {e}")

def load_netcdf(layer_name: str, use_cache: bool = True) -> xr.Dataset:
    """
    Charge un fichier NetCDF (.nc) avec xarray.
    Les fichiers NetCDF contiennent les données scientifiques multidimensionnelles (lat, lon, valeurs).

    Cache: Les datasets sont mis en cache en mémoire pour éviter de recharger à chaque requête.
    """
    # Vérifier le cache d'abord
    if use_cache and layer_name in _DATASET_CACHE:
        return _DATASET_CACHE[layer_name]

    metadata = load_metadata()
    if layer_name not in metadata:
        raise HTTPException(status_code=404, detail=f"Couche '{layer_name}' introuvable dans metadata.json")

    filename = metadata[layer_name]["filename"]
    try:
        path = get_data_path(filename)
        ds = xr.open_dataset(path)

        # Mettre en cache
        if use_cache:
            _DATASET_CACHE[layer_name] = ds

        return ds
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chargement {filename}: {e}")

def get_primary_variable(ds: xr.Dataset) -> str:
    """
    Détecte automatiquement la variable principale d'un dataset NetCDF.
    Ignore les coordonnées (lat, lon, time) et retourne la première variable de données.
    """
    coord_names = {"lat", "lon", "latitude", "longitude", "time", "x", "y"}
    data_vars = [v for v in ds.data_vars if v not in coord_names]
    if not data_vars:
        raise ValueError("Aucune variable de données trouvée dans le NetCDF")
    return data_vars[0]

def sample_data(data: np.ndarray, max_points: int = 10000) -> tuple[np.ndarray, int]:
    """
    Échantillonne les données pour éviter de surcharger la mémoire et le réseau.
    Réduit la résolution si nécessaire pour rester sous max_points.

    Returns:
        tuple: (données échantillonnées, facteur d'échantillonnage)
    """
    if data.size <= max_points:
        return data, 1

    # Calcul du facteur de sous-échantillonnage
    factor = int(np.ceil(np.sqrt(data.size / max_points)))
    return data[::factor, ::factor], factor

def get_lat_lon_arrays(ds: xr.Dataset) -> tuple[np.ndarray, np.ndarray]:
    """
    Extrait les tableaux de latitude et longitude d'un dataset xarray.
    Gère les différents noms de coordonnées (lat/latitude, lon/longitude).
    Cherche dans coords ET dans variables.

    Returns:
        tuple: (lat_array, lon_array)
    """
    # Détecter le nom de la coordonnée latitude (dans coords ou variables)
    if "lat" in ds.coords:
        lat_arr = ds["lat"].values
    elif "latitude" in ds.coords:
        lat_arr = ds["latitude"].values
    elif "lat" in ds.variables:
        lat_arr = ds["lat"].values
    elif "latitude" in ds.variables:
        lat_arr = ds["latitude"].values
    elif "lat" in ds.dims:
        # Créer des coordonnées à partir des dimensions si nécessaire
        lat_size = ds.dims["lat"]
        lat_arr = np.linspace(-90, 90, lat_size)  # Hypothèse: grille régulière globale
    else:
        raise ValueError(f"Aucune coordonnée latitude trouvée. Coords: {list(ds.coords)}, Variables: {list(ds.variables)}, Dims: {list(ds.dims)}")

    # Détecter le nom de la coordonnée longitude (dans coords ou variables)
    if "lon" in ds.coords:
        lon_arr = ds["lon"].values
    elif "longitude" in ds.coords:
        lon_arr = ds["longitude"].values
    elif "lon" in ds.variables:
        lon_arr = ds["lon"].values
    elif "longitude" in ds.variables:
        lon_arr = ds["longitude"].values
    elif "lon" in ds.dims:
        # Créer des coordonnées à partir des dimensions si nécessaire
        lon_size = ds.dims["lon"]
        lon_arr = np.linspace(-180, 180, lon_size)  # Hypothèse: grille régulière globale
    else:
        raise ValueError(f"Aucune coordonnée longitude trouvée. Coords: {list(ds.coords)}, Variables: {list(ds.variables)}, Dims: {list(ds.dims)}")

    return lat_arr, lon_arr

def validate_coordinates(lat: float, lon: float, ds: xr.Dataset) -> None:
    """
    Valide que les coordonnées lat/lon sont dans la plage du dataset.
    Lève une HTTPException si hors limites.
    """
    lat_arr, lon_arr = get_lat_lon_arrays(ds)

    lat_min, lat_max = float(lat_arr.min()), float(lat_arr.max())
    lon_min, lon_max = float(lon_arr.min()), float(lon_arr.max())

    if not (lat_min <= lat <= lat_max):
        raise HTTPException(
            status_code=400,
            detail=f"Latitude {lat} hors limites. Plage valide: [{lat_min:.2f}, {lat_max:.2f}]"
        )

    if not (lon_min <= lon <= lon_max):
        raise HTTPException(
            status_code=400,
            detail=f"Longitude {lon} hors limites. Plage valide: [{lon_min:.2f}, {lon_max:.2f}]"
        )

# ============================================================================
# ENDPOINT 1: Page d'accueil de l'API
# ============================================================================

@app.get("/")
def root():
    """
    Point d'entrée de l'API - Documentation des endpoints disponibles.
    Utilisé pour vérifier que l'API fonctionne et découvrir les routes.
    """
    return {
        "name": "MaziShark API",
        "version": "2.0.0",
        "description": "API scientifique pour la visualisation des habitats de requins",
        "endpoints": {
            "/": "Cette page (documentation)",
            "/health": "Vérification de l'état de l'API",
            "/data/layers": "Liste toutes les couches disponibles (metadata.json)",
            "/data/habitat": "GeoJSON de l'habitat potentiel",
            "/data/{layer_name}": "Données JSON d'une couche NetCDF",
            "/data/{layer_name}/map": "Carte PNG d'une couche",
            "/predict?lat={lat}&lon={lon}": "Prédiction de l'indice H à un point",
            "/hotspots": "Zones à fort potentiel (top 20%)",
        },
        "available_layers": list(load_metadata().keys()),
        "data_directory": PROCESSED_DATA_DIR,
    }

@app.get("/health")
def health():
    """Endpoint de santé pour vérifier que l'API est opérationnelle."""
    return {"status": "ok", "message": "MaziShark API is running"}

# ============================================================================
# ENDPOINT 2: Liste des couches disponibles
# ============================================================================

@app.get("/data/layers")
def get_layers():
    """
    Retourne metadata.json qui liste toutes les couches scientifiques disponibles.

    Utilisation frontend:
    - Afficher dynamiquement les options de couches dans un menu déroulant
    - Connaître les noms de fichiers et tailles pour optimiser le chargement
    - Construire les URLs pour récupérer chaque couche
    """
    try:
        metadata = load_metadata()
        return {
            "layers": metadata,
            "count": len(metadata),
            "description": "Couches océanographiques disponibles pour visualisation"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT 3: Habitat potentiel (GeoJSON)
# ============================================================================

@app.get("/data/habitat")
def get_habitat_geojson(threshold: Optional[float] = None, max_features: Optional[int] = None):
    """
    Retourne le GeoJSON pré-généré des zones d'habitat potentiel.
    
    Le fichier shark_habitat_index.geojson contient toutes les zones d'habitat
    calculées à partir de habitat_index_H.nc.
    
    Args:
        threshold: (Optionnel) Filtre les features avec H_index >= threshold
        max_features: (Optionnel) Limite le nombre de features retournées
    
    Returns:
        GeoJSON avec les zones d'habitat potentiel
    """
    try:
        # Charger le GeoJSON pré-généré
        geojson_path = get_data_path("shark_habitat_index.geojson")
        
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
        
        # Appliquer les filtres si demandés
        if threshold is not None or max_features is not None:
            features = geojson_data.get("features", [])
            
            # Filtrer par seuil H_index
            if threshold is not None:
                if not 0.0 <= threshold <= 1.0:
                    raise HTTPException(status_code=400, detail="Threshold doit être entre 0.0 et 1.0")
                features = [f for f in features if f.get("properties", {}).get("H_index", 0) >= threshold]
            
            # Limiter le nombre de features
            if max_features is not None:
                if max_features < 1:
                    raise HTTPException(status_code=400, detail="max_features doit être >= 1")
                features = features[:max_features]
            
            # Mettre à jour le GeoJSON avec les features filtrées
            geojson_data["features"] = features
            
            # Ajouter des métadonnées sur le filtrage
            if "metadata" not in geojson_data:
                geojson_data["metadata"] = {}
            
            geojson_data["metadata"]["filtered"] = True
            geojson_data["metadata"]["returned_features"] = len(features)
            if threshold is not None:
                geojson_data["metadata"]["threshold_applied"] = threshold
            if max_features is not None:
                geojson_data["metadata"]["max_features_applied"] = max_features
        
        # Headers pour GeoJSON
        headers = {"Content-Type": "application/geo+json"}
        
        return JSONResponse(content=geojson_data, headers=headers)
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Fichier shark_habitat_index.geojson introuvable dans processed_data/"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur chargement GeoJSON habitat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur chargement GeoJSON: {str(e)}"
        )

# ============================================================================
# ENDPOINT 4: Données NetCDF d'une couche spécifique
# ============================================================================

@app.get("/data/{layer_name}")
def get_layer_data(
    layer_name: str = Path(..., description="Nom de la couche"),
    sample: bool = Query(True, description="Échantillonner les données pour réduire la taille"),
    max_points: int = Query(10000, ge=100, le=100000, description="Nombre maximum de points (100-100000)")
):
    """
    Retourne les données d'une couche NetCDF en format JSON.

    Optimisations:
    - ✅ Cache: Dataset mis en cache en mémoire
    - ✅ Échantillonnage intelligent: Réduit la résolution si nécessaire
    - ✅ Validation: max_points ∈ [100, 100000]

    Paramètres:
    - layer_name: nom de la couche (pace_chlor_a, modis_chlor_a, sst_celsius, swot_ssh, habitat_index_H)
    - sample: si True, réduit la résolution pour optimiser la taille
    - max_points: nombre maximum de points à retourner (100-100000)

    Utilisation frontend:
    - Récupérer les données pour affichage sur carte Leaflet
    - Créer des heatmaps ou overlays colorés
    - Afficher les valeurs dans des tooltips au survol

    Format de sortie:
    {
        "layer": "pace_chlor_a",
        "variable": "chlor_a",
        "lat": [array de latitudes],
        "lon": [array de longitudes],
        "values": [array 2D de valeurs],
        "units": "mg/m³",
        "stats": {"min": 0.01, "max": 5.2, "mean": 0.8},
        "shape": [100, 150],
        "sampling_factor": 2
    }
    """
    try:
        # Chargement avec cache
        ds = load_netcdf(layer_name, use_cache=True)

        # Détection automatique de la variable principale
        var_name = get_primary_variable(ds)
        data_var = ds[var_name]

        # Extraction des coordonnées
        lat, lon = get_lat_lon_arrays(ds)
        values = data_var.values

        # Échantillonnage si demandé
        sampling_factor = 1
        if sample and values.size > max_points:
            values, sampling_factor = sample_data(values, max_points)
            # Réduire aussi les coordonnées avec le même facteur
            lat = lat[::sampling_factor]
            lon = lon[::sampling_factor]

        # Calcul des statistiques
        valid_values = values[np.isfinite(values)]
        stats = {
            "min": float(np.min(valid_values)) if valid_values.size > 0 else None,
            "max": float(np.max(valid_values)) if valid_values.size > 0 else None,
            "mean": float(np.mean(valid_values)) if valid_values.size > 0 else None,
        }

        # Conversion en listes pour JSON
        return {
            "layer": layer_name,
            "variable": var_name,
            "lat": lat.tolist(),
            "lon": lon.tolist(),
            "values": np.where(np.isfinite(values), values, None).tolist(),
            "units": data_var.attrs.get("units", "unknown"),
            "long_name": data_var.attrs.get("long_name", var_name),
            "stats": stats,
            "shape": list(values.shape),
            "sampled": sample,
            "sampling_factor": sampling_factor,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur traitement {layer_name}: {e}")

# ============================================================================
# ENDPOINT 5: Carte PNG d'une couche
# ============================================================================

@app.get("/data/{layer_name}/map")
def get_layer_map(
    layer_name: str = Path(..., description="Nom de la couche"),
    cmap: str = Query("viridis", description="Colormap matplotlib")
):
    """
    Génère une carte PNG d'une couche NetCDF avec matplotlib.

    Optimisations:
    - ✅ Cache: Dataset mis en cache en mémoire
    - ✅ Streaming: Retourne le PNG directement (pas de fichier temporaire)
    - ✅ Validation: Vérifie que la colormap est valide

    Utilisation frontend:
    - Afficher comme ImageOverlay sur Leaflet
    - Télécharger la carte en haute résolution
    - Prévisualisation rapide sans charger toutes les données
    """
    # Validation de la colormap
    if cmap not in VALID_COLORMAPS:
        raise HTTPException(
            status_code=400,
            detail=f"Colormap '{cmap}' invalide. Valides: {', '.join(sorted(VALID_COLORMAPS))}"
        )

    try:
        # Chargement avec cache
        ds = load_netcdf(layer_name, use_cache=True)
        var_name = get_primary_variable(ds)
        data_var = ds[var_name]

        lat, lon = get_lat_lon_arrays(ds)
        values = data_var.values

        # Création de la figure
        fig, ax = plt.subplots(figsize=(12, 8))
        im = ax.pcolormesh(lon, lat, values, cmap=cmap, shading="auto")

        # Titre et labels
        title = data_var.attrs.get("long_name", layer_name)
        units = data_var.attrs.get("units", "")
        ax.set_title(f"{title}", fontsize=14, fontweight="bold")
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)

        # Colorbar
        cbar = plt.colorbar(im, ax=ax, label=f"{units}")
        cbar.ax.tick_params(labelsize=10)

        # Sauvegarde en mémoire (streaming, pas de fichier temporaire)
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)

        # Retour direct en streaming (évite les fichiers temporaires et conflits)
        return StreamingResponse(
            buf,
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename={layer_name}_map.png"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération carte {layer_name}: {e}")

# ============================================================================
# ENDPOINT 6: Prédiction au point (lat, lon)
# ============================================================================

@app.get("/predict")
def predict(
    lat: float = Query(..., ge=-90, le=90, description="Latitude du point (-90 à 90)"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude du point (-180 à 180)")
):
    """
    Retourne l'indice d'habitat H au point le plus proche (nearest neighbor).

    Optimisations:
    - ✅ Cache: Dataset mis en cache en mémoire
    - ✅ Validation: Vérifie que lat/lon sont dans les limites du dataset
    - ✅ Validation: Vérifie que lat ∈ [-90, 90] et lon ∈ [-180, 180]

    Utilisation frontend:
    - Clic sur la carte pour obtenir la valeur H
    - Afficher dans un popup ou panneau latéral
    - Évaluer le potentiel d'habitat à un endroit précis
    """
    try:
        # Chargement avec cache
        ds = load_netcdf("habitat_index_H", use_cache=True)

        # Validation des coordonnées (vérifie qu'elles sont dans la plage du dataset)
        validate_coordinates(lat, lon, ds)

        H = ds["H_index"]
        lat_arr = ds["lat"].values
        lon_arr = ds["lon"].values

        # Recherche du voisin le plus proche
        i = int(np.abs(lat_arr - lat).argmin())
        j = int(np.abs(lon_arr - lon).argmin())

        val = float(H.values[i, j]) if np.isfinite(H.values[i, j]) else None

        return {
            "lat": lat,
            "lon": lon,
            "H_index": val,
            "nearest_lat": float(lat_arr[i]),
            "nearest_lon": float(lon_arr[j]),
            "grid_indices": {"i": i, "j": j},
            "interpretation": "High potential" if val and val > 0.7 else "Moderate potential" if val and val > 0.4 else "Low potential"
        }

    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier habitat_index_H.nc introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur prédiction: {e}")

# ============================================================================
# ENDPOINT 7: Hotspots (zones à fort potentiel)
# ============================================================================

@app.get("/hotspots")
def get_hotspots():
    """
    Retourne les zones à fort potentiel d'habitat (top 20% des valeurs H).

    Utilisation frontend:
    - Afficher des marqueurs sur les zones prioritaires
    - Créer une liste de recommandations pour les chercheurs
    - Filtrer la carte pour ne montrer que les zones intéressantes
    """
    try:
        # Vérifier si le CSV existe
        csv_path = get_data_path("hotspots_H_top20.csv")

        # Lecture simple du CSV
        hotspots = []
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            headers = lines[0].strip().split(",")

            for line in lines[1:]:
                values = line.strip().split(",")
                hotspot = {headers[i]: float(values[i]) if i > 0 else int(values[i]) for i in range(len(headers))}
                hotspots.append(hotspot)

        return {
            "hotspots": hotspots,
            "count": len(hotspots),
            "description": "Top 20% des zones avec le plus fort indice d'habitat"
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier hotspots_H_top20.csv introuvable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chargement hotspots: {e}")

# ============================================================================
# ENDPOINT LEGACY: Compatibilité avec l'ancien frontend
# ============================================================================

@app.get("/meta")
def meta():
    """Endpoint de compatibilité avec l'ancien frontend."""
    try:
        ds = load_netcdf("habitat_index_H")
        lat = ds["lat"].values
        lon = ds["lon"].values
        return {
            "lat": {"size": int(lat.size), "min": float(lat.min()), "max": float(lat.max())},
            "lon": {"size": int(lon.size), "min": float(lon.min()), "max": float(lon.max())},
        }
    except:
        raise HTTPException(status_code=404, detail="Données habitat introuvables")

@app.get("/map")
def map_legacy():
    """Endpoint de compatibilité - redirige vers /data/habitat_index_H/map"""
    return get_layer_map("habitat_index_H")
