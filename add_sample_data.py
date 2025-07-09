#!/usr/bin/env python3
"""
Script untuk menambahkan sample data aset_sewa dan histori_sewa
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

def add_sample_data():
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # First, add sample aset_sewa data
        aset_data = [
            {
                'jenis': 'tanah',
                'alamat': 'Jl. Raya Surabaya No. 123, Surabaya',
                'kecamatan': 'Gubeng',
                'kelurahan': 'Gubeng',
                'luas_tanah': 500.00,
                'luas_bangunan': None,
                'harga_prediksi': 800000000,
                'harga_sewa': 15000000,
                'status': 'tersedia'
            },
            {
                'jenis': 'tanah_bangunan',
                'alamat': 'Jl. Diponegoro No. 45, Surabaya',
                'kecamatan': 'Genteng',
                'kelurahan': 'Genteng',
                'luas_tanah': 300.00,
                'luas_bangunan': 150.00,
                'harga_prediksi': 1200000000,
                'harga_sewa': 25000000,
                'status': 'tersedia'
            },
            {
                'jenis': 'tanah',
                'alamat': 'Jl. Ahmad Yani No. 78, Surabaya',
                'kecamatan': 'Wonokromo',
                'kelurahan': 'Wonokromo',
                'luas_tanah': 750.00,
                'luas_bangunan': None,
                'harga_prediksi': 1000000000,
                'harga_sewa': 20000000,
                'status': 'tersedia'
            },
            {
                'jenis': 'tanah_bangunan',
                'alamat': 'Jl. Basuki Rahmat No. 12, Surabaya',
                'kecamatan': 'Sukolilo',
                'kelurahan': 'Keputih',
                'luas_tanah': 400.00,
                'luas_bangunan': 200.00,
                'harga_prediksi': 1500000000,
                'harga_sewa': 30000000,
                'status': 'tersedia'
            }
        ]
        
        # Check if aset_sewa table has data
        cursor.execute("SELECT COUNT(*) FROM aset_sewa")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Adding sample aset_sewa data...")
            for data in aset_data:
                query = """
                    INSERT INTO aset_sewa 
                    (jenis, alamat, kecamatan, kelurahan, luas_tanah, luas_bangunan, 
                     harga_prediksi, harga_sewa, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    data['jenis'], data['alamat'], data['kecamatan'], data['kelurahan'],
                    data['luas_tanah'], data['luas_bangunan'], data['harga_prediksi'],
                    data['harga_sewa'], data['status']
                )
                
                cursor.execute(query, values)
            
            conn.commit()
            print(f"✅ Added {len(aset_data)} aset_sewa records")
        else:
            print(f"ℹ️ aset_sewa table already has {count} records")
        
        # Check if user ID 2 exists, if not create one
        cursor.execute("SELECT COUNT(*) FROM users WHERE id = 2")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            print("Creating sample user...")
            from werkzeug.security import generate_password_hash
            hashed_pw = generate_password_hash('user123')
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('Test User', 'user@telkom.co.id', hashed_pw, 'pengguna'))
            conn.commit()
            print("✅ Added sample user")
        
        # Now add sample histori sewa data
        sample_histori = [
            {
                'user_id': 2,
                'aset_id': 1,
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
        
        # Check if histori_sewa already has data
        cursor.execute("SELECT COUNT(*) FROM histori_sewa")
        histori_count = cursor.fetchone()[0]
        
        if histori_count == 0:
            print("Adding sample histori_sewa data...")
            for data in sample_histori:
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
            print(f"✅ Successfully added {len(sample_histori)} histori_sewa records")
        else:
            print(f"ℹ️ histori_sewa table already has {histori_count} records")
        
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
    add_sample_data()
