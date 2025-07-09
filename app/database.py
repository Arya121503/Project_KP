from app import mysql
from flask import current_app
from werkzeug.security import generate_password_hash

def init_mysql_db():
    """Create users table & default admin"""
    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin', 'pengguna') NOT NULL DEFAULT 'pengguna'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Create aset_sewa table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS aset_sewa (
                id INT AUTO_INCREMENT PRIMARY KEY,
                jenis ENUM('tanah', 'tanah_bangunan') NOT NULL,
                alamat TEXT NOT NULL,
                kecamatan VARCHAR(100) NOT NULL,
                kelurahan VARCHAR(100) NOT NULL,
                luas_tanah DECIMAL(10,2) NOT NULL,
                luas_bangunan DECIMAL(10,2) DEFAULT NULL,
                kamar_tidur INT DEFAULT NULL,
                kamar_mandi INT DEFAULT NULL,
                jumlah_lantai INT DEFAULT NULL,
                harga_prediksi DECIMAL(15,2) NOT NULL,
                harga_sewa DECIMAL(15,2) NOT NULL,
                status ENUM('tersedia', 'disewa', 'tidak_tersedia') DEFAULT 'tersedia',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Create histori_sewa table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS histori_sewa (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                aset_id INT NOT NULL,
                jenis_aset ENUM('tanah', 'tanah_bangunan') NOT NULL,
                alamat TEXT NOT NULL,
                kecamatan VARCHAR(100) NOT NULL,
                kelurahan VARCHAR(100) NOT NULL,
                luas_tanah DECIMAL(10,2) NOT NULL,
                luas_bangunan DECIMAL(10,2) DEFAULT NULL,
                harga_sewa DECIMAL(15,2) NOT NULL,
                status_sewa ENUM('aktif', 'berakhir', 'dibatalkan') NOT NULL DEFAULT 'aktif',
                tanggal_mulai DATE NOT NULL,
                tanggal_berakhir DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (aset_id) REFERENCES aset_sewa(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # Create default admin if none exists
        cur.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
        if cur.fetchone()[0] == 0:
            hashed_pw = generate_password_hash('admin123')
            cur.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('Administrator', 'admin@telkom.co.id', hashed_pw, 'admin'))

        mysql.connection.commit()
        cur.close()
        print("✅ DB check done: users table ready, admin ensured.")
    except Exception as e:
        print(f"❌ Error init DB: {e}")
