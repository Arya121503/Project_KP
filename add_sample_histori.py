#!/usr/bin/env python3
"""
Script untuk menambahkan sample data histori sewa
"""

import mysql.connector
from datetime import datetime, timedelta
import random

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_kp'
}

def add_sample_histori_data():
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Sample histori sewa data
        sample_data = [
            {
                'user_id': 2,  # Assuming user ID 2 exists (pengguna)
                'aset_id': 1,  # Assuming aset ID 1 exists
                'jenis_aset': 'tanah',
                'alamat': 'Jl. Raya Surabaya No. 123, Surabaya',
                'kecamatan': 'Gubeng',
                'kelurahan': 'Gubeng',
                'luas_tanah': 500.00,
                'luas_bangunan': None,
                'harga_sewa': 15000000,
                'status_sewa': 'aktif',
                'tanggal_mulai': datetime.now() - timedelta(days=30),
                'tanggal_berakhir': datetime.now() + timedelta(days=335)
            },
            {
                'user_id': 2,
                'aset_id': 2,
                'jenis_aset': 'tanah_bangunan',
                'alamat': 'Jl. Diponegoro No. 45, Surabaya',
                'kecamatan': 'Genteng',
                'kelurahan': 'Genteng',
                'luas_tanah': 300.00,
                'luas_bangunan': 150.00,
                'harga_sewa': 25000000,
                'status_sewa': 'berakhir',
                'tanggal_mulai': datetime.now() - timedelta(days=400),
                'tanggal_berakhir': datetime.now() - timedelta(days=35)
            },
            {
                'user_id': 2,
                'aset_id': 3,
                'jenis_aset': 'tanah',
                'alamat': 'Jl. Ahmad Yani No. 78, Surabaya',
                'kecamatan': 'Wonokromo',
                'kelurahan': 'Wonokromo',
                'luas_tanah': 750.00,
                'luas_bangunan': None,
                'harga_sewa': 20000000,
                'status_sewa': 'dibatalkan',
                'tanggal_mulai': datetime.now() - timedelta(days=120),
                'tanggal_berakhir': datetime.now() + timedelta(days=245)
            },
            {
                'user_id': 2,
                'aset_id': 4,
                'jenis_aset': 'tanah_bangunan',
                'alamat': 'Jl. Basuki Rahmat No. 12, Surabaya',
                'kecamatan': 'Sukolilo',
                'kelurahan': 'Keputih',
                'luas_tanah': 400.00,
                'luas_bangunan': 200.00,
                'harga_sewa': 30000000,
                'status_sewa': 'aktif',
                'tanggal_mulai': datetime.now() - timedelta(days=60),
                'tanggal_berakhir': datetime.now() + timedelta(days=305)
            }
        ]
        
        # Insert sample data
        for data in sample_data:
            query = """
                INSERT INTO histori_sewa 
                (user_id, aset_id, jenis_aset, alamat, kecamatan, kelurahan, 
                 luas_tanah, luas_bangunan, harga_sewa, status_sewa, 
                 tanggal_mulai, tanggal_berakhir)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                data['user_id'], data['aset_id'], data['jenis_aset'],
                data['alamat'], data['kecamatan'], data['kelurahan'],
                data['luas_tanah'], data['luas_bangunan'], data['harga_sewa'],
                data['status_sewa'], data['tanggal_mulai'], data['tanggal_berakhir']
            )
            
            cursor.execute(query, values)
        
        conn.commit()
        print(f"✅ Successfully added {len(sample_data)} sample histori sewa records")
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_sample_histori_data()
