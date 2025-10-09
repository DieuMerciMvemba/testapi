# 🚀 Guide de Déploiement MaziShark API

## 📦 Stratégie d'Optimisation Vercel

### Problème
Vercel limite les déploiements à **100 MB**. Les fichiers NetCDF totalisent ~29 MB.

### Solution
- **Garder sur Vercel** : Fichiers essentiels (3.3 MB)
- **Stocker sur GitHub Release** : Fichiers volumineux (24.9 MB)
- **Téléchargement à la demande** : Les gros fichiers sont téléchargés automatiquement lors de la première requête

---

## ✅ Fichiers sur Vercel (3.3 MB)

| Fichier | Taille | Usage |
|---------|--------|-------|
| `habitat_index_H.nc` | 3.1 MB | Prédictions `/predict` et calculs habitat |
| `shark_habitat_index.geojson.gz` | 206 KB | Endpoint `/data/habitat` (compressé) |
| `hotspots_H_top20.csv` | 729 B | Endpoint `/hotspots` |
| `metadata.json` | 995 B | Liste des couches `/data/layers` |

**Total Vercel : 3.3 MB** ✅

---

## 📦 Fichiers sur GitHub Release (24.9 MB)

| Fichier | Taille | Téléchargement |
|---------|--------|----------------|
| `pace_chlor_a.nc` | 17 MB | À la première requête `/data/pace_chlor_a` |
| `modis_chlor_a.nc` | 964 KB | À la première requête `/data/modis_chlor_a` |
| `sst_celsius.nc` | 1.79 MB | À la première requête `/data/sst_celsius` |
| `swot_ssh.nc` | 44.6 KB | À la première requête `/data/swot_ssh` |

**Total GitHub : 19.8 MB**

---

## 🔧 Configuration

### 1. Créer GitHub Release

```bash
# Tag et release
git tag v1.0.0
git push origin v1.0.0

# Sur GitHub : Create Release v1.0.0
# Uploader les fichiers :
# - pace_chlor_a.nc
# - modis_chlor_a.nc
# - sst_celsius.nc
# - swot_ssh.nc
```

### 2. Fichiers Créés

- ✅ `.vercelignore` : Exclut les gros fichiers du déploiement
- ✅ `api/index.py` : Téléchargement automatique depuis GitHub
- ✅ `requirements.txt` : Ajout de `requests`

### 3. Déployer sur Vercel

```bash
git add .
git commit -m "Optimize: Téléchargement fichiers volumineux depuis GitHub Release"
git push origin main
```

Vercel redéploiera automatiquement avec seulement 3.3 MB !

---

## 🎯 Fonctionnement

### Endpoints Toujours Disponibles (sans téléchargement)
- ✅ `GET /` - Documentation
- ✅ `GET /health` - Santé API
- ✅ `GET /data/layers` - Liste couches
- ✅ `GET /data/habitat` - GeoJSON habitat
- ✅ `GET /predict?lat=X&lon=Y` - Prédictions
- ✅ `GET /hotspots` - Zones prioritaires

### Endpoints avec Téléchargement (première fois uniquement)
- 📥 `GET /data/pace_chlor_a` - Télécharge pace_chlor_a.nc (17 MB)
- 📥 `GET /data/modis_chlor_a` - Télécharge modis_chlor_a.nc (964 KB)
- 📥 `GET /data/sst_celsius` - Télécharge sst_celsius.nc (1.79 MB)
- 📥 `GET /data/swot_ssh` - Télécharge swot_ssh.nc (44.6 KB)

**Note** : Après le premier téléchargement, les fichiers sont mis en cache et réutilisés.

---

## 📊 Avantages

✅ **Déploiement Vercel** : 3.3 MB (sous limite 100 MB)
✅ **Fonctionnalités principales** : Toujours disponibles
✅ **Téléchargement intelligent** : Seulement si nécessaire
✅ **Cache** : Fichiers téléchargés réutilisés
✅ **Transparent** : L'utilisateur ne voit aucune différence

---

## 🧪 Tests

```bash
# Tester localement
uvicorn api.index:app --reload

# Endpoints sans téléchargement
curl http://localhost:8000/health
curl http://localhost:8000/data/habitat
curl http://localhost:8000/predict?lat=-21&lon=55

# Endpoints avec téléchargement (première fois)
curl http://localhost:8000/data/pace_chlor_a
# → Télécharge pace_chlor_a.nc depuis GitHub Release
```

---

## ⚠️ Important

1. **GitHub Release** : Doit être publique et contenir les fichiers
2. **URL Release** : Vérifier que l'URL dans `api/index.py` est correcte
3. **Timeout** : Le premier téléchargement peut prendre 30-60 secondes
4. **Cache Vercel** : Les fichiers téléchargés persistent entre les requêtes

---

## 🎯 Résultat Final

**Avant** : 29 MB → ❌ Risque limite Vercel
**Après** : 3.3 MB → ✅ Déploiement optimal

**Toutes les fonctionnalités sont préservées !** 🦈✨
