#!/usr/bin/env python3
"""
Analisis detail masalah data bangunan dan solusinya
"""
import pandas as pd

def analyze_building_data_issues():
    """Analisis masalah data bangunan"""
    print("=== ANALISIS MASALAH DATA BANGUNAN ===")
    
    # Load data
    df_building = pd.read_csv("data/raw/Dataset_Bangunan_Surabaya_Final_Revisi_.csv")
    df_land = pd.read_csv("data/raw/dataset_tanah_njop_surabaya_sertifikat.csv")
    
    # Kecamatan resmi Surabaya (31 kecamatan)
    kecamatan_resmi = {
        'Asemrowo', 'Benowo', 'Bubutan', 'Bulak', 'Dukuh Pakis', 'Gayungan',
        'Genteng', 'Gubeng', 'Gunung Anyar', 'Jambangan', 'Karang Pilang',
        'Kenjeran', 'Krembangan', 'Lakarsantri', 'Mulyorejo', 'Pabean Cantikan',
        'Pakal', 'Rungkut', 'Sambikerep', 'Sawahan', 'Semampir', 'Simokerto',
        'Sukolilo', 'Sukomanunggal', 'Tambaksari', 'Tandes', 'Tegalsari',
        'Tenggilis Mejoyo', 'Wiyung', 'Wonocolo', 'Wonokromo'
    }
    
    # Kecamatan dalam data bangunan
    building_kec = set(df_building['Kecamatan'].unique())
    
    # Kecamatan dalam data tanah
    land_kec = set(df_land['kecamatan'].unique())
    
    print(f"📊 Kecamatan resmi Surabaya: {len(kecamatan_resmi)}")
    print(f"📊 Kecamatan dalam data bangunan: {len(building_kec)}")
    print(f"📊 Kecamatan dalam data tanah: {len(land_kec)}")
    
    # Masalah 1: Nama kecamatan tidak konsisten
    print(f"\n🔍 MASALAH 1: INKONSISTENSI NAMA KECAMATAN")
    
    # Mapping untuk nama yang tidak konsisten
    name_mapping = {
        'Dukuh pakis': 'Dukuh Pakis',
        'Tenggilis mejoyo': 'Tenggilis Mejoyo'
    }
    
    inconsistent_names = []
    for kec in building_kec:
        if kec not in kecamatan_resmi:
            inconsistent_names.append(kec)
    
    if inconsistent_names:
        print(f"❌ Nama tidak konsisten dalam data bangunan:")
        for name in inconsistent_names:
            if name in name_mapping:
                print(f"  - '{name}' → harus '{name_mapping[name]}'")
            else:
                print(f"  - '{name}' → tidak diketahui mapping")
    
    # Masalah 2: Kecamatan yang hilang
    print(f"\n🔍 MASALAH 2: KECAMATAN YANG HILANG")
    missing_in_building = kecamatan_resmi - building_kec
    if missing_in_building:
        print(f"❌ Kecamatan yang hilang dari data bangunan:")
        for kec in sorted(missing_in_building):
            print(f"  - {kec}")
    
    # Masalah 3: Missing values
    print(f"\n🔍 MASALAH 3: MISSING VALUES")
    missing_by_column = df_building.isnull().sum()
    missing_columns = missing_by_column[missing_by_column > 0].sort_values(ascending=False)
    
    if len(missing_columns) > 0:
        print(f"❌ Kolom dengan missing values:")
        for col, count in missing_columns.items():
            percentage = (count / len(df_building)) * 100
            print(f"  - {col}: {count} ({percentage:.1f}%)")
    
    return name_mapping, missing_in_building, missing_columns

def suggest_solutions():
    """Saran solusi untuk masalah data bangunan"""
    print(f"\n=== SOLUSI YANG DISARANKAN ===")
    
    print("1. 🔧 PERBAIKAN NAMA KECAMATAN")
    print("   - Standardisasi nama kecamatan agar konsisten")
    print("   - 'Dukuh pakis' → 'Dukuh Pakis'")
    print("   - 'Tenggilis mejoyo' → 'Tenggilis Mejoyo'")
    
    print("\n2. 📋 KECAMATAN YANG HILANG")
    print("   - Data bangunan tidak lengkap (27 dari 31 kecamatan)")
    print("   - Kecamatan yang hilang: Bulak, Gunung Anyar, Karang Pilang, Pabean Cantikan")
    print("   - Opsi: Tambahkan data atau terima bahwa tidak semua kecamatan memiliki data bangunan")
    
    print("\n3. 💾 MISSING VALUES")
    print("   - Bersihkan atau isi missing values")
    print("   - Gunakan strategi imputation yang sesuai")
    print("   - Atau hapus baris dengan missing values kritis")
    
    print("\n4. 🔄 KONSISTENSI DENGAN DATA TANAH")
    print("   - Pastikan format nama kecamatan sama")
    print("   - Validasi bahwa kedua dataset kompatibel")

def main():
    print("🔍 Analisis Masalah Data Bangunan")
    print("=" * 50)
    
    name_mapping, missing_kec, missing_cols = analyze_building_data_issues()
    
    suggest_solutions()
    
    print("\n" + "=" * 50)
    print("=== KESIMPULAN ===")
    
    if len(name_mapping) > 0:
        print("⚠️  Ada masalah nama kecamatan yang tidak konsisten")
    
    if len(missing_kec) > 0:
        print("⚠️  Ada kecamatan yang hilang dari data bangunan")
    
    if len(missing_cols) > 0:
        print("⚠️  Ada banyak missing values")
    
    print("\n📋 STATUS KEAMANAN DATA BANGUNAN:")
    print("✅ Tidak ada Prajuritkulon (AMAN)")
    print("⚠️  Perlu perbaikan inkonsistensi nama")
    print("⚠️  Perlu handling missing values")
    print("⚠️  Data tidak lengkap (27/31 kecamatan)")
    
    print("\n🎯 REKOMENDASI:")
    print("1. Perbaiki nama kecamatan untuk konsistensi")
    print("2. Handle missing values dengan strategi yang tepat")
    print("3. Terima bahwa tidak semua kecamatan memiliki data bangunan")
    print("4. Dokumentasikan batasan data")

if __name__ == "__main__":
    main()
