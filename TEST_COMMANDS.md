# 🧪 Commandes de Test - Backend MaziShark

## 🚀 Démarrer le serveur

```bash
cd mazisharkfastapi
uvicorn api.index:app --reload --port 8000
```

---

## ✅ Tests Basiques

### 1. Vérifier l'état de l'API
```bash
curl http://localhost:8000/health
```
**Résultat attendu:**
```json
{"status": "ok", "message": "MaziShark API is running"}
```

### 2. Documentation de l'API
```bash
curl http://localhost:8000/
```
**Résultat attendu:** Liste de tous les endpoints disponibles

### 3. Liste des couches
```bash
curl http://localhost:8000/data/layers
```
**Résultat attendu:** metadata.json avec toutes les couches

---

## 🧪 Tests des Optimisations

### Test Cache NetCDF

**Premier appel (chargement depuis disque):**
```bash
time curl http://localhost:8000/data/pace_chlor_a > /dev/null
```
**Temps attendu:** ~2-3 secondes

**Deuxième appel (depuis cache):**
```bash
time curl http://localhost:8000/data/pace_chlor_a > /dev/null
```
**Temps attendu:** ~200-300ms (⚡ 90% plus rapide)

---

### Test Streaming PNG

**Télécharger une carte:**
```bash
curl http://localhost:8000/data/sst_celsius/map -o sst_map.png
```
**Vérifier:** Pas de fichiers temporaires dans `api/`

**Tester différentes colormaps:**
```bash
curl "http://localhost:8000/data/pace_chlor_a/map?cmap=plasma" -o pace_plasma.png
curl "http://localhost:8000/data/modis_chlor_a/map?cmap=coolwarm" -o modis_coolwarm.png
curl "http://localhost:8000/data/habitat_index_H/map?cmap=viridis" -o habitat_viridis.png
```

---

### Test Validation Coordonnées

**Coordonnées valides:**
```bash
curl "http://localhost:8000/predict?lat=-21.5&lon=55.5"
```
**Résultat attendu:** ✅ Valeur H retournée

**Latitude hors limites:**
```bash
curl "http://localhost:8000/predict?lat=50&lon=55.5"
```
**Résultat attendu:** ❌ 400 Bad Request
```json
{
  "detail": "Latitude 50 hors limites. Plage valide: [-25.0, -15.0]"
}
```

**Longitude hors limites:**
```bash
curl "http://localhost:8000/predict?lat=-21.5&lon=100"
```
**Résultat attendu:** ❌ 400 Bad Request

---

### Test Validation Colormap

**Colormap valide:**
```bash
curl "http://localhost:8000/data/sst_celsius/map?cmap=viridis" -o test.png
```
**Résultat attendu:** ✅ PNG généré

**Colormap invalide:**
```bash
curl "http://localhost:8000/data/sst_celsius/map?cmap=invalid_colormap"
```
**Résultat attendu:** ❌ 400 Bad Request
```json
{
  "detail": "Colormap 'invalid_colormap' invalide. Valides: autumn, cool, coolwarm, ..."
}
```

**Tester toutes les colormaps valides:**
```bash
for cmap in viridis plasma inferno magma cividis coolwarm RdYlBu RdYlGn Spectral jet hot cool spring summer autumn winter; do
  echo "Testing $cmap..."
  curl "http://localhost:8000/data/sst_celsius/map?cmap=$cmap" -o "test_$cmap.png"
done
```

---

### Test Validation max_points

**Valeur valide:**
```bash
curl "http://localhost:8000/data/pace_chlor_a?max_points=5000"
```
**Résultat attendu:** ✅ Données échantillonnées avec `sampling_factor`

**Valeur trop petite:**
```bash
curl "http://localhost:8000/data/pace_chlor_a?max_points=50"
```
**Résultat attendu:** ❌ 422 Unprocessable Entity

**Valeur trop grande:**
```bash
curl "http://localhost:8000/data/pace_chlor_a?max_points=200000"
```
**Résultat attendu:** ❌ 422 Unprocessable Entity

**Tester différentes valeurs:**
```bash
curl "http://localhost:8000/data/pace_chlor_a?max_points=100"    # Min valide
curl "http://localhost:8000/data/pace_chlor_a?max_points=1000"
curl "http://localhost:8000/data/pace_chlor_a?max_points=10000"  # Défaut
curl "http://localhost:8000/data/pace_chlor_a?max_points=100000" # Max valide
```

---

## 📊 Tests de Performance

### Mesurer le temps de réponse

**Avec cache (après premier chargement):**
```bash
# Test 10 requêtes consécutives
for i in {1..10}; do
  echo "Request $i:"
  time curl -s http://localhost:8000/data/pace_chlor_a > /dev/null
done
```

