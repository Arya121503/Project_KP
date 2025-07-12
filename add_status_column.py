#!/usr/bin/env python3
"""
Script to add status_kirim_user column to the database
"""

import mysql.connector
from config import Config

try:
    # Connect to MySQL
    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    
    cursor = connection.cursor()
    
    # Check if column exists
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'prediksi_properti_bangunan_tanah' 
        AND COLUMN_NAME = 'status_kirim_user'
    """)
    
    column_exists = cursor.fetchone()[0]
    
    if column_exists == 0:
        # Add the column
        cursor.execute("""
            ALTER TABLE prediksi_properti_bangunan_tanah 
            ADD COLUMN status_kirim_user VARCHAR(20) DEFAULT 'draft'
        """)
        
        connection.commit()
        print("Column 'status_kirim_user' added successfully!")
    else:
        print("Column 'status_kirim_user' already exists!")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
