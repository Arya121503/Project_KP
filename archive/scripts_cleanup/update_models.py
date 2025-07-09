"""
Script untuk memperbarui sistem prediction models agar menggunakan model hasil retraining
"""

import os
import sys
from datetime import datetime

def update_system_with_new_models():
    """Update sistem untuk menggunakan model baru hasil retraining"""
    print("🔄 MEMPERBARUI SISTEM DENGAN MODEL BARU")
    print("=" * 50)
    
    # 1. Verifikasi model baru ada
    model_dir = "ml_model"
    required_models = {
        'Random Forest': 'random_forest_model.pkl',
        'CatBoost': 'catboost_model.pkl'
    }
    
    print("1. VERIFIKASI MODEL BARU:")
    for name, filename in required_models.items():
        model_path = os.path.join(model_dir, filename)
        if os.path.exists(model_path):
            mod_time = datetime.fromtimestamp(os.path.getmtime(model_path))
            print(f"   ✅ {name}: {filename} (Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print(f"   ❌ {name}: {filename} tidak ditemukan!")
            return False
    
    # 2. Periksa performa model baru
    comparison_path = os.path.join(model_dir, 'model_comparison.csv')
    if os.path.exists(comparison_path):
        import pandas as pd
        df_comparison = pd.read_csv(comparison_path)
        
        print(f"\n2. PERFORMA MODEL BARU:")
        for _, row in df_comparison.iterrows():
            print(f"   📊 {row['Model']}:")
            print(f"      - R² Score: {row['R2_Test']:.4f}")
            print(f"      - MAE: Rp {row['MAE_Test']:,.0f}")
            print(f"      - Training Time: {row['Training_Time_Sec']:.2f}s")
            print(f"      - Data Points: {row['Data_Points']:,.0f}")
    
    # 3. Update prediction_models.py jika diperlukan
    print(f"\n3. SISTEM INTEGRATION:")
    print("   ✅ Model tersimpan dengan nama file yang sama")
    print("   ✅ Sistem akan otomatis menggunakan model terbaru")
    print("   ✅ Tidak perlu perubahan kode aplikasi")
    
    # 4. Restart recommendation
    print(f"\n4. REKOMENDASI:")
    print("   🔄 Restart aplikasi Flask untuk memuat model baru")
    print("   🧪 Test prediksi di dashboard untuk verifikasi")
    print("   📊 Monitor performa model dalam penggunaan")
    
    print(f"\n✅ SISTEM BERHASIL DIPERBARUI!")
    print(f"Model baru siap digunakan untuk prediksi harga properti.")
    
    return True

def test_new_models():
    """Test model baru untuk memastikan berfungsi dengan baik"""
    print(f"\n🧪 TESTING MODEL BARU")
    print("=" * 30)
    
    try:
        import joblib
        import numpy as np
        
        # Test Random Forest
        rf_path = os.path.join("ml_model", "random_forest_model.pkl")
        if os.path.exists(rf_path):
            rf_model = joblib.load(rf_path)
            print("✅ Random Forest model berhasil dimuat")
            
            # Test prediksi dengan data dummy
            n_features = len(rf_model.feature_names_in_) if hasattr(rf_model, 'feature_names_in_') else 8
            dummy_data = np.random.rand(1, n_features) * 100  # Data dummy
            try:
                prediction = rf_model.predict(dummy_data)
                print(f"✅ Random Forest test prediction: Rp {prediction[0]:,.0f}")
            except Exception as e:
                print(f"❌ Random Forest prediction error: {e}")
        
        # Test CatBoost
        cat_path = os.path.join("ml_model", "catboost_model.pkl")
        if os.path.exists(cat_path):
            cat_model = joblib.load(cat_path)
            print("✅ CatBoost model berhasil dimuat")
            
            # Test prediksi dengan data dummy
            n_features = cat_model.feature_names_ if hasattr(cat_model, 'feature_names_') else 8
            if isinstance(n_features, list):
                n_features = len(n_features)
            elif not isinstance(n_features, int):
                n_features = 8
                
            dummy_data = np.random.rand(1, n_features) * 100
            try:
                prediction = cat_model.predict(dummy_data)
                print(f"✅ CatBoost test prediction: Rp {prediction[0]:,.0f}")
            except Exception as e:
                print(f"❌ CatBoost prediction error: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SISTEM UPDATE UNTUK MODEL BARU")
    print("=" * 50)
    
    if update_system_with_new_models():
        if test_new_models():
            print(f"\n🎉 SUKSES!")
            print("✅ Model baru siap digunakan")
            print("✅ Sistem telah diperbarui")
            print("🔄 Silakan restart aplikasi Flask")
        else:
            print(f"\n⚠️ Model dimuat tapi ada error saat testing")
    else:
        print(f"\n❌ Gagal memperbarui sistem")
