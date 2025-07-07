#!/usr/bin/env python3
"""
Script untuk mengecek dan mencari MySQL server yang berjalan
"""
import mysql.connector
from mysql.connector import Error
import socket

def check_port(host, port):
    """Cek apakah port terbuka"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_mysql_connection(host, port, user, password):
    """Test koneksi MySQL"""
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connection_timeout=5
        )
        if connection.is_connected():
            info = connection.get_server_info()
            connection.close()
            return True, info
        return False, None
    except Error as e:
        return False, str(e)

def find_mysql_server():
    """Mencari MySQL server yang berjalan"""
    common_ports = [3306, 3307, 3308, 3309]
    common_passwords = ['', 'root', 'password', 'admin', 'Arya151203F.']
    
    print("🔍 Mencari MySQL server yang berjalan...")
    print("-" * 50)
    
    for port in common_ports:
        print(f"📍 Checking port {port}...")
        
        if check_port('localhost', port):
            print(f"  ✅ Port {port} terbuka")
            
            for password in common_passwords:
                success, info = test_mysql_connection('localhost', port, 'root', password)
                if success:
                    print(f"  🎉 MySQL ditemukan!")
                    print(f"     Host: localhost")
                    print(f"     Port: {port}")
                    print(f"     User: root")
                    print(f"     Password: {'(empty)' if password == '' else password}")
                    print(f"     Server Info: {info}")
                    return port, password
                else:
                    print(f"  ❌ Password '{password if password else '(empty)'}' gagal: {info}")
        else:
            print(f"  ❌ Port {port} tertutup")
    
    return None, None

def generate_config(port, password):
    """Generate konfigurasi yang benar"""
    config_content = f"""import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'telkom-dashboard-secret'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = os.environ.get('MYSQL_PORT') or {port}
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '{password}'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'db_kp'
"""
    
    env_content = f"""SECRET_KEY=telkom-property-prediction-secret-key-2025
MYSQL_HOST=localhost
MYSQL_PORT={port}
MYSQL_USER=root
MYSQL_PASSWORD={password}
MYSQL_DB=db_kp
FLASK_ENV=development
FLASK_DEBUG=True"""
    
    return config_content, env_content

if __name__ == "__main__":
    print("="*60)
    print("🔍 MYSQL SERVER DETECTION TOOL")
    print("="*60)
    
    port, password = find_mysql_server()
    
    if port and password is not None:
        print("\n" + "="*50)
        print("✅ MYSQL DITEMUKAN!")
        print("="*50)
        
        config_content, env_content = generate_config(port, password)
        
        print("\n📝 Update config.py dengan:")
        print("-" * 30)
        print(config_content)
        
        print("\n📝 Update .env dengan:")
        print("-" * 30)
        print(env_content)
        
        response = input("\n❓ Apakah ingin mengupdate config otomatis? (y/n): ")
        if response.lower() == 'y':
            try:
                with open('config.py', 'w') as f:
                    f.write(config_content)
                with open('.env', 'w') as f:
                    f.write(env_content)
                print("✅ Konfigurasi berhasil diupdate!")
                print("💡 Sekarang jalankan: python setup_database.py")
            except Exception as e:
                print(f"❌ Error update config: {e}")
    else:
        print("\n" + "="*50)
        print("❌ MYSQL SERVER TIDAK DITEMUKAN!")
        print("="*50)
        print("\n💡 Solusi:")
        print("1. Install dan jalankan XAMPP:")
        print("   - Download: https://www.apachefriends.org/")
        print("   - Buka XAMPP Control Panel")
        print("   - Klik 'Start' di MySQL")
        print("")
        print("2. Atau install MySQL Server:")
        print("   - Download: https://dev.mysql.com/downloads/mysql/")
        print("   - Install dengan password root")
        print("")
        print("3. Atau gunakan Docker:")
        print("   docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -d mysql:8.0")
        print("")
        print("4. Atau gunakan MySQL di port yang berbeda")
