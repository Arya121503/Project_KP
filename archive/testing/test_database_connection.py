#!/usr/bin/env python3
"""
Script untuk test database connection dan table existence
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, mysql

def test_database():
    app = create_app()
    
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Test connection
            cur.execute("SELECT 1")
            print("✅ Database connection: OK")
            
            # Check if tables exist
            tables_to_check = [
                'prediksi_properti_tanah',
                'prediksi_properti_bangunan_tanah'
            ]
            
            for table in tables_to_check:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"✅ Table '{table}': {count} records")
                except Exception as e:
                    print(f"❌ Table '{table}': {e}")
            
            # Test the actual query from API
            try:
                cur.execute("""
                    SELECT id, kecamatan, kelurahan, luas_tanah_m2 as luas, 
                           harga_prediksi_tanah as harga, jenis_sertifikat as sertifikat, 
                           'tanah' as tipe
                    FROM prediksi_properti_tanah
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                tanah_data = cur.fetchall()
                print(f"✅ Tanah query: {len(tanah_data)} records returned")
                if tanah_data:
                    print(f"   Sample: {tanah_data[0]}")
            except Exception as e:
                print(f"❌ Tanah query error: {e}")
            
            try:
                cur.execute("""
                    SELECT id, kecamatan, 'N/A' as kelurahan, 
                           (luas_tanah_m2 + luas_bangunan_m2) as luas, 
                           harga_prediksi_total as harga, 
                           sertifikat, 'bangunan' as tipe
                    FROM prediksi_properti_bangunan_tanah
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                bangunan_data = cur.fetchall()
                print(f"✅ Bangunan query: {len(bangunan_data)} records returned")
                if bangunan_data:
                    print(f"   Sample: {bangunan_data[0]}")
            except Exception as e:
                print(f"❌ Bangunan query error: {e}")
            
            cur.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")

if __name__ == "__main__":
    test_database()
