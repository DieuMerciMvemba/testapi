# MaziShark API Backend - FastAPI

Backend scientifique complet pour visualiser les données océanographiques et l'habitat potentiel des requins.

## Structure du projet

mazisharkfastapi/
├── api/
│   └── index.py          # Backend FastAPI complet
├── processed_data/       # Données scientifiques
│   ├── pace_chlor_a.nc
│   ├── modis_chlor_a.nc
│   ├── sst_celsius.nc
│   ├── swot_ssh.nc
│   ├── habitat_index_H.nc
│   ├── hotspots_H_top20.csv
│   └── metadata.json
├── requirements.txt      # Dépendances Python
├── vercel.json          # Configuration Vercel
└── README.md

## Endpoints disponibles

### 1. **GET /** - Documentation de l'API
Retourne la liste de tous les endpoints et couches disponibles.

### 2. **GET /data/layers** - Liste des couches
Retourne `metadata.json` avec toutes les couches scientifiques disponibles.

**Utilisation frontend**: Menu déroulant pour sélectionner les couches à afficher.

### 3. **GET /data/habitat** - GeoJSON de l'habitat
Retourne le GeoJSON de l'habitat potentiel (si disponible).

**Utilisation frontend**: Afficher les zones d'habitat sur Leaflet.

### 4. **GET /data/{layer_name}** - Données d'une couche
Retourne les données NetCDF en JSON (lat, lon, valeurs, stats).

**Paramètres**:
- `sample` (bool): Échantillonner pour réduire la taille (défaut: true)
- `max_points` (int): Nombre max de points (défaut: 10000)

**Exemples**:
- `/data/pace_chlor_a`
- `/data/sst_celsius`
- `/data/habitat_index_H`

### 5. **GET /data/{layer_name}/map** - Carte PNG
Génère une carte PNG d'une couche avec matplotlib.

**Paramètres**:
- `cmap` (str): Colormap matplotlib (défaut: viridis)

**Utilisation frontend**: ImageOverlay sur Leaflet.

### 6. **GET /predict?lat={lat}&lon={lon}** - Prédiction au point
Retourne l'indice H au point le plus proche.

**Utilisation frontend**: Clic sur la carte pour obtenir la valeur H.

### 7. **GET /hotspots** - Zones à fort potentiel
Retourne les top 20% des zones avec le plus fort indice d'habitat.

**Utilisation frontend**: Marqueurs sur les zones prioritaires.

### 8. **Endpoints legacy** (compatibilité)
- `/meta` - Métadonnées habitat
- `/map` - Carte habitat
- `/analyze` - Statistiques habitat

## Installation locale

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur de développement
uvicorn api.index:app --reload --port 8000

# Tester l'API
curl http://localhost:8000/
curl http://localhost:8000/data/layers
```

## Déploiement sur Vercel

1. **Connecter le repo GitHub à Vercel**
2. **Configuration**:
   - Root Directory: `mazisharkfastapi`
   - Build Command: (laisser vide)
   - Output Directory: (laisser vide)

3. **Variables d'environnement** (optionnel):
   ```
   CORS_ALLOW_ORIGINS=*
   ```

4. **Déployer** 🚀

L'API sera accessible à: `https://votre-projet.vercel.app`

## Données scientifiques

Le répertoire `processed_data/` contient:

- **pace_chlor_a.nc**: Chlorophylle-a PACE (8.3 MB)
- **modis_chlor_a.nc**: Chlorophylle-a MODIS (15.84 MB)
- **sst_celsius.nc**: Température de surface (7.93 MB)
- **swot_ssh.nc**: hauteur de surface SWOT (7.93 MB)
- **habitat_index_H.nc**: Indice d'habitat potentiel (7.93 MB)
- **hotspots_H_top20.csv**: Top 20% des zones à fort potentiel
- **metadata.json**: Métadonnées de toutes les couches

## Configuration CORS

Le backend autorise toutes les origines par défaut (`*`).

Pour restreindre à des domaines spécifiques:
```bash
export CORS_ALLOW_ORIGINS="https://mazisharklive.vercel.app,https://localhost:3000"
```

## Notes techniques

- **Échantillonnage automatique**: Les données sont réduites pour éviter de surcharger la mémoire
- **Détection automatique**: La variable principale de chaque NetCDF est détectée automatiquement
- **Gestion d'erreurs**: Tous les endpoints gèrent les erreurs avec des messages explicites
- **Modulaire**: Code organisé en sections pour faciliter l'ajout de nouvelles fonctionnalités

## Tests rapides

```bash
# Vérifier l'état de l'API
curl http://localhost:8000/health

# Lister les couches
curl http://localhost:8000/data/layers

# Obtenir les données d'une couche
curl http://localhost:8000/data/pace_chlor_a

# Prédiction au point
curl "http://localhost:8000/predict?lat=-21.5&lon=55.5"

# Hotspots
curl http://localhost:8000/hotspots
