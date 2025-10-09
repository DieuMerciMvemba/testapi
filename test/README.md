# Tests API MaziShark

Tests pour l'API déployée sur Vercel: **https://testapi-theta.vercel.app/**

## Fichiers de test

- **`test_api.py`**: Script Python complet avec tous les tests
- **`test_endpoints.sh`**: Script Bash pour tests rapides (Linux/Mac)
- **`test_endpoints.ps1`**: Script PowerShell pour tests rapides (Windows)

## Exécution des tests

### Option 1: Script Python (recommandé)

```bash
# Installer les dépendances
pip install requests

# Lancer tous les tests
python test/test_api.py
```

### Option 2: Script Bash (Linux/Mac)

```bash
chmod +x test/test_endpoints.sh
./test/test_endpoints.sh
```

### Option 3: Script PowerShell (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File test/test_endpoints.ps1
```

### Option 4: Tests manuels avec curl

```bash
# Test 1: Root
curl https://testapi-theta.vercel.app/

# Test 2: Health
curl https://testapi-theta.vercel.app/health

# Test 3: Layers
curl https://testapi-theta.vercel.app/data/layers

# Test 4: Habitat GeoJSON
curl https://testapi-theta.vercel.app/data/habitat

# Test 5: Layer data
curl "https://testapi-theta.vercel.app/data/habitat_index_H?sample=true&max_points=1000"

# Test 6: Predict
curl "https://testapi-theta.vercel.app/predict?lat=49.0&lon=-22.5"

# Test 7: Hotspots
curl https://testapi-theta.vercel.app/hotspots

# Test 8: Map (télécharge PNG)
curl "https://testapi-theta.vercel.app/data/habitat_index_H/map?cmap=viridis" -o habitat_map.png
```

## Endpoints testés

| Endpoint | Description | Test |
|----------|-------------|------|
| `GET /` | Documentation API | ✅ |
| `GET /health` | Santé de l'API | ✅ |
| `GET /data/layers` | Liste des couches | ✅ |
| `GET /data/habitat` | GeoJSON habitat | ✅ |
| `GET /data/{layer_name}` | Données d'une couche | ✅ |
| `GET /data/{layer_name}/map` | Carte PNG | ✅ |
| `GET /predict?lat={lat}&lon={lon}` | Prédiction au point | ✅ |
| `GET /hotspots` | Zones prioritaires | ✅ |

## Résultats attendus

### ✅ Succès (200 OK)
- Tous les endpoints doivent retourner un code 200
- Les données JSON doivent être bien formées
- Les images PNG doivent être téléchargeables

### ❌ Erreurs possibles
- **404**: Fichier de données manquant
- **500**: Erreur serveur (problème de traitement)
- **400**: Paramètres invalides

## Notes

- Les tests utilisent l'échantillonnage (`sample=true`) pour réduire la taille des données
- L'endpoint `/data/habitat` utilise maintenant `shark_habitat_index.geojson`
- Les cartes PNG sont générées à la volée (pas de cache)
