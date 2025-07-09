"""
Script untuk memverifikasi bahwa semua data Prajuritkulon telah dihapus
dan sistem berfungsi dengan baik
"""

import os
import sys
import pandas as pd

def verify_csv_cleanup():
    """Verifikasi bahwa file CSV sudah bersih"""
    print("=== Verifikasi CSV Dataset ===")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'raw', 'dataset_tanah_njop_surabaya_sertifikat.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ File CSV tidak ditemukan: {csv_path}")
        return False
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ File CSV berhasil dibaca: {len(df)} baris")
        
        # Periksa apakah ada data Prajuritkulon
        if 'kecamatan' in df.columns:
            prajurit_count = df[df['kecamatan'].str.contains('prajurit', case=False, na=False)].shape[0]
            if prajurit_count > 0:
                print(f"❌ Masih ada {prajurit_count} data Prajuritkulon di CSV!")
                return False
            else:
                print("✅ CSV bersih - tidak ada data Prajuritkulon")
        
        # Tampilkan daftar kecamatan yang tersedia
        if 'kecamatan' in df.columns:
            kecamatan_list = df['kecamatan'].unique()
            print(f"✅ Kecamatan yang tersedia: {len(kecamatan_list)} dari 31 kecamatan resmi Surabaya")
            print("   📋 Kecamatan yang ada:")
            for kec in sorted(kecamatan_list)[:10]:  # Tampilkan 10 pertama
                print(f"      - {kec}")
            if len(kecamatan_list) > 10:
                print(f"      ... dan {len(kecamatan_list) - 10} lainnya")
            
            # Periksa kecamatan yang hilang
            kecamatan_resmi = [
                "Asemrowo", "Benowo", "Bubutan", "Bulak", "Dukuh Pakis",
                "Gayungan", "Genteng", "Gubeng", "Gunung Anyar", "Jambangan",
                "Karang Pilang", "Kenjeran", "Krembangan", "Lakarsantri", "Mulyorejo",
                "Pabean Cantikan", "Pakal", "Rungkut", "Sambikerep", "Sawahan",
                "Semampir", "Simokerto", "Sukolilo", "Sukomanunggal", "Tambaksari",
                "Tandes", "Tegalsari", "Tenggilis Mejoyo", "Wiyung", "Wonocolo", "Wonokromo"
            ]
            
            missing_kecamatan = set(kecamatan_resmi) - set(kecamatan_list)
            if missing_kecamatan:
                print(f"   ⚠️  Kecamatan yang tidak tersedia dalam dataset: {', '.join(sorted(missing_kecamatan))}")
            else:
                print("   ✅ Semua kecamatan resmi Surabaya tersedia dalam dataset")
        
        return True
        
    except Exception as e:
        print(f"❌ Error membaca CSV: {e}")
        return False

def verify_data_processor():
    """Verifikasi bahwa data processor berfungsi dengan baik"""
    print("\n=== Verifikasi Data Processor ===")
    
    try:
        # Import data processor
        sys.path.append(os.path.dirname(__file__))
        from app.data_processor import AssetDataProcessor, TanahDataProcessor
        
        # Test AssetDataProcessor
        processor = AssetDataProcessor()
        if processor.df is not None:
            print(f"✅ AssetDataProcessor berhasil dimuat: {len(processor.df)} baris")
        else:
            print("❌ AssetDataProcessor gagal dimuat")
            return False
        
        # Test TanahDataProcessor
        tanah_processor = TanahDataProcessor()
        if tanah_processor.df is not None:
            print(f"✅ TanahDataProcessor berhasil dimuat: {len(tanah_processor.df)} baris")
            
            # Test get_all_kecamatan
            kecamatan_list = tanah_processor.get_all_kecamatan()
            print(f"✅ Kecamatan dari processor: {len(kecamatan_list)} dari 31 kecamatan resmi Surabaya")
            
            # Periksa apakah ada Prajuritkulon
            prajurit_in_list = [k for k in kecamatan_list if 'prajurit' in k.lower()]
            if prajurit_in_list:
                print(f"❌ Masih ada data Prajuritkulon di processor: {prajurit_in_list}")
                return False
            else:
                print("✅ Data processor bersih - tidak ada Prajuritkulon")
                
            # Periksa kelengkapan kecamatan
            kecamatan_resmi = [
                "Asemrowo", "Benowo", "Bubutan", "Bulak", "Dukuh Pakis",
                "Gayungan", "Genteng", "Gubeng", "Gunung Anyar", "Jambangan",
                "Karang Pilang", "Kenjeran", "Krembangan", "Lakarsantri", "Mulyorejo",
                "Pabean Cantikan", "Pakal", "Rungkut", "Sambikerep", "Sawahan",
                "Semampir", "Simokerto", "Sukolilo", "Sukomanunggal", "Tambaksari",
                "Tandes", "Tegalsari", "Tenggilis Mejoyo", "Wiyung", "Wonocolo", "Wonokromo"
            ]
            
            missing_kecamatan = set(kecamatan_resmi) - set(kecamatan_list)
            if missing_kecamatan:
                print(f"   ⚠️  Kecamatan yang tidak tersedia: {', '.join(sorted(missing_kecamatan))}")
            else:
                print("   ✅ Semua kecamatan resmi Surabaya tersedia")
                
        else:
            print("❌ TanahDataProcessor gagal dimuat")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing data processor: {e}")
        return False

def verify_system_integration():
    """Verifikasi integrasi sistem secara keseluruhan"""
    print("\n=== Verifikasi Integrasi Sistem ===")
    
    try:
        # Test apakah semua module bisa diimport
        sys.path.append(os.path.dirname(__file__))
        
        from app.routes import main
        print("✅ Routes berhasil diimport")
        
        from app.prediction_models import PrediksiPropertiTanah, PrediksiPropertiBangunanTanah
        print("✅ Prediction models berhasil diimport")
        
        from app.data_processor import AssetDataProcessor, TanahDataProcessor
        print("✅ Data processors berhasil diimport")
        
        print("✅ Semua module terintegrasi dengan baik")
        return True
        
    except Exception as e:
        print(f"❌ Error integrasi sistem: {e}")
        return False

def main():
    """Fungsi utama untuk verifikasi lengkap"""
    print("🔍 Memulai verifikasi sistem setelah pembersihan data Prajuritkulon...\n")
    
    all_passed = True
    
    # Verifikasi CSV
    if not verify_csv_cleanup():
        all_passed = False
    
    # Verifikasi Data Processor
    if not verify_data_processor():
        all_passed = False
    
    # Verifikasi Integrasi Sistem
    if not verify_system_integration():
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 SEMUA VERIFIKASI BERHASIL!")
        print("✅ Data Prajuritkulon telah dihapus sepenuhnya")
        print("✅ Sistem berfungsi dengan baik")
        print("✅ Dashboard siap digunakan dengan data yang bersih")
    else:
        print("❌ ADA MASALAH YANG PERLU DIPERBAIKI")
        print("   Periksa pesan error di atas dan lakukan perbaikan")
    
    print("="*50)

if __name__ == "__main__":
    main()
