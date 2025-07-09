#!/usr/bin/env python3
"""
Script untuk mengecek status model files dan verifikasi kebutuhan retraining
"""
import os
import joblib
from datetime import datetime

def check_model_files():
    """Check status of model files"""
    print("=== MODEL FILES STATUS ===")
    
    model_dir = "ml_model"
    models = ['random_forest_model.pkl', 'catboost_model.pkl', 'xgboost_model.pkl']
    
    for model_name in models:
        model_path = os.path.join(model_dir, model_name)
        if os.path.exists(model_path):
            # Get modification time
            mtime = os.path.getmtime(model_path)
            mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            # Get file size
            file_size = os.path.getsize(model_path)
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"✅ {model_name}")
            print(f"   📅 Modified: {mod_time}")
            print(f"   📊 Size: {file_size_mb:.2f} MB")
            
            # Try to load model and check basic info
            try:
                model = joblib.load(model_path)
                if hasattr(model, 'feature_names_in_'):
                    print(f"   🔧 Features: {len(model.feature_names_in_)} features")
                elif hasattr(model, 'n_features_in_'):
                    print(f"   🔧 Features: {model.n_features_in_} features")
                else:
                    print(f"   🔧 Features: Available")
            except Exception as e:
                print(f"   ❌ Error loading model: {e}")
        else:
            print(f"❌ {model_name}: Not found")
        print()

def check_data_status():
    """Check current data status"""
    print("=== DATA STATUS ===")
    
    # Check CSV file
    csv_file = "data/raw/dataset_tanah_njop_surabaya_sertifikat.csv"
    if os.path.exists(csv_file):
        import pandas as pd
        df = pd.read_csv(csv_file)
        
        print(f"✅ Dataset: {len(df)} records")
        print(f"✅ Kecamatan: {df['kecamatan'].nunique()} unique districts")
        
        # Check if Prajuritkulon exists
        prajurit_count = df['kecamatan'].str.contains('prajurit', case=False, na=False).sum()
        if prajurit_count > 0:
            print(f"⚠️  Prajuritkulon data found: {prajurit_count} records")
        else:
            print("✅ No Prajuritkulon data found")
            
        # Check Tenggilis Mejoyo
        tenggilis_count = df['kecamatan'].str.contains('tenggilis', case=False, na=False).sum()
        print(f"✅ Tenggilis Mejoyo data: {tenggilis_count} records")
        
        # Get data modification time
        mtime = os.path.getmtime(csv_file)
        mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"📅 Data last modified: {mod_time}")
        
    else:
        print("❌ Dataset not found")

def check_comparison_file():
    """Check model comparison file"""
    print("=== MODEL COMPARISON STATUS ===")
    
    comp_file = "ml_model/model_comparison.csv"
    if os.path.exists(comp_file):
        import pandas as pd
        df = pd.read_csv(comp_file)
        
        print(f"✅ Comparison file exists with {len(df)} models")
        print("📊 Model performance:")
        for _, row in df.iterrows():
            print(f"   {row['Model']}: R² = {row['R2_Test']:.4f}")
            if 'Retrain_Date' in row:
                print(f"   Last retrain: {row['Retrain_Date']}")
        
        # Check file modification time
        mtime = os.path.getmtime(comp_file)
        mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"📅 Comparison file last modified: {mod_time}")
    else:
        print("❌ Model comparison file not found")

def assess_retraining_need():
    """Assess if retraining is needed"""
    print("=== RETRAINING ASSESSMENT ===")
    
    # Check if data was modified after models
    csv_file = "data/raw/dataset_tanah_njop_surabaya_sertifikat.csv"
    model_file = "ml_model/random_forest_model.pkl"
    
    if os.path.exists(csv_file) and os.path.exists(model_file):
        data_mtime = os.path.getmtime(csv_file)
        model_mtime = os.path.getmtime(model_file)
        
        data_time = datetime.fromtimestamp(data_mtime)
        model_time = datetime.fromtimestamp(model_mtime)
        
        print(f"📊 Data last modified: {data_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 Model last modified: {model_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if data_mtime > model_mtime:
            print("⚠️  DATA IS NEWER THAN MODEL - RETRAINING RECOMMENDED")
            return True
        else:
            print("✅ Model is up-to-date with current data")
            return False
    else:
        print("❌ Cannot compare timestamps - files missing")
        return True

if __name__ == "__main__":
    print("🔍 Checking model and data status...")
    print("=" * 60)
    
    check_model_files()
    check_data_status()
    check_comparison_file()
    
    print("=" * 60)
    needs_retraining = assess_retraining_need()
    
    if needs_retraining:
        print("🔄 RECOMMENDATION: Retraining needed")
    else:
        print("✅ RECOMMENDATION: No retraining needed - models are current")
    
    print("=" * 60)
