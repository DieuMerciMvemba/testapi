# 🦈 MaziShark FastAPI Backend

Backend scientifique FastAPI pour visualiser les habitats potentiels de requins à partir de données océaniques (PACE, MODIS, SST, SWOT). Ce service alimente l'application frontend (Next.js/React) et peut être déployé sur Vercel.

---

## 📁 Arborescence principale

```
mazisharkfastapi/
├── api/index.py              # Application FastAPI principale
├── API_USAGE_GUIDE.md        # Guide d'utilisation détaillé des endpoints
├── DEPLOYMENT_GUIDE.md       # Stratégie d'optimisation et déploiement Vercel
├── processed_data/           # Données NetCDF / GeoJSON / CSV utilisées par l'API
│   ├── metadata.json         # Métadonnées des couches scientifiques
│   └── ...                   # pace_chlor_a.nc, habitat_index_H.nc, etc.
├── requirements.txt          # Dépendances Python
├── test/test_api.py          # Tests d'intégration (exemples de requêtes)
└── vercel.json               # Configuration déploiement Vercel
```

---

## ⚙️ Installation

```bash
# Cloner le dépôt
 git clone https://github.com/<user>/<repo>.git
 cd mazisharkfastapi

# Créer un environnement virtuel (optionnel)
 python -m venv .venv
 source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1

# Installer les dépendances
 pip install -r requirements.txt

# Lancer le serveur local
 uvicorn api.index:app --reload --port 8000
```

Le serveur est accessible sur `http://127.0.0.1:8000`.

---

## 🧪 Tests

Les tests d'intégration se trouvent dans `test/test_api.py`. Ils s'exécutent directement (script autonome) et servent d'exemples de requêtes vers l'instance déployée (`https://testapi-theta.vercel.app`).

```bash
python test/test_api.py
```

Le script affiche huit scénarios:
- `GET /`
- `GET /health`
- `GET /data/layers`
- `GET /data/habitat`
- `GET /data/habitat_index_H?sample=true&max_points=1000`
- `GET /predict?lat=49.0&lon=-22.5`
- `GET /hotspots`
- `GET /data/habitat_index_H/map?cmap=viridis`

---

## 🌐 Endpoints principaux

| Endpoint | Description | Référence |
|----------|-------------|-----------|
| `GET /` | Documentation JSON + métadonnées détaillées | `api/index.py` (`root()`) |
| `GET /health` | Vérification de santé | `health()` |
| `GET /data/layers` | Retourne `processed_data/metadata.json` enrichi | `get_layers()` |
| `GET /data/habitat` | GeoJSON d'habitat (`shark_habitat_index.geojson(.gz)`) | `get_habitat()` |
| `GET /data/{layer_name}` | Données NetCDF en JSON + stats + échantillonnage | `get_layer_data()` |
| `GET /data/{layer_name}/map` | Carte PNG générée avec matplotlib | `get_layer_map()` |
| `GET /predict` | Valeur `H_index` au point le plus proche | `predict()` |
| `GET /hotspots` | Top 20% des zones à fort potentiel (`hotspots_H_top20.csv`) | `get_hotspots()` |
| `GET /meta` / `/map` / `/analyze` | Compatibilité legacy | Section "ENDPOINT LEGACY" |

Consulter `API_USAGE_GUIDE.md` pour des exemples cURL, intégration React/Leaflet et bonnes pratiques (échantillonnage, colormaps, etc.).

---

## 🗂️ Données scientifiques (`processed_data/`)

Les fichiers NetCDF/GeoJSON utilisés par l'API sont **stockés localement** (aucun téléchargement externe requis sur Vercel). Les caractéristiques détaillées (dimensions, variables, statistiques) sont dans `processed_data/metadata.json` et exposées par `GET /` & `GET /data/layers`.

Principales couches :
- `habitat_index_H.nc` : indice agrégé H (lat=720, lon=1440)
- `pace_chlor_a.nc` : chlorophylle PACE haute résolution
- `modis_chlor_a.nc` : chlorophylle MODIS (4 pas de temps)
- `sst_celsius.nc` : température de surface (1 pas de temps)
- `swot_ssh.nc` : hauteur de mer SWOT
- `shark_habitat_index.geojson.gz` : zones d'habitat pré-calculées
- `hotspots_H_top20.csv` : 20% meilleures zones selon H

---

## 🚀 Déploiement Vercel

Le déploiement est optimisé pour rester sous la limite de 100 MB :
- `.vercelignore` exclut les fichiers NetCDF volumineux si besoin.
- `DEPLOYMENT_GUIDE.md` explique comment utiliser GitHub Releases pour les fichiers lourds (optionnel) et résume les étapes `git push` / création de release.
- `vercel.json` force l'utilisation du runtime Python (`@vercel/python`).

---

## 📄 Ressources complémentaires

- `API_USAGE_GUIDE.md` : scénarios complets d'utilisation des endpoints.
- `DEPLOYMENT_GUIDE.md` : recommandations pour Vercel.
- `test/test_api.py` : tests de bout en bout / documentation vivante.

---

## 🆘 Support

Pour toute question ou contribution:
1. Ouvrir une issue sur le dépôt GitHub.
2. Décrire l'endpoint concerné, les étapes de reproduction et les logs (console + API).
3. Vérifier la cohérence avec `processed_data/metadata.json` avant de soumettre.

**MaziShark API** est prête pour l'intégration frontend et la recherche océanographique ! 🦈🌊
