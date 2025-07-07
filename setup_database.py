#!/usr/bin/env python3
"""
Script untuk setup database MySQL untuk aplikasi
"""
import mysql.connector
from mysql.connector import Error
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'telkom-dashboard-secret'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'db_kp'

def create_database():
    """Membuat database jika belum ada"""
    connection = None
    try:
        # Koneksi ke MySQL server tanpa database spesifik
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Membuat database jika belum ada
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
            print(f"✅ Database '{Config.MYSQL_DB}' created successfully or already exists")
            
            # Pilih database
            cursor.execute(f"USE {Config.MYSQL_DB}")
            
            # Buat tabel users jika belum ada
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT NOT NULL AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin','pengguna') NOT NULL DEFAULT 'pengguna',
                PRIMARY KEY (id),
                UNIQUE KEY email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """
            cursor.execute(create_users_table)
            print("✅ Table 'users' created successfully or already exists")
            
            # Insert admin user jika belum ada
            from werkzeug.security import generate_password_hash
            admin_password_hash = generate_password_hash('admin123')
            
            insert_admin = """
            INSERT IGNORE INTO users (name, email, password, role) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_admin, ('Admin', 'admin@telkom.co.id', admin_password_hash, 'admin'))
            
            # Buat tabel prediksi_properti_tanah
            create_prediksi_tanah_table = """
            CREATE TABLE IF NOT EXISTS prediksi_properti_tanah (
                id INT NOT NULL AUTO_INCREMENT,
                kecamatan VARCHAR(100),
                kelurahan VARCHAR(100),
                luas_tanah_m2 DECIMAL(10,2),
                njop_tanah_per_m2 DECIMAL(15,2),
                zona_nilai_tanah VARCHAR(50),
                kelas_tanah VARCHAR(50),
                jenis_sertifikat VARCHAR(50),
                harga_prediksi_tanah DECIMAL(15,2),
                harga_per_m2_tanah DECIMAL(15,2),
                model_predictor VARCHAR(50),
                confidence_score DECIMAL(5,4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """
            cursor.execute(create_prediksi_tanah_table)
            print("✅ Table 'prediksi_properti_tanah' created successfully")
            
            # Buat tabel prediksi_properti_bangunan_tanah
            create_prediksi_bangunan_table = """
            CREATE TABLE IF NOT EXISTS prediksi_properti_bangunan_tanah (
                id INT NOT NULL AUTO_INCREMENT,
                kecamatan VARCHAR(100),
                kamar_tidur INT,
                kamar_mandi INT,
                luas_tanah_m2 DECIMAL(10,2),
                luas_bangunan_m2 DECIMAL(10,2),
                daya_listrik INT,
                jumlah_lantai INT,
                sertifikat VARCHAR(50),
                ruang_makan VARCHAR(20),
                ruang_tamu VARCHAR(20),
                kondisi_perabotan VARCHAR(50),
                hadap VARCHAR(50),
                terjangkau_internet VARCHAR(20),
                lebar_jalan VARCHAR(50),
                sumber_air VARCHAR(50),
                hook VARCHAR(20),
                kondisi_properti VARCHAR(50),
                tipe_iklan VARCHAR(50),
                aksesibilitas VARCHAR(50),
                tingkat_keamanan VARCHAR(50),
                harga_prediksi_bangunan_tanah DECIMAL(15,2),
                harga_per_m2_bangunan DECIMAL(15,2),
                model_predictor VARCHAR(50),
                confidence_score DECIMAL(5,4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
            """
            cursor.execute(create_prediksi_bangunan_table)
            print("✅ Table 'prediksi_properti_bangunan_tanah' created successfully")
            
            connection.commit()
            print("✅ Database setup completed successfully!")
            
            # Tampilkan info login
            print("\n" + "="*50)
            print("🔑 LOGIN CREDENTIALS:")
            print("Email: admin@telkom.co.id")
            print("Password: admin123")
            print("Role: admin")
            print("="*50)
            
    except Error as e:
        print(f"❌ Error while connecting to MySQL: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def check_database_connection():
    """Cek koneksi ke database"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        
        if connection.is_connected():
            print("✅ Database connection successful!")
            connection.close()
            return True
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up database for Telkom Property Prediction System...")
    print(f"📍 Database Host: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
    print(f"📍 Database Name: {Config.MYSQL_DB}")
    print(f"📍 Database User: {Config.MYSQL_USER}")
    
    if create_database():
        check_database_connection()
    else:
        print("❌ Database setup failed!")