**Comparer avec/sans échantillonnage:**
```bash
# Sans échantillonnage (toutes les données)
time curl "http://localhost:8000/data/modis_chlor_a?sample=false" > /dev/null

# Avec échantillonnage (défaut)
time curl "http://localhost:8000/data/modis_chlor_a?sample=true&max_points=10000" > /dev/null
```

---

## 🔍 Tests des Endpoints Spécifiques

### GET /data/layers
```bash
curl http://localhost:8000/data/layers | jq
```

### GET /data/{layer_name}
```bash
# Toutes les couches disponibles
curl http://localhost:8000/data/pace_chlor_a | jq
curl http://localhost:8000/data/modis_chlor_a | jq
curl http://localhost:8000/data/sst_celsius | jq
curl http://localhost:8000/data/swot_ssh | jq
curl http://localhost:8000/data/habitat_index_H | jq
```

### GET /data/{layer_name}/map
```bash
# Générer toutes les cartes
curl http://localhost:8000/data/pace_chlor_a/map -o pace.png
curl http://localhost:8000/data/modis_chlor_a/map -o modis.png
curl http://localhost:8000/data/sst_celsius/map -o sst.png
curl http://localhost:8000/data/swot_ssh/map -o swot.png
curl http://localhost:8000/data/habitat_index_H/map -o habitat.png
```

### GET /predict
```bash
# Tester plusieurs points
curl "http://localhost:8000/predict?lat=-21.5&lon=55.5" | jq
curl "http://localhost:8000/predict?lat=-20.0&lon=56.0" | jq
curl "http://localhost:8000/predict?lat=-22.0&lon=54.5" | jq
```

### GET /hotspots
```bash
curl http://localhost:8000/hotspots | jq
```

### GET /data/habitat (GeoJSON)
```bash
curl http://localhost:8000/data/habitat | jq
```

---

## 🌐 Tests avec Frontend

### Tester CORS
```bash
# Depuis un autre domaine
curl -H "Origin: https://example.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/data/layers
```
**Résultat attendu:** Headers CORS présents

---

## 🐛 Tests d'Erreurs

### Couche inexistante
```bash
curl http://localhost:8000/data/invalid_layer
```
**Résultat attendu:** ❌ 404 Not Found

### Paramètres invalides
```bash
# Latitude invalide (hors -90 à 90)
curl "http://localhost:8000/predict?lat=100&lon=55"

# Longitude invalide (hors -180 à 180)
curl "http://localhost:8000/predict?lat=-21&lon=200"

# max_points invalide
curl "http://localhost:8000/data/pace_chlor_a?max_points=-100"
```

---

## 📈 Monitoring et Logs

### Vérifier les logs du serveur
```bash
# Les logs uvicorn montrent:
# - Temps de réponse
# - Status codes
# - Erreurs éventuelles
```

### Vérifier l'utilisation mémoire
```bash
# Windows
tasklist | findstr python

# Linux/Mac
ps aux | grep python
```

---

## ✅ Checklist de Tests

- [ ] Serveur démarre sans erreur
- [ ] `/health` retourne OK
- [ ] `/` retourne la documentation
- [ ] `/data/layers` retourne toutes les couches
- [ ] Cache NetCDF fonctionne (2ème requête plus rapide)
- [ ] Streaming PNG fonctionne (pas de fichiers temporaires)
- [ ] Validation coordonnées fonctionne (erreur 400 si hors limites)
- [ ] Validation colormap fonctionne (erreur 400 si invalide)
- [ ] Validation max_points fonctionne (erreur 422 si hors limites)
- [ ] Toutes les couches sont accessibles
- [ ] Toutes les cartes PNG se génèrent
- [ ] `/predict` retourne des valeurs correctes
- [ ] `/hotspots` retourne le CSV
- [ ] CORS fonctionne
- [ ] Gestion d'erreurs correcte

---

## 🚀 Tests de Production

### Avant déploiement Vercel

1. **Tester localement avec toutes les couches:**
```bash
for layer in pace_chlor_a modis_chlor_a sst_celsius swot_ssh habitat_index_H; do
  echo "Testing $layer..."
  curl "http://localhost:8000/data/$layer" | jq '.stats'
  curl "http://localhost:8000/data/$layer/map" -o "$layer.png"
done
```

2. **Vérifier les performances:**
```bash
# Mesurer le temps de 100 requêtes
time for i in {1..100}; do
  curl -s http://localhost:8000/data/pace_chlor_a > /dev/null
done
```

3. **Vérifier la mémoire:**
```bash
# Surveiller l'utilisation mémoire pendant les tests
# Le cache ne doit pas dépasser ~100-200 MB
```

---

**Note:** Remplacer `localhost:8000` par l'URL de production après déploiement Vercel.
