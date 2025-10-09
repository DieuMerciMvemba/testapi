# 🚀 Guide d'utilisation de l'API MaziShark

Ce document décrit **comment interroger chaque endpoint** du backend `mazisharkfastapi` sans erreur, en s'appuyant sur les mêmes scénarios validés dans `test/test_api.py` et les données NetCDF/GeoJSON stockées dans `processed_data/`.

## 📂 Préparer l'environnement

```bash
cd "c:/Users/dM/Videos/Mazishark Final/dev/mazisharkfastapi"
pip install -r requirements.txt
uvicorn api.index:app --reload --port 8000
```

L'API locale sera accessible sur `http://127.0.0.1:8000`.

Pour interroger la version déployée : `https://testapi-theta.vercel.app`.

## 🧪 Référence tests

Toutes les requêtes ci-dessous sont implémentées et validées dans `test/test_api.py`. Ce fichier est la source officielle de tests d'intégration.

```
mazisharkfastapi/
├── api/index.py
├── processed_data/
├── test/test_api.py  <- références de requêtes
└── API_USAGE_GUIDE.md <- ce guide
```

## 🌐 Endpoints principaux

### 1. `GET /`
- **Description** : documentation JSON de l'API.
- **Usage** : vérifier la disponibilité et consulter les métadonnées (`layers`).
- **Requête** :
  ```bash
  curl https://testapi-theta.vercel.app/
  ```

### 2. `GET /health`
- **Description** : statut rapide de l'API.
- **Réponse** : `{ "status": "ok", "message": "MaziShark API is running" }`
- **Requête** :
  ```bash
  curl https://testapi-theta.vercel.app/health
  ```

### 3. `GET /data/layers`
- **Description** : liste complète des couches NetCDF et GeoJSON déclarées dans `processed_data/metadata.json`.
- **Contenu** : tailles, dimensions, variables, endpoints recommandés (`requests`).
- **Requête** :
  ```bash
  curl https://testapi-theta.vercel.app/data/layers
  ```

### 4. `GET /data/habitat`
- **Description** : retourne `shark_habitat_index.geojson.gz` (décompressé à la volée).
- **Filtres** :
  - `threshold` (ex: `0.5`) pour filtrer `H_index` ≥ seuil.
  - `max_features` (ex: `2000`) pour limiter le nombre de polygones.
- **Exemples** :
  ```bash
  curl "https://testapi-theta.vercel.app/data/habitat"
  curl "https://testapi-theta.vercel.app/data/habitat?threshold=0.6"
  curl "https://testapi-theta.vercel.app/data/habitat?threshold=0.6&max_features=1500"
  ```

### 5. `GET /data/{layer_name}`
- **Description** : extrait un dataset NetCDF en JSON, avec stats et sous-échantillonnage.
- **Paramètres** :
  - `sample` (bool, défaut `true`) : sous-échantillonne pour limiter la charge.
  - `max_points` (int) : nombre max de points retournés (défaut `10000`).
- **Layers disponibles** (voir `metadata.json`) :
  - `pace_chlor_a`
  - `modis_chlor_a`
  - `sst_celsius`
  - `swot_ssh`
  - `habitat_index_H`
- **Exemples** :
  ```bash
  curl "https://testapi-theta.vercel.app/data/habitat_index_H?sample=true&max_points=1000"
  curl "https://testapi-theta.vercel.app/data/modis_chlor_a?sample=true&max_points=5000"
  curl "https://testapi-theta.vercel.app/data/pace_chlor_a?sample=true&max_points=5000"
  ```

### 6. `GET /data/{layer_name}/map`
- **Description** : génère une carte PNG (base64 possible) pour une couche donnée.
- **Paramètres** :
  - `cmap` : colormap matplotlib (ex : `viridis`, `turbo`, `inferno`, `cividis`).
- **Exemple** :
  ```bash
  curl "https://testapi-theta.vercel.app/data/habitat_index_H/map?cmap=viridis" --output habitat_map.png
  ```

### 7. `GET /predict?lat={lat}&lon={lon}`
- **Description** : renvoie `H_index` au point le plus proche dans `habitat_index_H.nc`.
- **Exemple** :
  ```bash
  curl "https://testapi-theta.vercel.app/predict?lat=-21.0&lon=55.5"
  ```
- **Réponse** : lat/lon interrogés, lat/lon les plus proches, `H_index`, interprétation (`high`, `moderate`, `low`).

### 8. `GET /hotspots`
- **Description** : expose les 20 % meilleures zones (`hotspots_H_top20.csv`).
- **Réponse** : liste de hotspots (lat, lon, H) et descriptif.
- **Exemple** :
  ```bash
  curl https://testapi-theta.vercel.app/hotspots
  ```

## 📡 Scénarios d'intégration Frontend (React/Leaflet)

- **Charger la liste des couches** : appeler `/data/layers`, remplir un menu déroulant avec `layers`.
- **Afficher GeoJSON habitat** :
  ```javascript
  fetch("https://testapi-theta.vercel.app/data/habitat?threshold=0.5&max_features=2000")
    .then(res => res.json())
    .then(data => L.geoJSON(data).addTo(map));
  ```
- **Afficher carte raster** :
  ```javascript
  const url = "https://testapi-theta.vercel.app/data/habitat_index_H/map?cmap=viridis";
  const imageOverlay = L.imageOverlay(url, bounds);
  imageOverlay.addTo(map);
  ```
- **Tooltip prédiction** : sur clic carte, appeler `/predict?lat=...&lon=...` pour afficher `H_index`.

## 🧾 Métadonnées de référence

Toutes les statistiques (dimensions, min/max, etc.) sont centralisées dans `processed_data/metadata.json`. Ce fichier est consommé par `/data/layers` et par la route `/`.

Exemple pour `habitat_index_H` :
```json
{
  "habitat_index_H": {
    "filename": "habitat_index_H.nc",
    "size_MB": 3.12,
    "dimensions": {"lat": 720, "lon": 1440},
    "variables": {
      "H_index": {
        "dtype": "float64",
        "min": 0.0,
        "max": 1.0,
        "mean": 0.372203348
      }
    },
    "requests": {
      "data": "/data/habitat_index_H?sample=true&max_points=5000",
      "map": "/data/habitat_index_H/map?cmap=viridis",
      "predict": "/predict?lat=-21.1&lon=55.5"
    }
  }
}
```

## 🔐 Bonnes pratiques
- Toujours appliquer `sample=true` et ajuster `max_points` pour éviter des réponses trop lourdes.
- Utiliser les colormaps listées dans `VALID_COLORMAPS` (définies dans `index.py`).
- Vérifier la présence des fichiers dans `processed_data/` (aucun téléchargement GitHub Release n'est nécessaire sur Vercel).
- Pour éviter les blocages CORS en frontend, configurer `CORS_ALLOW_ORIGINS` si besoin.

## 📚 Références
- Code principal : `api/index.py`
- Tests d'intégration : `test/test_api.py`
- Données : `processed_data/`
- Métadonnées : `processed_data/metadata.json`
- Guide : `API_USAGE_GUIDE.md` (ce document)

**MaziShark API est prête pour l'intégration frontend et la visualisation scientifique ! 🦈**
