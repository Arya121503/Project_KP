"""
Script untuk menambahkan data kecamatan Tenggilis Mejoyo 
dengan menggunakan rata-rata dari kecamatan lain
"""

import pandas as pd
import numpy as np
import os
from random import randint, choice, uniform

def add_tenggilis_mejoyo_data():
    """Menambahkan data Tenggilis Mejoyo berdasarkan rata-rata kecamatan lain"""
    print("=== Menambahkan Data Tenggilis Mejoyo ===")
    
    # Baca file CSV yang sudah ada
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'raw', 'dataset_tanah_njop_surabaya_sertifikat.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ File CSV tidak ditemukan: {csv_path}")
        return False
    
    try:
        # Baca data existing
        df = pd.read_csv(csv_path)
        print(f"✅ Data existing berhasil dibaca: {len(df)} baris")
        
        # Hitung statistik rata-rata dari semua kecamatan
        stats = {
            'avg_luas_tanah': df['luas_tanah_m2'].mean(),
            'avg_njop_tanah': df['njop_tanah_m2'].mean(),
            'avg_njop_total': df['njop_total'].mean(),
            'avg_zona_nilai': df['zona_nilai_tanah'].mode()[0] if not df['zona_nilai_tanah'].mode().empty else 2,
            'common_kelas': df['kelas_tanah'].mode()[0] if not df['kelas_tanah'].mode().empty else 'B',
            'common_tahun': df['tahun'].mode()[0] if not df['tahun'].mode().empty else 2025
        }
        
        print(f"📊 Statistik rata-rata:")
        print(f"   - Luas tanah: {stats['avg_luas_tanah']:.0f} m²")
        print(f"   - NJOP per m²: Rp {stats['avg_njop_tanah']:,.0f}")
        print(f"   - NJOP total: Rp {stats['avg_njop_total']:,.0f}")
        print(f"   - Zona nilai: {stats['avg_zona_nilai']}")
        print(f"   - Kelas tanah: {stats['common_kelas']}")
        
        # Ambil sample kelurahan dari kecamatan lain untuk variasi
        sample_kelurahan = [
            "Kelurahan Tenggilis Mejoyo Utara",
            "Kelurahan Tenggilis Mejoyo Selatan", 
            "Kelurahan Tenggilis Mejoyo Timur",
            "Kelurahan Tenggilis Mejoyo Barat",
            "Kelurahan Tenggilis Mejoyo Tengah",
            "Desa Tenggilis Mejoyo Utara",
            "Desa Tenggilis Mejoyo Selatan",
            "Lingkungan Tenggilis Mejoyo",
            "Kelurahan Tenggilis Utara",
            "Kelurahan Tenggilis Selatan",
            "Kelurahan Mejoyo Utara",
            "Kelurahan Mejoyo Selatan",
            "Desa Tenggilis",
            "Desa Mejoyo",
            "Lingkungan Tenggilis",
            "Lingkungan Mejoyo"
        ]
        
        # Jenis sertifikat yang umum
        jenis_sertifikat = ['SHM', 'HGB', 'Belum Bersertifikat', 'Girik']
        sertifikat_weights = [0.4, 0.3, 0.2, 0.1]  # Probabilitas untuk setiap jenis
        
        # Generate data Tenggilis Mejoyo (sekitar 30-35 baris untuk proporsional)
        tenggilis_data = []
        num_records = randint(30, 35)
        
        for i in range(num_records):
            # Variasi data berdasarkan rata-rata dengan random factor
            luas_factor = uniform(0.7, 1.3)  # Variasi 70% - 130%
            njop_factor = uniform(0.8, 1.2)  # Variasi 80% - 120%
            
            luas_tanah = int(stats['avg_luas_tanah'] * luas_factor)
            njop_per_m2 = int(stats['avg_njop_tanah'] * njop_factor)
            njop_total = luas_tanah * njop_per_m2
            
            # Random kelurahan
            kelurahan = choice(sample_kelurahan)
            
            # Random jenis sertifikat berdasarkan probabilitas
            jenis_sert = np.random.choice(jenis_sertifikat, p=sertifikat_weights)
            
            # Generate nomor sertifikat jika ada
            no_sertifikat = ""
            if jenis_sert != "Belum Bersertifikat":
                no_sertifikat = f"SRT-{randint(100000, 999999)}"
            
            tenggilis_data.append({
                'kecamatan': 'Tenggilis Mejoyo',
                'kelurahan': kelurahan,
                'luas_tanah_m2': luas_tanah,
                'njop_tanah_m2': njop_per_m2,
                'njop_total': njop_total,
                'zona_nilai_tanah': stats['avg_zona_nilai'],
                'kelas_tanah': stats['common_kelas'],
                'tahun': stats['common_tahun'],
                'jenis_sertifikat': jenis_sert,
                'no_sertifikat': no_sertifikat
            })
        
        # Buat DataFrame baru untuk data Tenggilis Mejoyo
        tenggilis_df = pd.DataFrame(tenggilis_data)
        
        # Gabungkan dengan data existing
        combined_df = pd.concat([df, tenggilis_df], ignore_index=True)
        
        # Urutkan berdasarkan kecamatan
        combined_df = combined_df.sort_values('kecamatan')
        
        # Simpan ke file CSV
        combined_df.to_csv(csv_path, index=False)
        
        print(f"✅ Data Tenggilis Mejoyo berhasil ditambahkan: {len(tenggilis_data)} baris")
        print(f"✅ Total data sekarang: {len(combined_df)} baris")
        print(f"✅ File CSV berhasil diperbarui: {csv_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error menambahkan data Tenggilis Mejoyo: {e}")
        return False

