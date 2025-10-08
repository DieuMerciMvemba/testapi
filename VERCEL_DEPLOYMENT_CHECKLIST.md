# ✅ Checklist Déploiement Vercel - MaziShark API

## 🔍 Vérifications Pré-Déploiement

### 1. **Code Backend**

#### ✅ Variables Définies
- [x] `CACHE_DIR` défini (remplace `PROCESSED_DATA_DIR`)
- [x] `GITHUB_RELEASE_URL` défini
- [x] `FILE_CHECKSUMS` défini
- [x] Pas de référence à `PROCESSED_DATA_DIR` dans les endpoints

#### ✅ Fonction `get_data_path()`
- [x] Détecte environnement Vercel (`os.getenv("VERCEL")`)
- [x] Sur Vercel: télécharge depuis GitHub Releases
- [x] En dev local: utilise `processed_data/` si disponible
- [x] Fallback sur téléchargement si fichier local absent

#### ✅ Fonction `download_from_release()`
- [x] Cache dans `/tmp/mazishark_cache` (compatible Vercel)
- [x] Vérification checksum SHA256
- [x] Retry automatique (3 tentatives)
- [x] Backoff exponentiel
- [x] Logging détaillé

### 2. **Configuration Vercel**

#### ✅ vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

- [x] Pas de conflit `builds`/`functions`
- [x] `maxLambdaSize: 50mb` pour supporter les NetCDF
- [x] Routes configurées correctement

#### ✅ requirements.txt
```
fastapi==0.115.0
numpy==2.0.2
xarray==2024.9.0
matplotlib==3.9.0
netCDF4==1.7.1
typing_extensions>=4.9.0
```

- [x] Pas de dépendances manquantes
- [x] Versions compatibles Python 3.12

### 3. **GitHub Release**

#### ✅ Release v5.0.0
- URL: https://github.com/DieuMerciMvemba/testapi/releases/tag/v5.0.0

#### ✅ Fichiers Présents
- [x] modis_chlor_a.nc (15.8 MB)
- [x] pace_chlor_a.nc (8.3 MB)
- [x] sst_celsius.nc (7.93 MB)
- [x] swot_ssh.nc (7.93 MB)
- [x] habitat_index_H.nc (7.93 MB)
- [x] hotspots_H_top20.csv (729 B)
- [x] metadata.json (1.2 KB)

#### ✅ URLs Accessibles
Tester manuellement:
```bash
curl -I https://github.com/DieuMerciMvemba/testapi/releases/download/v5.0.0/metadata.json
# Devrait retourner: HTTP/2 200
```

### 4. **Tests Locaux**

#### Test 1: Backend se charge
```bash
python -c "from api.index import app; print('OK')"
```
- [x] Pas d'erreur d'import
- [x] Toutes les routes chargées

#### Test 2: Endpoint racine
```bash
curl http://localhost:8000/
```
- [x] Retourne la documentation
- [x] `cache_directory` présent
- [x] `github_release` présent
- [x] Pas de `data_directory`

#### Test 3: Health check
```bash
curl http://localhost:8000/health
```
- [x] Retourne `{"status": "ok"}`

---

## 🚀 Étapes de Déploiement

### 1. Pousser le Code sur GitHub
```bash
cd "c:/Users/dM/Videos/Mazishark Final/dev/mazisharkfastapi"
git add .
git commit -m "feat: intégration GitHub Releases pour fichiers lourds"
git push origin main
```

