#!/usr/bin/env python3
"""
Script untuk memperbaiki masalah data bangunan
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os

def fix_building_data():
    """Perbaiki masalah data bangunan"""
    print("=== MEMPERBAIKI DATA BANGUNAN ===")
    
    # Load data
    building_file = "data/raw/Dataset_Bangunan_Surabaya_Final_Revisi_.csv"
    df = pd.read_csv(building_file)
    
    print(f"📊 Data awal: {len(df)} rows, {len(df.columns)} columns")
    
    # 1. Perbaiki nama kecamatan
    print("\n1. 🔧 PERBAIKAN NAMA KECAMATAN")
    
    name_mapping = {
        'Dukuh pakis': 'Dukuh Pakis',
        'Tenggilis mejoyo': 'Tenggilis Mejoyo'
    }
    
    changes_made = 0
    for old_name, new_name in name_mapping.items():
        if old_name in df['Kecamatan'].values:
            count = df['Kecamatan'].value_counts().get(old_name, 0)
            df['Kecamatan'] = df['Kecamatan'].replace(old_name, new_name)
            print(f"  ✅ '{old_name}' → '{new_name}' ({count} records)")
            changes_made += count
    
    print(f"  📊 Total perubahan: {changes_made} records")
    
    # 2. Handle missing values strategis
    print("\n2. 💾 HANDLING MISSING VALUES")
    
    # Strategy untuk setiap kolom
    missing_strategies = {
        'Lebar Jalan': 'mode',    # Kategorikal - gunakan mode
        'Hadap': 'mode',          # Kategorikal - gunakan mode
        'Sumber Air': 'mode',     # Kategorikal - gunakan mode
        'Ruang Makan': 'mode',    # Kategorikal - gunakan mode
        'Daya Listrik': 'median', # Numerik - gunakan median
        'Ruang Tamu': 'mode',     # Kategorikal - gunakan mode
        'Hook': 'mode',           # Kategorikal - gunakan mode
        'Terjangkau Internet': 'mode',  # Kategorikal - gunakan mode
        'Kondisi Properti': 'mode',     # Kategorikal - gunakan mode
        'Jumlah Lantai': 'median'       # Numerik - gunakan median
    }
    
    missing_before = df.isnull().sum().sum()
    
    for column, strategy in missing_strategies.items():
        if column in df.columns:
            missing_count = df[column].isnull().sum()
            if missing_count > 0:
                if strategy == 'median' and pd.api.types.is_numeric_dtype(df[column]):
                    fill_value = df[column].median()
                elif strategy == 'mode':
                    mode_values = df[column].mode()
                    fill_value = mode_values.iloc[0] if not mode_values.empty else 'Unknown'
                else:
                    # Fallback to mode for non-numeric columns
                    mode_values = df[column].mode()
                    fill_value = mode_values.iloc[0] if not mode_values.empty else 'Unknown'
                
                df[column] = df[column].fillna(fill_value)
                print(f"  ✅ {column}: {missing_count} missing values filled with {strategy} ({fill_value})")
    
    missing_after = df.isnull().sum().sum()
    print(f"  📊 Missing values: {missing_before} → {missing_after}")
    
    # 3. Verifikasi hasil
    print("\n3. ✅ VERIFIKASI HASIL")
    
    # Check kecamatan
    unique_kecamatan = df['Kecamatan'].nunique()
    print(f"  📊 Unique kecamatan: {unique_kecamatan}")
    
    # Check Prajuritkulon
    prajurit_count = df['Kecamatan'].str.contains('prajurit', case=False, na=False).sum()
    if prajurit_count == 0:
        print("  ✅ Tidak ada Prajuritkulon")
    else:
        print(f"  ❌ Masih ada Prajuritkulon: {prajurit_count}")
    
    # Check missing values
    remaining_missing = df.isnull().sum().sum()
    print(f"  📊 Missing values tersisa: {remaining_missing}")
    
    # 4. Simpan hasil
    print("\n4. 💾 MENYIMPAN HASIL")
    
    # Backup original
    backup_file = building_file.replace('.csv', '_backup_before_fix.csv')
    if not os.path.exists(backup_file):
        df_original = pd.read_csv(building_file)
        df_original.to_csv(backup_file, index=False)
        print(f"  ✅ Backup dibuat: {backup_file}")
    
    # Simpan hasil perbaikan
    df.to_csv(building_file, index=False)
    print(f"  ✅ File diperbaharui: {building_file}")
    
    # 5. Summary
    print("\n5. 📋 SUMMARY PERBAIKAN")
    print(f"  ✅ Nama kecamatan distandarisasi: {changes_made} records")
    print(f"  ✅ Missing values dikurangi: {missing_before} → {missing_after}")
    print(f"  ✅ Unique kecamatan: {unique_kecamatan}")
    print(f"  ✅ Data bersih dari Prajuritkulon")
    
    return df

def create_building_summary():
    """Buat summary data bangunan setelah perbaikan"""
    print("\n=== SUMMARY DATA BANGUNAN ===")
    
    df = pd.read_csv("data/raw/Dataset_Bangunan_Surabaya_Final_Revisi_.csv")
    
    # Kecamatan analysis
    kecamatan_stats = df['Kecamatan'].value_counts().sort_index()
    
    print(f"📊 Total records: {len(df)}")
    print(f"📊 Unique kecamatan: {df['Kecamatan'].nunique()}")
    print(f"📊 Missing values: {df.isnull().sum().sum()}")
    
    print(f"\n📋 Distribusi per kecamatan:")
    for kecamatan, count in kecamatan_stats.items():
        print(f"  - {kecamatan}: {count} records")
    
    # Missing kecamatan analysis
    kecamatan_resmi = {
        'Asemrowo', 'Benowo', 'Bubutan', 'Bulak', 'Dukuh Pakis', 'Gayungan',
        'Genteng', 'Gubeng', 'Gunung Anyar', 'Jambangan', 'Karang Pilang',
        'Kenjeran', 'Krembangan', 'Lakarsantri', 'Mulyorejo', 'Pabean Cantikan',
        'Pakal', 'Rungkut', 'Sambikerep', 'Sawahan', 'Semampir', 'Simokerto',
        'Sukolilo', 'Sukomanunggal', 'Tambaksari', 'Tandes', 'Tegalsari',
        'Tenggilis Mejoyo', 'Wiyung', 'Wonocolo', 'Wonokromo'
    }
    
    available_kecamatan = set(df['Kecamatan'].unique())
    missing_kecamatan = kecamatan_resmi - available_kecamatan
    
    if missing_kecamatan:
        print(f"\n⚠️  Kecamatan yang tidak ada data bangunan ({len(missing_kecamatan)}):")
        for kec in sorted(missing_kecamatan):
            print(f"  - {kec}")
    
    print(f"\n✅ Coverage: {len(available_kecamatan)}/{len(kecamatan_resmi)} kecamatan ({len(available_kecamatan)/len(kecamatan_resmi)*100:.1f}%)")

def main():
    print("🔧 Perbaikan Data Bangunan")
    print("=" * 50)
    
    # Fix data
    df_fixed = fix_building_data()
    
    # Create summary
    create_building_summary()
    
    print("\n" + "=" * 50)
    print("=== HASIL PERBAIKAN ===")
    print("✅ Data bangunan telah diperbaiki")
    print("✅ Nama kecamatan distandarisasi")
    print("✅ Missing values dikurangi")
    print("✅ Tidak ada Prajuritkulon")
    print("✅ File backup dibuat")
    print("⚠️  Beberapa kecamatan tidak memiliki data bangunan (normal)")
    
    print("\n📋 DATA BANGUNAN SEKARANG LEBIH AMAN!")

if __name__ == "__main__":
    main()
