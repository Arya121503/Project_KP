#!/usr/bin/env python3
"""
Script untuk menambahkan sample data favorit aset
"""

import mysql.connector
from datetime import datetime, timedelta

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_kp'
}

def add_sample_favorites():
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Sample favorite data
        sample_favorites = [
            {
                'user_id': 2,
                'aset_id': 1,
                'catatan': 'Lokasi strategis dekat jalan raya, cocok untuk usaha retail',
                'created_at': datetime.now() - timedelta(days=3)
            },
            {
                'user_id': 2,
                'aset_id': 3,
                'catatan': 'Tanah luas, potensial untuk warehouse atau gudang',
                'created_at': datetime.now() - timedelta(days=7)
            },
            {
                'user_id': 2,
                'aset_id': 4,
                'catatan': 'Bangunan sudah jadi, tinggal pakai untuk kantor',
                'created_at': datetime.now() - timedelta(hours=12)
            }
        ]
        
        # Check if favorit_aset already has data
        cursor.execute("SELECT COUNT(*) FROM favorit_aset WHERE user_id = 2")
        favorit_count = cursor.fetchone()[0]
        
        if favorit_count == 0:
            print("Adding sample favorite data...")
            for favorit in sample_favorites:
                query = """
                    INSERT INTO favorit_aset 
                    (user_id, aset_id, catatan, created_at)
                    VALUES (%s, %s, %s, %s)
                """
                
                values = (
                    favorit['user_id'], favorit['aset_id'], 
                    favorit['catatan'], favorit['created_at']
                )
                
                cursor.execute(query, values)
            
            conn.commit()
            print(f"✅ Successfully added {len(sample_favorites)} favorite records")
        else:
            print(f"ℹ️ favorit_aset table already has {favorit_count} records for user 2")
        
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
    add_sample_favorites()
