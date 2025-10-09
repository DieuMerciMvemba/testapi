#!/bin/bash

# Script de test pour l'API MaziShark
# URL: https://testapi-theta.vercel.app/

BASE_URL="https://testapi-theta.vercel.app"

echo "=========================================="
echo "TESTS API MAZISHARK"
echo "=========================================="
echo ""

# Test 1: Root
echo "TEST 1: GET /"
curl -s "$BASE_URL/" | jq '.'
echo ""

# Test 2: Health
echo "TEST 2: GET /health"
curl -s "$BASE_URL/health" | jq '.'
echo ""

# Test 3: Layers
echo "TEST 3: GET /data/layers"
curl -s "$BASE_URL/data/layers" | jq '.count, .layers | keys'
echo ""

# Test 4: Habitat
echo "TEST 4: GET /data/habitat"
curl -s "$BASE_URL/data/habitat" | jq '.type, .features | length'
echo ""

# Test 5: Layer data
echo "TEST 5: GET /data/habitat_index_H"
curl -s "$BASE_URL/data/habitat_index_H?sample=true&max_points=1000" | jq '.layer, .shape, .stats'
echo ""

# Test 6: Predict
echo "TEST 6: GET /predict?lat=49.0&lon=-22.5"
curl -s "$BASE_URL/predict?lat=49.0&lon=-22.5" | jq '.'
echo ""

# Test 7: Hotspots
echo "TEST 7: GET /hotspots"
curl -s "$BASE_URL/hotspots" | jq '.count, .hotspots[:3]'
echo ""

# Test 8: Map (télécharge l'image)
echo "TEST 8: GET /data/habitat_index_H/map"
curl -s "$BASE_URL/data/habitat_index_H/map?cmap=viridis" -o test/habitat_map.png
echo "✅ Image sauvegardée: test/habitat_map.png"
echo ""

echo "=========================================="
echo "TESTS TERMINÉS"
echo "=========================================="