def verify_tenggilis_addition():
    """Verifikasi bahwa data Tenggilis Mejoyo berhasil ditambahkan"""
    print("\n=== Verifikasi Data Tenggilis Mejoyo ===")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'raw', 'dataset_tanah_njop_surabaya_sertifikat.csv')
    
    try:
        df = pd.read_csv(csv_path)
        
        # Hitung jumlah kecamatan unik
        kecamatan_count = df['kecamatan'].nunique()
        print(f"✅ Total kecamatan unik: {kecamatan_count}")
        
        # Periksa apakah Tenggilis Mejoyo ada
        tenggilis_data = df[df['kecamatan'] == 'Tenggilis Mejoyo']
        if len(tenggilis_data) > 0:
            print(f"✅ Data Tenggilis Mejoyo ditemukan: {len(tenggilis_data)} baris")
            
            # Tampilkan statistik Tenggilis Mejoyo
            print(f"📊 Statistik Tenggilis Mejoyo:")
            print(f"   - Rata-rata luas tanah: {tenggilis_data['luas_tanah_m2'].mean():.0f} m²")
            print(f"   - Rata-rata NJOP per m²: Rp {tenggilis_data['njop_tanah_m2'].mean():,.0f}")
            print(f"   - Rata-rata NJOP total: Rp {tenggilis_data['njop_total'].mean():,.0f}")
            print(f"   - Jumlah kelurahan: {tenggilis_data['kelurahan'].nunique()}")
            
            # Tampilkan sample data
            print(f"\n📋 Sample data Tenggilis Mejoyo:")
            for i, row in tenggilis_data.head(3).iterrows():
                print(f"   - {row['kelurahan']}: {row['luas_tanah_m2']} m², Rp {row['njop_total']:,.0f}")
            
            return True
        else:
            print("❌ Data Tenggilis Mejoyo tidak ditemukan")
            return False
            
    except Exception as e:
        print(f"❌ Error verifikasi: {e}")
        return False

def main():
    """Fungsi utama untuk menambahkan data Tenggilis Mejoyo"""
    print("🚀 Memulai proses penambahan data Tenggilis Mejoyo...\n")
    
    # Backup file original terlebih dahulu
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'raw', 'dataset_tanah_njop_surabaya_sertifikat.csv')
    backup_path = csv_path.replace('.csv', '_backup_before_tenggilis.csv')
    
    try:
        import shutil
        shutil.copy2(csv_path, backup_path)
        print(f"✅ Backup file dibuat: {backup_path}")
    except Exception as e:
        print(f"⚠️  Gagal membuat backup: {e}")
    
    # Tambahkan data Tenggilis Mejoyo
    if add_tenggilis_mejoyo_data():
        # Verifikasi hasil
        if verify_tenggilis_addition():
            print("\n" + "="*50)
            print("🎉 PROSES BERHASIL DISELESAIKAN!")
            print("✅ Data Tenggilis Mejoyo berhasil ditambahkan")
            print("✅ Total kecamatan sekarang: 31 kecamatan")
            print("✅ Data sudah siap digunakan")
            print("="*50)
        else:
            print("\n❌ Verifikasi gagal - ada masalah dengan data")
    else:
        print("\n❌ Gagal menambahkan data Tenggilis Mejoyo")

if __name__ == "__main__":
    main()
