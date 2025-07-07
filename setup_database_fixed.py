#!/usr/bin/env python3
"""
Script untuk setup database MySQL untuk aplikasi - Fixed Version
"""
import mysql.connector
from mysql.connector import Error
import os

def create_database():
    """Membuat database jika belum ada"""
    connection = None
    
    # Konfigurasi MySQL yang sudah dideteksi
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'db_kp'
    
    try:
        print(f"🔗 Connecting to MySQL at {MYSQL_HOST}:{MYSQL_PORT}...")
        
        # Koneksi ke MySQL server tanpa database spesifik
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            connection_timeout=10
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print(f"✅ Connected to MySQL Server: {connection.get_server_info()}")
            
            # Membuat database jika belum ada
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
            print(f"✅ Database '{MYSQL_DB}' created successfully or already exists")
            
            # Pilih database
            cursor.execute(f"USE {MYSQL_DB}")
            
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
            
            if cursor.rowcount > 0:
                print("✅ Admin user created successfully")
            else:
                print("ℹ️  Admin user already exists")
            
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
            print("\n🎉 Database setup completed successfully!")
            
            # Tampilkan info login
            print("\n" + "="*50)
            print("🔑 LOGIN CREDENTIALS:")
            print("Email: admin@telkom.co.id")
            print("Password: admin123")
            print("Role: admin")
            print("="*50)
            
            # Tampilkan info database
            print("\n📊 DATABASE INFO:")
            print(f"Host: {MYSQL_HOST}")
            print(f"Port: {MYSQL_PORT}")
            print(f"Database: {MYSQL_DB}")
            print(f"User: {MYSQL_USER}")
            print("="*50)
            
            return True
            
    except Error as e:
        print(f"❌ Error while connecting to MySQL: {e}")
        
        if "Can't connect" in str(e):
            print("\n💡 TROUBLESHOOTING:")
            print("1. Pastikan MySQL/MariaDB server berjalan")
            print("2. Cek XAMPP Control Panel - MySQL harus 'Running'")
            print("3. Atau jalankan: net start mysql (as administrator)")
            print("4. Atau install MySQL Server dari: https://dev.mysql.com/downloads/")
            
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Database connection closed")

def check_database_connection():
    """Cek koneksi ke database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='db_kp'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"✅ Database connection successful! Found {user_count} users.")
            cursor.close()
            connection.close()
            return True
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🏢 TELKOM PROPERTY PREDICTION SYSTEM")
    print("🗄️  DATABASE SETUP UTILITY")
    print("="*60)
    
    if create_database():
        print("\n🔍 Testing database connection...")
        check_database_connection()
        print("\n✅ Setup completed! You can now run: python run.py")
    else:
        print("\n❌ Database setup failed!")
        print("Please fix the MySQL connection and try again.")
