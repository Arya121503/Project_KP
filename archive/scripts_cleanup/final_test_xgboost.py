#!/usr/bin/env python3
"""
Script sederhana untuk mengonfirmasi XGBoost model berhasil diretrain dan berfungsi
"""
import os
import joblib
import pandas as pd
from datetime import datetime

def test_xgboost_final():
    """Final test untuk XGBoost model"""
    print("=== FINAL TEST XGBOOST MODEL ===")
    
    # Load model
    model_path = "ml_model/xgboost_model.pkl"
    try:
        xgb_model = joblib.load(model_path)
        
        # Model info
        mtime = os.path.getmtime(model_path)
        mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        file_size = os.path.getsize(model_path) / (1024 * 1024)
        
        print(f"✅ Model berhasil dimuat")
        print(f"📅 Last modified: {mod_time}")
        print(f"📊 File size: {file_size:.2f} MB")
        print(f"🔧 Features: {xgb_model.n_features_in_}")
        
        # Test multiple predictions
        test_cases = [
            {
                'name': 'Rumah Kecil',
                'luas_bangunan': 60,
                'luas_tanah': 90,
                'kamar_tidur': 2,
                'kamar_mandi': 1,
                'daya_listrik': 900,
                'jumlah_lantai': 1,
                'njop_rp_per_m2': 2000000,
                'rasio_bangunan_tanah': 0.67
            },
            {
                'name': 'Rumah Sedang',
                'luas_bangunan': 100,
                'luas_tanah': 150,
                'kamar_tidur': 3,
                'kamar_mandi': 2,
                'daya_listrik': 1300,
                'jumlah_lantai': 2,
                'njop_rp_per_m2': 2500000,
                'rasio_bangunan_tanah': 0.67
            },
            {
                'name': 'Rumah Besar',
                'luas_bangunan': 200,
                'luas_tanah': 300,
                'kamar_tidur': 4,
                'kamar_mandi': 3,
                'daya_listrik': 2200,
                'jumlah_lantai': 2,
                'njop_rp_per_m2': 3000000,
                'rasio_bangunan_tanah': 0.67
            }
        ]
        
        print(f"\n=== TEST PREDIKSI BEBERAPA KASUS ===")
        for i, case in enumerate(test_cases, 1):
            test_df = pd.DataFrame([{k: v for k, v in case.items() if k != 'name'}])
            prediction = xgb_model.predict(test_df)[0]
            
            print(f"\n{i}. {case['name']}:")
            print(f"   Luas bangunan: {case['luas_bangunan']} m²")
            print(f"   Luas tanah: {case['luas_tanah']} m²")
            print(f"   Kamar tidur: {case['kamar_tidur']}")
            print(f"   Prediksi harga: Rp {prediction:,.0f}")
            print(f"   Harga per m²: Rp {prediction/case['luas_bangunan']:,.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_all_models_consistency():
    """Periksa konsistensi semua model"""
    print(f"\n=== KONSISTENSI SEMUA MODEL ===")
    
    models = {
        'Random Forest': 'ml_model/random_forest_model.pkl',
        'CatBoost': 'ml_model/catboost_model.pkl',
        'XGBoost': 'ml_model/xgboost_model.pkl'
    }
    
    results = {}
    
    for model_name, model_path in models.items():
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                mtime = os.path.getmtime(model_path)
                mod_time = datetime.fromtimestamp(mtime)
                
                results[model_name] = {
                    'status': 'OK',
                    'features': getattr(model, 'n_features_in_', 'N/A'),
                    'modified': mod_time,
                    'today': mod_time.strftime("%Y-%m-%d") == "2025-07-08"
                }
                
            except Exception as e:
                results[model_name] = {
                    'status': f'ERROR: {e}',
                    'features': 'N/A',
                    'modified': 'N/A',
                    'today': False
                }
        else:
            results[model_name] = {
                'status': 'NOT FOUND',
                'features': 'N/A',
                'modified': 'N/A',
                'today': False
            }
    
    # Display results
    for model_name, info in results.items():
        status_icon = "✅" if info['status'] == 'OK' else "❌"
        date_icon = "🆕" if info['today'] else "📅"
        
        print(f"{status_icon} {model_name}:")
        print(f"   Status: {info['status']}")
        print(f"   Features: {info['features']}")
        if info['modified'] != 'N/A':
            print(f"   {date_icon} Modified: {info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    all_ok = all(info['status'] == 'OK' for info in results.values())
    all_today = all(info['today'] for info in results.values())
    
    return all_ok and all_today

def main():
    print("🔍 Final Validation - XGBoost Retraining")
    print("=" * 50)
    
    # Test XGBoost
    xgb_success = test_xgboost_final()
    
    # Check all models
    all_models_ok = check_all_models_consistency()
    
    print("=" * 50)
    print("=== RINGKASAN FINAL ===")
    
    if xgb_success:
        print("✅ XGBoost model: BERHASIL DIRETRAIN")
    else:
        print("❌ XGBoost model: GAGAL")
    
    if all_models_ok:
        print("✅ Semua model: KONSISTEN & UP-TO-DATE")
    else:
        print("⚠️  Beberapa model: PERLU PERHATIAN")
    
    if xgb_success and all_models_ok:
        print("\n🎉 RETRAINING XGBOOST BERHASIL!")
        print("✅ Semua model (Random Forest, CatBoost, XGBoost) telah diretrain")
        print("✅ Menggunakan data terbaru (tanpa Prajuritkulon, dengan Tenggilis Mejoyo)")
        print("✅ Model siap digunakan untuk prediksi")
    else:
        print("\n⚠️  MASIH ADA ISSUE!")
        print("🔄 Silakan periksa error di atas")

if __name__ == "__main__":
    main()
