#!/usr/bin/env python3
"""
Test API response untuk debugging
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, mysql
import json

def test_api():
    app = create_app()
    
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Test the exact query from API
            cur.execute("""
                SELECT id, kecamatan, kelurahan, luas_tanah_m2 as luas, 
                       harga_prediksi_tanah as harga, jenis_sertifikat as sertifikat, 
                       'tanah' as tipe
                FROM prediksi_properti_tanah
                ORDER BY created_at DESC
                LIMIT 2
            """)
            tanah_data = cur.fetchall()
            print("✅ Tanah query results:")
            for row in tanah_data:
                print(f"   {row}")
            
            cur.execute("""
                SELECT id, kecamatan, 'N/A' as kelurahan, 
                       (luas_tanah_m2 + luas_bangunan_m2) as luas, 
                       harga_prediksi_total as harga, 
                       sertifikat, 'bangunan' as tipe
                FROM prediksi_properti_bangunan_tanah
                ORDER BY created_at DESC
                LIMIT 2
            """)
            bangunan_data = cur.fetchall()
            print("✅ Bangunan query results:")
            for row in bangunan_data:
                print(f"   {row}")
            
            # Test data processing
            all_data = []
            
            # Process tanah data
            for row in tanah_data:
                all_data.append({
                    'id': row[0],
                    'kecamatan': row[1],
                    'kelurahan': row[2],
                    'luas': float(row[3] or 0),
                    'harga': float(row[4] or 0),
                    'sertifikat': row[5],
                    'tipe': row[6]
                })
            
            # Process bangunan data
            for row in bangunan_data:
                all_data.append({
                    'id': row[0],
                    'kecamatan': row[1],
                    'kelurahan': row[2],
                    'luas': float(row[3] or 0),
                    'harga': float(row[4] or 0),
                    'sertifikat': row[5],
                    'tipe': row[6]
                })
            
            print(f"✅ Processed data: {len(all_data)} items")
            print("Sample processed item:")
            if all_data:
                print(f"   {all_data[0]}")
            
            # Simulate API response
            response = {
                'success': True,
                'data': {
                    'all_properties': all_data,
                    'total_count': len(all_data)
                }
            }
            
            print("✅ API Response structure:")
            print(f"   success: {response['success']}")
            print(f"   data.all_properties length: {len(response['data']['all_properties'])}")
            print(f"   data.total_count: {response['data']['total_count']}")
            
            cur.close()
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
