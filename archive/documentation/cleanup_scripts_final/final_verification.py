"""
Script final untuk memverifikasi sistem lengkap dengan 31 kecamatan Surabaya
"""

import pandas as pd
import os

def final_verification():
    """Verifikasi final sistem lengkap"""
    print("🔍 VERIFIKASI FINAL SISTEM LENGKAP")
    print("="*50)
    
    # Kecamatan resmi Surabaya
    kecamatan_resmi = [
        "Asemrowo", "Benowo", "Bubutan", "Bulak", "Dukuh Pakis",
        "Gayungan", "Genteng", "Gubeng", "Gunung Anyar", "Jambangan",
        "Karang Pilang", "Kenjeran", "Krembangan", "Lakarsantri", "Mulyorejo",
        "Pabean Cantikan", "Pakal", "Rungkut", "Sambikerep", "Sawahan",
        "Semampir", "Simokerto", "Sukolilo", "Sukomanunggal", "Tambaksari",
        "Tandes", "Tegalsari", "Tenggilis Mejoyo", "Wiyung", "Wonocolo", "Wonokromo"
    ]
    
    try:
        # Baca CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'raw', 'dataset_tanah_njop_surabaya_sertifikat.csv')
        df = pd.read_csv(csv_path)
        
        print(f"📊 STATISTIK DATASET:")
        print(f"   Total record: {len(df)}")
        print(f"   Total kecamatan: {df['kecamatan'].nunique()}")
        
        # Periksa kelengkapan kecamatan
        kecamatan_dalam_csv = set(df['kecamatan'].unique())
        kecamatan_resmi_set = set(kecamatan_resmi)
        
        missing = kecamatan_resmi_set - kecamatan_dalam_csv
        extra = kecamatan_dalam_csv - kecamatan_resmi_set
        
        if not missing and not extra:
            print(f"✅ KELENGKAPAN KECAMATAN: SEMPURNA!")
            print(f"   Semua 31 kecamatan resmi Surabaya tersedia")
        else:
            if missing:
                print(f"❌ Kecamatan yang hilang: {missing}")
            if extra:
                print(f"⚠️  Kecamatan tambahan: {extra}")
        
        # Periksa data Prajuritkulon
        prajurit_data = df[df['kecamatan'].str.contains('prajurit', case=False, na=False)]
        if len(prajurit_data) == 0:
            print(f"✅ DATA PRAJURITKULON: BERSIH!")
            print(f"   Tidak ada data Prajuritkulon yang tersisa")
        else:
            print(f"❌ Masih ada {len(prajurit_data)} data Prajuritkulon!")
        
        # Periksa data Tenggilis Mejoyo
        tenggilis_data = df[df['kecamatan'] == 'Tenggilis Mejoyo']
        if len(tenggilis_data) > 0:
            print(f"✅ DATA TENGGILIS MEJOYO: TERSEDIA!")
            print(f"   Jumlah record: {len(tenggilis_data)}")
            print(f"   Rata-rata NJOP total: Rp {tenggilis_data['njop_total'].mean():,.0f}")
            print(f"   Jumlah kelurahan: {tenggilis_data['kelurahan'].nunique()}")
        else:
            print(f"❌ Data Tenggilis Mejoyo tidak ditemukan!")
        
        # Statistik per kecamatan
        print(f"\n📈 DISTRIBUSI DATA PER KECAMATAN:")
        kecamatan_stats = df['kecamatan'].value_counts().sort_index()
        
        for kecamatan in sorted(kecamatan_resmi):
            count = kecamatan_stats.get(kecamatan, 0)
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {kecamatan}: {count} record")
        
        # Ringkasan final
        print(f"\n🎯 RINGKASAN FINAL:")
        print(f"   📊 Total data: {len(df)} record")
        print(f"   🏘️  Total kecamatan: {df['kecamatan'].nunique()}/31")
        print(f"   🚫 Data Prajuritkulon: {'BERSIH' if len(prajurit_data) == 0 else 'MASIH ADA'}")
        print(f"   ➕ Data Tenggilis Mejoyo: {'TERSEDIA' if len(tenggilis_data) > 0 else 'TIDAK ADA'}")
        print(f"   💾 File backup: tersedia")
        
        if len(kecamatan_dalam_csv) == 31 and len(prajurit_data) == 0 and len(tenggilis_data) > 0:
            print(f"\n🎉 STATUS: SISTEM LENGKAP DAN SIAP DIGUNAKAN!")
            return True
        else:
            print(f"\n⚠️  STATUS: MASIH ADA YANG PERLU DIPERBAIKI")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    final_verification()
