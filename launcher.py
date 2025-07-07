#!/usr/bin/env python3
"""
Launcher script untuk menjalankan aplikasi Telkom Property Prediction
"""
import os
import sys
import subprocess
from pathlib import Path

def check_mysql_server():
    """Cek apakah MySQL server berjalan"""
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            connection_timeout=5
        )
        connection.close()
        return True
    except Exception as e:
        print(f"❌ MySQL server tidak berjalan atau tidak dapat diakses: {e}")
        print(f"📍 Pastikan MySQL server berjalan di localhost:3306")
        return False

def check_dependencies():
    """Cek apakah semua dependencies terinstall"""
    required_packages = [
        'flask', 'werkzeug', 'flask_wtf', 'wtforms', 
        'pandas', 'numpy', 'pymysql', 'flask_mysqldb',
        'sklearn', 'xgboost', 'catboost', 'joblib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            if package == 'sklearn':
                try:
                    import sklearn
                except ImportError:
                    missing_packages.append('scikit-learn')
            elif package == 'flask_mysqldb':
                try:
                    import flask_mysqldb
                except ImportError:
                    missing_packages.append('Flask-MySQLdb')
            else:
                missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Package yang belum terinstall: {', '.join(missing_packages)}")
        print("💡 Jalankan: pip install -r requirements.txt")
        return False
    
    print("✅ Semua dependencies sudah terinstall")
    return True

def check_ml_models():
    """Cek apakah model ML tersedia"""
    model_dir = Path("ml_model")
    required_models = ["catboost_model.pkl", "xgboost_model.pkl", "random_forest_model.pkl"]
    
    missing_models = []
    for model in required_models:
        model_path = model_dir / model
        if not model_path.exists():
            missing_models.append(model)
    
    if missing_models:
        print(f"⚠️  Model ML yang tidak ditemukan: {', '.join(missing_models)}")
        print("💡 Aplikasi tetap bisa berjalan tanpa model ML, namun fitur prediksi tidak akan bekerja")
        return False
    
    print("✅ Semua model ML tersedia")
    return True

def check_database_setup():
    """Cek apakah database sudah disetup"""
    try:
        import mysql.connector
        
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='db_kp'
        )
        
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()
        connection.close()
        
        required_tables = ['users', 'prediksi_properti_tanah', 'prediksi_properti_bangunan_tanah']
        existing_tables = [table[0] for table in tables]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"❌ Tabel database yang belum ada: {', '.join(missing_tables)}")
            print("💡 Jalankan: python setup_database_fixed.py")
            return False
        
        print("✅ Database sudah disetup dengan benar")
        return True
        
    except Exception as e:
        print(f"❌ Error saat cek database: {e}")
        print("💡 Jalankan: python setup_database_fixed.py")
        return False

def run_application():
    """Jalankan aplikasi Flask"""
    print("\n🚀 Memulai aplikasi...")
    print("📍 Aplikasi akan berjalan di: http://localhost:5000")
    print("🔑 Login admin: admin@telkom.co.id / admin123")
    print("\n" + "="*50)
    
    try:
        from app import create_app
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error saat menjalankan aplikasi: {e}")
        return False

def main():
    """Main function"""
    print("="*60)
    print("🏢 TELKOM PROPERTY PREDICTION SYSTEM")
    print("="*60)
    
    print("\n📋 Melakukan pengecekan sistem...")
    
    # 1. Cek dependencies
    if not check_dependencies():
        return False
    
    # 2. Cek MySQL server
    if not check_mysql_server():
        print("\n💡 Cara menjalankan MySQL:")
        print("   - XAMPP: Buka XAMPP Control Panel → Start MySQL")
        print("   - MySQL Service: net start mysql (run as administrator)")
        print("   - Docker: docker run --name mysql -p 3307:3306 -e MYSQL_ROOT_PASSWORD=Arya151203F. -d mysql:8.0")
        return False
    
    # 3. Cek database setup
    if not check_database_setup():
        print("\n🔧 Menjalankan setup database...")
        try:
            subprocess.run([sys.executable, "setup_database_fixed.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Gagal setup database: {e}")
            return False
    
    # 4. Cek model ML (opsional)
    check_ml_models()
    
    # 5. Jalankan aplikasi
    print("\n✅ Semua pengecekan selesai!")
    print("✅ Sistem siap dijalankan!")
    
    input("\n👋 Tekan Enter untuk memulai aplikasi...")
    run_application()

if __name__ == "__main__":
    main()
