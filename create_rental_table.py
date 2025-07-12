#!/usr/bin/env python3
"""
Script to create the rental predictions table in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
import mysql.connector

def create_rental_table():
    """Create the rental predictions table"""
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = connection.cursor()
        
        # Create rental predictions table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS prediksi_sewa_bulanan (
            id INT AUTO_INCREMENT PRIMARY KEY,
            kecamatan VARCHAR(100) NOT NULL,
            kelurahan VARCHAR(100),
            luas_tanah_m2 INT,
            luas_bangunan_m2 INT,
            kamar_tidur INT,
            kamar_mandi INT,
            jumlah_lantai INT,
            tahun_dibangun INT,
            daya_listrik INT,
            sertifikat VARCHAR(100),
            kondisi_properti VARCHAR(100),
            tingkat_keamanan VARCHAR(50),
            aksesibilitas VARCHAR(50),
            tipe_iklan VARCHAR(50),
            NJOP_Rp_per_m2 DECIMAL(15,2),
            harga_sewa_rf DECIMAL(15,2),
            harga_sewa_xgb DECIMAL(15,2),
            harga_sewa_catboost DECIMAL(15,2),
            harga_sewa_ensemble DECIMAL(15,2),
            confidence_score DECIMAL(5,4),
            model_predictor VARCHAR(50) DEFAULT 'ensemble',
            property_type VARCHAR(20) DEFAULT 'bangunan',
            status_kirim_user ENUM('pending', 'sent') DEFAULT 'pending',
            alamat TEXT,
            deskripsi TEXT,
            foto_url VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_kecamatan (kecamatan),
            INDEX idx_status (status_kirim_user),
            INDEX idx_property_type (property_type),
            INDEX idx_created_at (created_at)
        )
        """
        
        cursor.execute(create_table_query)
        connection.commit()
        print('✅ Rental predictions table created successfully!')
        
        # Show table structure
        cursor.execute("DESCRIBE prediksi_sewa_bulanan")
        columns = cursor.fetchall()
        print('\n📋 Table structure:')
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f'❌ Error creating table: {e}')
        sys.exit(1)

if __name__ == '__main__':
    create_rental_table()
