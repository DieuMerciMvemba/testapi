"""
Tests pour l'API MaziShark déployée sur Vercel
URL: https://testapi-theta.vercel.app/
By Mvemba Tsimba DieuMerci
"""

import requests
import json 

# Configuration
BASE_URL = "https://testapi-theta.vercel.app"

def test_root():
    """Test endpoint racine /"""
    print("\n" + "="*60)
    print("TEST 1: GET /")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Name: {data.get('name')}")
        print(f"✅ Version: {data.get('version')}")
        print(f"✅ Available layers: {len(data.get('available_layers', []))}")
        print(f"   Layers: {', '.join(data.get('available_layers', []))}")
    else:
        print(f"❌ Erreur: {response.text}")
    
    return response.status_code == 200


def test_health():
    """Test endpoint /health"""
    print("\n" + "="*60)
    print("TEST 2: GET /health")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {data.get('status')}")
        print(f"✅ Message: {data.get('message')}")
    else:
        print(f"❌ Erreur: {response.text}")
    
    return response.status_code == 200


def test_layers():
    """Test endpoint /data/layers"""
    print("\n" + "="*60)
    print("TEST 3: GET /data/layers")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/data/layers")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Nombre de couches: {data.get('count')}")
        print(f"✅ Description: {data.get('description')}")
        
        layers = data.get('layers', {})
        for layer_name, layer_info in layers.items():
            print(f"   - {layer_name}: {layer_info.get('description')} ({layer_info.get('size_MB')} MB)")
    else:
        print(f"❌ Erreur: {response.text}")
    
    return response.status_code == 200


def test_habitat():
    """Test endpoint /data/habitat"""
    print("\n" + "="*60)
    print("TEST 4: GET /data/habitat")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/data/habitat")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Type: {data.get('type')}")
        features = data.get('features', [])
        print(f"✅ Nombre de features: {len(features)}")
        if len(features) > 0:
            print(f"   Premier feature: {features[0].get('type')}")
    else:
        print(f"❌ Erreur: {response.text}")
    
    return response.status_code == 200


def test_layer_data():
    """Test endpoint /data/{layer_name}"""
    print("\n" + "="*60)
    print("TEST 5: GET /data/habitat_index_H")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/data/habitat_index_H?sample=true&max_points=1000")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Layer: {data.get('layer')}")
        print(f"✅ Variable: {data.get('variable')}")
        print(f"✅ Units: {data.get('units')}")
        print(f"✅ Shape: {data.get('shape')}")
        print(f"✅ Sampled: {data.get('sampled')}")
        print(f"✅ Sampling factor: {data.get('sampling_factor')}")
        
        stats = data.get('stats', {})
        print(f"✅ Stats:")
        print(f"   - Min: {stats.get('min')}")
        print(f"   - Max: {stats.get('max')}")
        print(f"   - Mean: {stats.get('mean')}")
    else:
        print(f"❌ Erreur: {response.text}")
    
    return response.status_code == 200


def test_predict():
    """Test endpoint /predict"""
    print("\n" + "="*60)
    print("TEST 6: GET /predict?lat=49.0&lon=-22.5")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/predict?lat=49.0&lon=-22.5")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Latitude: {data.get('lat')}")
        print(f"✅ Longitude: {data.get('lon')}")
        print(f"✅ H_index: {data.get('H_index')}")
        print(f"✅ Nearest lat: {data.get('nearest_lat')}")
        print(f"✅ Nearest lon: {data.get('nearest_lon')}")
        print(f"✅ Interpretation: {data.get('interpretation')}")
    else:
        print(f"❌ Erreur: {response.text}")
    
    return response.status_code == 200


def test_hotspots():
    """Test endpoint /hotspots"""
    print("\n" + "="*60)
    print("TEST 7: GET /hotspots")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/hotspots")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Nombre de hotspots: {data.get('count')}")
        print(f"✅ Description: {data.get('description')}")
        
        hotspots = data.get('hotspots', [])
        if len(hotspots) > 0:
            print(f"\n   Top 5 hotspots:")
            for i, hotspot in enumerate(hotspots[:5], 1):
                print(f"   {i}. Lat: {hotspot.get('lat')}, Lon: {hotspot.get('lon')}, H: {hotspot.get('H')}")
    else:
        print(f"❌ Erreur: {response.text}")
    
    return response.status_code == 200


def test_layer_map():
    """Test endpoint /data/{layer_name}/map"""
    print("\n" + "="*60)
    print("TEST 8: GET /data/habitat_index_H/map")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/data/habitat_index_H/map?cmap=viridis")
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        print(f"✅ Image PNG reçue ({len(response.content)} bytes)")
        
        # Sauvegarder l'image
        with open("test/habitat_map.png", "wb") as f:
            f.write(response.content)
        print(f"✅ Image sauvegardée: test/habitat_map.png")
    else:
        print(f"❌ Erreur: {response.text}")
    
    return response.status_code == 200


def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "🦈"*30)
    print("TESTS API MAZISHARK - https://testapi-theta.vercel.app/")
    print("🦈"*30)
    
    results = {
        "Root endpoint": test_root(),
        "Health check": test_health(),
        "Layers list": test_layers(),
        "Habitat GeoJSON": test_habitat(),
        "Layer data": test_layer_data(),
        "Predict": test_predict(),
        "Hotspots": test_hotspots(),
        "Layer map": test_layer_map(),
    }
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "-"*60)
    print(f"Total: {total} tests")
    print(f"✅ Réussis: {passed}")
    print(f"❌ Échoués: {failed}")
    print(f"Taux de réussite: {(passed/total)*100:.1f}%")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
