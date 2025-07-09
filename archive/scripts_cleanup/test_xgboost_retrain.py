#!/usr/bin/env python3
"""
Script untuk test dan validasi model XGBoo        # Test predict_price method
        test_data = {
            'luas_bangunan': 100,
            'luas_tanah': 150,
            'kamar_tidur': 3,
            'kamar_mandi': 2,
            'daya_listrik': 1300,
            'jumlah_lantai': 2,
            'njop_rp_per_m2': 2500000,
            'kecamatan': 'Gubeng'
        }ru diretrain
"""
import os
import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_xgboost_model():
    """Test XGBoost model yang baru diretrain"""
    print("=== TEST XGBOOST MODEL BARU ===")
    
    # Load model
    model_path = "ml_model/xgboost_model.pkl"
    if not os.path.exists(model_path):
        print("❌ Model XGBoost tidak ditemukan")
        return False
    
    try:
        xgb_model = joblib.load(model_path)
        
        # Get model info
        mtime = os.path.getmtime(model_path)
        mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        file_size = os.path.getsize(model_path) / (1024 * 1024)
        
        print(f"✅ Model XGBoost berhasil dimuat")
        print(f"📅 Last modified: {mod_time}")
        print(f"📊 File size: {file_size:.2f} MB")
        print(f"🔧 Features: {xgb_model.n_features_in_}")
        
        # Test prediction dengan data dummy
        print("\n=== TEST PREDIKSI ===")
        
        # Create dummy data matching expected features
        test_data = pd.DataFrame({
            'luas_bangunan': [100],
            'luas_tanah': [150],
            'kamar_tidur': [3],
            'kamar_mandi': [2],
            'daya_listrik': [1300],
            'jumlah_lantai': [2],
            'njop_rp_per_m2': [2500000],
            'rasio_bangunan_tanah': [0.67]
        })
        
        prediction = xgb_model.predict(test_data)
        print(f"✅ Test prediction berhasil: Rp {prediction[0]:,.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

def test_prediction_models_integration():
    """Test integrasi dengan prediction_models.py"""
    print("\n=== TEST INTEGRASI PREDICTION MODELS ===")
    
    try:
        from app.prediction_models import PrediksiPropertiTanah
        
        # Create prediction model instance
        pred_model = PrediksiPropertiTanah()
        
        # Test prediction dengan data contoh
        test_data = {
            'luas_bangunan_m2': 100,
            'luas_tanah_m2': 150,
            'jumlah_kamar_tidur': 3,
            'jumlah_kamar_mandi': 2,
            'jumlah_garasi': 1,
            'tahun_dibangun': 2015,
            'kecamatan': 'Gubeng'
        }
        
        # Test predict_price method
        result = pred_model.predict_price(test_data)
        
        if result['success']:
            print(f"✅ Prediksi harga berhasil: Rp {result['predicted_price']:,.0f}")
            print(f"📊 Model digunakan: {result['model_used']}")
            print(f"🔧 Confidence: {result['confidence']:.2f}")
            return True
        else:
            print(f"❌ Prediksi gagal: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing integration: {e}")
        return False

def validate_all_models():
    """Validasi semua model sudah up-to-date"""
    print("\n=== VALIDASI SEMUA MODEL ===")
    
    models = {
        'Random Forest': 'ml_model/random_forest_model.pkl',
        'CatBoost': 'ml_model/catboost_model.pkl',
        'XGBoost': 'ml_model/xgboost_model.pkl'
    }
    
    all_valid = True
    
    for model_name, model_path in models.items():
        if os.path.exists(model_path):
            mtime = os.path.getmtime(model_path)
            mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if model is from today (indicating recent retrain)
            if mod_time.startswith("2025-07-08"):
                print(f"✅ {model_name}: Up-to-date ({mod_time})")
            else:
                print(f"⚠️  {model_name}: Older model ({mod_time})")
                all_valid = False
        else:
            print(f"❌ {model_name}: Not found")
            all_valid = False
    
    return all_valid

def main():
    print("🔍 Validasi Model XGBoost yang Baru Diretrain")
    print("=" * 60)
    
    # Test XGBoost model
    xgb_test = test_xgboost_model()
    
    # Test integration
    integration_test = test_prediction_models_integration()
    
    # Validate all models
    all_models_valid = validate_all_models()
    
    print("\n" + "=" * 60)
    print("=== RINGKASAN VALIDASI ===")
    
    if xgb_test:
        print("✅ XGBoost model: VALID")
    else:
        print("❌ XGBoost model: INVALID")
    
    if integration_test:
        print("✅ Integrasi sistem: VALID")
    else:
        print("❌ Integrasi sistem: INVALID")
    
    if all_models_valid:
        print("✅ Semua model: UP-TO-DATE")
    else:
        print("⚠️  Beberapa model: PERLU UPDATE")
    
    overall_status = xgb_test and integration_test and all_models_valid
    
    if overall_status:
        print("\n🎉 SEMUA VALIDASI BERHASIL!")
        print("✅ XGBoost model siap digunakan")
        print("✅ Semua model konsisten dengan data terbaru")
        print("✅ Sistem siap untuk produksi")
    else:
        print("\n⚠️  BEBERAPA VALIDASI GAGAL!")
        print("🔄 Silakan periksa issue di atas")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
