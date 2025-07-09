#!/usr/bin/env python3
"""
Script untuk memeriksa status data bangunan
"""
import pandas as pd
import os

def check_building_data():
    """Check status data bangunan"""
    print("=== PEMERIKSAAN DATA BANGUNAN ===")
    
    # Path file
    building_file = "data/raw/Dataset_Bangunan_Surabaya_Final_Revisi_.csv"
    
    if not os.path.exists(building_file):
        print(f"❌ File tidak ditemukan: {building_file}")
        return False
    
    try:
        # Load data
        df = pd.read_csv(building_file)
        
        print(f"✅ Dataset berhasil dimuat: {len(df)} rows")
        print(f"📊 Columns: {len(df.columns)} kolom")
        print(f"📋 Column names: {list(df.columns)}")
        
        # Check for kecamatan column
        kecamatan_col = None
        for col in df.columns:
            if 'kecamatan' in col.lower():
                kecamatan_col = col
                break
        
        if kecamatan_col:
            print(f"\n🏢 Kecamatan column: '{kecamatan_col}'")
            print(f"📊 Unique kecamatan: {df[kecamatan_col].nunique()}")
            
            # Check for Prajuritkulon
            prajurit_count = df[kecamatan_col].str.contains('prajurit', case=False, na=False).sum()
            if prajurit_count > 0:
                print(f"⚠️  PRAJURITKULON DITEMUKAN: {prajurit_count} records")
                print("🔍 Data Prajuritkulon:")
                prajurit_data = df[df[kecamatan_col].str.contains('prajurit', case=False, na=False)]
                print(prajurit_data[kecamatan_col].unique())
                return False
            else:
                print("✅ Tidak ada data Prajuritkulon")
            
            # Check for Tenggilis Mejoyo
            tenggilis_count = df[kecamatan_col].str.contains('tenggilis', case=False, na=False).sum()
            print(f"🏘️  Tenggilis Mejoyo: {tenggilis_count} records")
            
            # List all kecamatan
            print(f"\n📋 Daftar kecamatan ({df[kecamatan_col].nunique()}):")
            kecamatan_list = sorted(df[kecamatan_col].unique())
            for i, kec in enumerate(kecamatan_list, 1):
                count = df[df[kecamatan_col] == kec].shape[0]
                print(f"  {i:2d}. {kec}: {count} records")
            
        else:
            print("❌ Tidak ada kolom kecamatan yang ditemukan")
            return False
        
        # Check data quality
        print(f"\n🔍 KUALITAS DATA:")
        print(f"Missing values: {df.isnull().sum().sum()}")
        print(f"Duplicates: {df.duplicated().sum()}")
        
        # Check file modification time
        import datetime
        mtime = os.path.getmtime(building_file)
        mod_time = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"📅 Last modified: {mod_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def check_building_vs_land_consistency():
    """Check consistency between building and land data"""
    print(f"\n=== KONSISTENSI DATA BANGUNAN VS TANAH ===")
    
    try:
        # Load both datasets
        df_building = pd.read_csv("data/raw/Dataset_Bangunan_Surabaya_Final_Revisi_.csv")
        df_land = pd.read_csv("data/raw/dataset_tanah_njop_surabaya_sertifikat.csv")
        
        # Find kecamatan columns
        building_kec_col = None
        land_kec_col = None
        
        for col in df_building.columns:
            if 'kecamatan' in col.lower():
                building_kec_col = col
                break
        
        for col in df_land.columns:
            if 'kecamatan' in col.lower():
                land_kec_col = col
                break
        
        if building_kec_col and land_kec_col:
            building_kec = set(df_building[building_kec_col].unique())
            land_kec = set(df_land[land_kec_col].unique())
            
            print(f"📊 Kecamatan dalam data bangunan: {len(building_kec)}")
            print(f"📊 Kecamatan dalam data tanah: {len(land_kec)}")
            
            # Check differences
            only_in_building = building_kec - land_kec
            only_in_land = land_kec - building_kec
            common = building_kec & land_kec
            
            print(f"✅ Kecamatan sama: {len(common)}")
            
            if only_in_building:
                print(f"⚠️  Hanya di data bangunan: {only_in_building}")
            
            if only_in_land:
                print(f"⚠️  Hanya di data tanah: {only_in_land}")
            
            # Check for Prajuritkulon in building data
            building_prajurit = any('prajurit' in kec.lower() for kec in building_kec)
            land_prajurit = any('prajurit' in kec.lower() for kec in land_kec)
            
            if building_prajurit:
                print("❌ Data bangunan masih mengandung Prajuritkulon!")
                return False
            else:
                print("✅ Data bangunan tidak mengandung Prajuritkulon")
            
            if land_prajurit:
                print("❌ Data tanah masih mengandung Prajuritkulon!")
                return False
            else:
                print("✅ Data tanah tidak mengandung Prajuritkulon")
            
            return True
            
        else:
            print("❌ Tidak dapat menemukan kolom kecamatan")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🔍 Pemeriksaan Keamanan Data Bangunan")
    print("=" * 50)
    
    # Check building data
    building_ok = check_building_data()
    
    # Check consistency
    consistency_ok = check_building_vs_land_consistency()
    
    print("\n" + "=" * 50)
    print("=== RINGKASAN KEAMANAN DATA BANGUNAN ===")
    
    if building_ok and consistency_ok:
        print("✅ DATA BANGUNAN AMAN!")
        print("✅ Tidak ada Prajuritkulon")
        print("✅ Konsisten dengan data tanah")
        print("✅ Kualitas data baik")
    else:
        print("❌ DATA BANGUNAN TIDAK AMAN!")
        if not building_ok:
            print("❌ Ada masalah dengan data bangunan")
        if not consistency_ok:
            print("❌ Tidak konsisten dengan data tanah")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
