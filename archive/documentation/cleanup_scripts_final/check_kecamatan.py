"""
Script untuk memverifikasi kecamatan Surabaya yang valid
"""

# Daftar 31 kecamatan resmi di Surabaya
KECAMATAN_SURABAYA_RESMI = [
    "Asemrowo",
    "Benowo", 
    "Bubutan",
    "Bulak",
    "Dukuh Pakis",
    "Gayungan",
    "Genteng",
    "Gubeng",
    "Gunung Anyar",
    "Jambangan",
    "Karang Pilang",
    "Kenjeran",
    "Krembangan",
    "Lakarsantri",
    "Mulyorejo",
    "Pabean Cantikan",
    "Pakal",
    "Rungkut",
    "Sambikerep",
    "Sawahan",
    "Semampir",
    "Simokerto",
    "Sukolilo",
    "Sukomanunggal",
    "Tambaksari",
    "Tandes",
    "Tegalsari",
    "Tenggilis Mejoyo",
    "Wiyung",
    "Wonocolo",
    "Wonokromo"
]

import pandas as pd
import os

def check_kecamatan_completeness():
    """Periksa kelengkapan kecamatan di CSV"""
    print("=== Verifikasi Kecamatan Surabaya ===")
    
    # Baca CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'raw', 'dataset_tanah_njop_surabaya_sertifikat.csv')
    df = pd.read_csv(csv_path)
    
    # Ambil kecamatan unik dari CSV
    kecamatan_in_csv = set(df['kecamatan'].str.strip().unique())
    
    print(f"Kecamatan resmi Surabaya: {len(KECAMATAN_SURABAYA_RESMI)}")
    print(f"Kecamatan dalam CSV: {len(kecamatan_in_csv)}")
    
    # Periksa kecamatan yang hilang
    missing_kecamatan = set(KECAMATAN_SURABAYA_RESMI) - kecamatan_in_csv
    extra_kecamatan = kecamatan_in_csv - set(KECAMATAN_SURABAYA_RESMI)
    
    if missing_kecamatan:
        print(f"\n❌ Kecamatan yang hilang ({len(missing_kecamatan)}):")
        for kec in sorted(missing_kecamatan):
            print(f"   - {kec}")
    
    if extra_kecamatan:
        print(f"\n⚠️  Kecamatan tambahan yang tidak resmi ({len(extra_kecamatan)}):")
        for kec in sorted(extra_kecamatan):
            print(f"   - {kec}")
    
    if not missing_kecamatan and not extra_kecamatan:
        print("\n✅ Semua kecamatan lengkap dan valid!")
    
    print(f"\n📋 Kecamatan yang ada dalam CSV:")
    for kec in sorted(kecamatan_in_csv):
        status = "✅" if kec in KECAMATAN_SURABAYA_RESMI else "❌"
        print(f"   {status} {kec}")

if __name__ == "__main__":
    check_kecamatan_completeness()
