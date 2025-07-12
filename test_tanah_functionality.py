#!/usr/bin/env python3
"""
Test script untuk menguji fungsi prediksi tanah
"""

import requests
import json

# Test data untuk prediksi tanah
tanah_data = {
    'Kecamatan': 'Sukolilo',
    'Kelurahan': 'Keputih',
    'Luas Tanah': 200,
    'NJOP_Tanah_per_m2': 2500000,
    'Zona_Nilai_Tanah': '2',
    'Kelas_Tanah': 'B',
    'Jenis_Sertifikat': 'SHM',
    'model_type': 'random_forest'
}

def test_tanah_prediction():
    """Test prediksi tanah"""
    print("Testing tanah prediction...")
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/predict-tanah-price',
            json=tanah_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Tanah prediction successful!")
            print(f"Predicted price: Rp {result['prediction']:,.0f}")
            print(f"Price per m2: Rp {result['price_per_m2']:,.0f}")
            print(f"Model used: {result['model_used']}")
            print(f"Confidence: {result['confidence']:.1f}%")
            return result
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_save_tanah_prediction(prediction_result):
    """Test menyimpan prediksi tanah"""
    print("\nTesting save tanah prediction...")
    
    if not prediction_result:
        print("❌ No prediction result to save")
        return False
    
    save_data = {
        **tanah_data,
        'prediction': prediction_result['prediction'],
        'price_per_m2': prediction_result['price_per_m2'],
        'model_used': prediction_result['model_used'],
        'confidence': prediction_result['confidence']
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/save-tanah-prediction',
            json=save_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Tanah prediction saved successfully!")
            print(f"Asset ID: {result['asset_id']}")
            return result['asset_id']
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_tanah_list():
    """Test mendapatkan daftar tanah"""
    print("\nTesting tanah list...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/tanah-list')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Tanah list retrieved successfully!")
            print(f"Total assets: {len(result['data'])}")
            if result['data']:
                first_asset = result['data'][0]
                price = first_asset['harga_prediksi_tanah']
                if isinstance(price, str):
                    price = float(price)
                print(f"First asset: {first_asset['kecamatan']} - Rp {price:,.0f}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_compare_tanah_models():
    """Test perbandingan model tanah"""
    print("\nTesting tanah model comparison...")
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/predict-tanah-all-models',
            json=tanah_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Tanah model comparison successful!")
            for model, prediction in result['predictions'].items():
                if 'error' not in prediction:
                    print(f"{model}: Rp {prediction['prediction']:,.0f} ({prediction['confidence']:.1f}%)")
                else:
                    print(f"{model}: Error - {prediction['error']}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Main test function"""
    print("=== Testing Tanah Prediction Functionality ===\n")
    
    # Test 1: Prediksi tanah
    prediction_result = test_tanah_prediction()
    
    # Test 2: Simpan prediksi
    if prediction_result:
        asset_id = test_save_tanah_prediction(prediction_result)
    
    # Test 3: Ambil daftar tanah
    test_tanah_list()
    
    # Test 4: Bandingkan model
    test_compare_tanah_models()
    
    print("\n=== Test completed! ===")

if __name__ == "__main__":
    main()
