# Script PowerShell de test pour l'API MaziShark
# URL: https://testapi-theta.vercel.app/

$BASE_URL = "https://testapi-theta.vercel.app"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "TESTS API MAZISHARK" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Root
Write-Host "TEST 1: GET /" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/" -Method Get
$response | ConvertTo-Json -Depth 3
Write-Host ""

# Test 2: Health
Write-Host "TEST 2: GET /health" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get
$response | ConvertTo-Json
Write-Host ""

# Test 3: Layers
Write-Host "TEST 3: GET /data/layers" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/data/layers" -Method Get
Write-Host "Nombre de couches: $($response.count)"
$response.layers.PSObject.Properties.Name
Write-Host ""

# Test 4: Habitat
Write-Host "TEST 4: GET /data/habitat" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/data/habitat" -Method Get
Write-Host "Type: $($response.type)"
Write-Host "Nombre de features: $($response.features.Count)"
Write-Host ""

# Test 5: Layer data
Write-Host "TEST 5: GET /data/habitat_index_H" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/data/habitat_index_H?sample=true&max_points=1000" -Method Get
Write-Host "Layer: $($response.layer)"
Write-Host "Shape: $($response.shape)"
Write-Host "Stats: Min=$($response.stats.min), Max=$($response.stats.max), Mean=$($response.stats.mean)"
Write-Host ""

# Test 6: Predict
Write-Host "TEST 6: GET /predict?lat=49.0&lon=-22.5" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/predict?lat=49.0&lon=-22.5" -Method Get
$response | ConvertTo-Json
Write-Host ""

# Test 7: Hotspots
Write-Host "TEST 7: GET /hotspots" -ForegroundColor Yellow
$response = Invoke-RestMethod -Uri "$BASE_URL/hotspots" -Method Get
Write-Host "Nombre de hotspots: $($response.count)"
Write-Host "Top 3:"
$response.hotspots[0..2] | Format-Table rank, lat, lon, H
Write-Host ""

# Test 8: Map (télécharge l'image)
Write-Host "TEST 8: GET /data/habitat_index_H/map" -ForegroundColor Yellow
$outputPath = "test\habitat_map.png"
Invoke-WebRequest -Uri "$BASE_URL/data/habitat_index_H/map?cmap=viridis" -OutFile $outputPath
Write-Host "✅ Image sauvegardée: $outputPath" -ForegroundColor Green
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "TESTS TERMINÉS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