### 2. Connecter à Vercel
1. Aller sur https://vercel.com
2. Cliquer sur "Add New Project"
3. Importer le repo GitHub
4. Configurer:
   - **Framework Preset**: Other
   - **Root Directory**: `mazisharkfastapi` (ou laisser vide si c'est la racine)
   - **Build Command**: (laisser vide)
   - **Output Directory**: (laisser vide)

### 3. Variables d'Environnement (optionnel)
Aucune variable obligatoire, mais possibles:
- `CACHE_DIR`: `/tmp/mazishark_cache` (défaut)
- `CORS_ALLOW_ORIGINS`: `*` (défaut)

### 4. Déployer
Cliquer sur "Deploy" et attendre ~2-3 minutes.

---

## 🧪 Tests Post-Déploiement

### URL de Production
Remplacer `YOUR_VERCEL_URL` par l'URL fournie par Vercel.

### Test 1: Health Check
```bash
curl https://YOUR_VERCEL_URL/health
```
**Attendu**: `{"status": "ok", "message": "MaziShark API is running"}`

### Test 2: Documentation
```bash
curl https://YOUR_VERCEL_URL/
```
**Attendu**: JSON avec liste des endpoints

### Test 3: Liste des Couches
```bash
curl https://YOUR_VERCEL_URL/data/layers
```
**Attendu**: JSON avec metadata des 5 couches

### Test 4: Téléchargement et Données
```bash
curl https://YOUR_VERCEL_URL/data/pace_chlor_a
```
**Attendu**: 
- Première requête: ~10-20 secondes (téléchargement)
- JSON avec lat, lon, values, stats

### Test 5: Carte PNG
```bash
curl https://YOUR_VERCEL_URL/data/sst_celsius/map -o sst_map.png
```
**Attendu**: Fichier PNG téléchargé

### Test 6: Prédiction
```bash
curl "https://YOUR_VERCEL_URL/predict?lat=-21.5&lon=55.5"
```
**Attendu**: JSON avec H_index

### Test 7: Hotspots
```bash
curl https://YOUR_VERCEL_URL/hotspots
```
**Attendu**: JSON avec liste des hotspots

---

## 🐛 Debugging sur Vercel

### Voir les Logs
1. Aller sur Vercel Dashboard
2. Sélectionner le projet
3. Onglet "Logs"
4. Filtrer par "Function Logs"

### Logs Attendus (Première Requête)
```
INFO: ☁️ [VERCEL] Téléchargement de metadata.json depuis GitHub Releases...
INFO: 📥 Téléchargement de metadata.json depuis https://github.com/...
INFO: ✅ Fichier metadata.json téléchargé avec succès (tentative 1/3)
INFO: ☁️ [VERCEL] Téléchargement de pace_chlor_a.nc depuis GitHub Releases...
INFO: 📥 Téléchargement de pace_chlor_a.nc depuis https://github.com/...
INFO: ✅ Fichier pace_chlor_a.nc téléchargé avec succès (tentative 1/3)
```

### Logs Attendus (Requêtes Suivantes)
```
INFO: ☁️ [VERCEL] Téléchargement de pace_chlor_a.nc depuis GitHub Releases...
INFO: ✅ Fichier pace_chlor_a.nc chargé depuis le cache local: /tmp/mazishark_cache/pace_chlor_a.nc
```

### Erreurs Communes

#### Erreur 1: "Internal Server Error"
**Cause**: Variable non définie (ex: `PROCESSED_DATA_DIR`)
**Solution**: Vérifier que toutes les variables sont définies

#### Erreur 2: "Fichier introuvable dans GitHub Release"
**Cause**: Fichier pas uploadé ou nom incorrect
**Solution**: Vérifier que tous les fichiers sont dans la release v5.0.0

#### Erreur 3: "Checksum invalide"
**Cause**: Fichier corrompu ou checksum incorrect
**Solution**: Re-télécharger le fichier ou corriger le checksum

#### Erreur 4: "Function Timeout"
**Cause**: Téléchargement trop long (>60s)
**Solution**: Augmenter le timeout ou réduire la taille des fichiers

#### Erreur 5: "Memory Limit Exceeded"
**Cause**: Trop de fichiers NetCDF en mémoire
**Solution**: Réduire le cache ou augmenter la mémoire Vercel

---

## 📊 Métriques de Performance

### Première Requête (Cold Start + Téléchargement)
- **Temps**: 15-30 secondes
- **Opérations**:
  1. Cold start Vercel (~2-3s)
  2. Téléchargement metadata.json (~1s)
  3. Téléchargement NetCDF (~10-20s)
  4. Chargement xarray (~2-3s)
  5. Traitement et réponse (~1s)

### Requêtes Suivantes (Cache Actif)
- **Temps**: 2-5 secondes
- **Opérations**:
  1. Vérification cache local (~0.1s)
  2. Chargement depuis cache mémoire (~0.5s)
  3. Traitement et réponse (~1-2s)

### Après Cold Start (Cache Perdu)
- **Temps**: 10-15 secondes
- **Opérations**:
  1. Cold start Vercel (~2-3s)
  2. Fichiers déjà en cache /tmp/ (~0.1s)
  3. Téléchargement si checksum invalide (~10s)
  4. Chargement xarray (~2-3s)
  5. Traitement et réponse (~1s)

---

## ⚠️ Limitations Vercel

### 1. Timeout
- **Limite**: 60 secondes (plan gratuit)
- **Impact**: Première requête peut timeout si téléchargement lent
- **Solution**: Passer au plan Pro (300s timeout)

### 2. Mémoire
- **Limite**: 1024 MB (plan gratuit)
- **Impact**: Peut être insuffisant pour plusieurs NetCDF en mémoire
- **Solution**: Réduire le cache ou passer au plan Pro (3008 MB)

### 3. Cache /tmp/
- **Limite**: Éphémère (perdu entre cold starts)
- **Impact**: Re-téléchargement après inactivité
- **Solution**: Accepter ou utiliser Redis externe

### 4. Bande Passante
- **Limite**: 100 GB/mois (plan gratuit)
- **Impact**: ~2000 téléchargements complets possibles
- **Solution**: Optimiser le cache ou passer au plan Pro

---

## ✅ Checklist Finale

### Avant Déploiement
- [x] Code testé localement
- [x] Pas de `PROCESSED_DATA_DIR` dans le code
- [x] `CACHE_DIR` et `GITHUB_RELEASE_URL` définis
- [x] Tous les fichiers dans GitHub Release v5.0.0
- [x] Checksums SHA256 corrects
- [x] vercel.json configuré correctement
- [x] requirements.txt à jour

### Après Déploiement
- [ ] Health check fonctionne
- [ ] Documentation accessible
- [ ] Liste des couches fonctionne
- [ ] Téléchargement et données fonctionnent
- [ ] Cartes PNG se génèrent
- [ ] Prédiction fonctionne
- [ ] Hotspots fonctionnent
- [ ] Logs Vercel propres (pas d'erreurs)
- [ ] Performance acceptable (<30s première requête)

### Frontend
- [ ] Mettre à jour l'URL de l'API dans `.env.local`
- [ ] Tester toutes les pages du frontend
- [ ] Vérifier que les cartes s'affichent
- [ ] Vérifier que les graphiques fonctionnent

---

## 🔗 Liens Utiles

- **GitHub Release**: https://github.com/DieuMerciMvemba/testapi/releases/tag/v5.0.0
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Documentation Vercel Python**: https://vercel.com/docs/functions/serverless-functions/runtimes/python

---

**Date**: 2025-10-08  
**Version**: 2.2.0  
**Status**: ✅ Prêt pour déploiement
