#!/usr/bin/env python3
"""
Script untuk setup database MySQL dan tabel yang diperlukan
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
sys.path.append('.')
from config import Config

def create_database():
    """Membuat database jika belum ada"""
    try:
        # Koneksi tanpa specify database
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Buat database jika belum ada
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{Config.MYSQL_DB}' berhasil dibuat/sudah ada")
        
        # Gunakan database
        cursor.execute(f"USE {Config.MYSQL_DB}")
        
        # Buat tabel users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin', 'pengguna') NOT NULL DEFAULT 'pengguna',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Insert default admin jika belum ada
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        if cursor.fetchone()[0] == 0:
            from werkzeug.security import generate_password_hash
            hashed_pw = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('Administrator', 'admin@telkom.co.id', hashed_pw, 'admin'))
            print("✅ Default admin user created")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ Database setup selesai!")
        return True
        
    except Error as e:
        print(f"❌ Error setup database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Memulai setup database...")
    print("=" * 50)
    print(f"Host: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
    print(f"User: {Config.MYSQL_USER}")
    print(f"Database: {Config.MYSQL_DB}")
    print("=" * 50)
    
    success = create_database()
    
    if success:
        print("\n✅ Database setup berhasil!")
        print("Sekarang Anda dapat menjalankan create_prediction_tables.py")
    else:
        print("\n❌ Database setup gagal!")
        print("Periksa konfigurasi MySQL Anda")
