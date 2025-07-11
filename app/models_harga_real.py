"""
Model untuk tabel harga real properti
"""

from app import mysql

class HargaTanahReal:
    def __init__(self, id=None, prediksi_id=None, harga_real=None, catatan=None, 
                 updated_by=None, updated_at=None):
        self.id = id
        self.prediksi_id = prediksi_id
        self.harga_real = harga_real
        self.catatan = catatan
        self.updated_by = updated_by
        self.updated_at = updated_at

    @staticmethod
    def get_by_prediksi_id(prediksi_id):
        """Ambil data harga real berdasarkan id prediksi"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, prediksi_id, harga_real, catatan, updated_by, updated_at
                FROM harga_tanah_real 
                WHERE prediksi_id = %s
            """, (prediksi_id,))
            row = cur.fetchone()
            cur.close()
            
            if row:
                return {
                    'id': row[0],
                    'prediksi_id': row[1],
                    'harga_real': row[2],
                    'catatan': row[3],
                    'updated_by': row[4],
                    'updated_at': row[5]
                }
            return None
        except Exception as e:
            print(f"Error getting harga real tanah: {e}")
            return None

    def save(self):
        """Simpan atau update harga real"""
        try:
            cur = mysql.connection.cursor()
            # Check if record exists
            cur.execute("SELECT id FROM harga_tanah_real WHERE prediksi_id = %s", (self.prediksi_id,))
            existing = cur.fetchone()
            
            if existing:
                # Update existing record
                cur.execute("""
                    UPDATE harga_tanah_real 
                    SET harga_real = %s, catatan = %s, updated_by = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE prediksi_id = %s
                """, (self.harga_real, self.catatan, self.updated_by, self.prediksi_id))
            else:
                # Insert new record
                cur.execute("""
                    INSERT INTO harga_tanah_real 
                    (prediksi_id, harga_real, catatan, updated_by, updated_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (self.prediksi_id, self.harga_real, self.catatan, self.updated_by))
            
            mysql.connection.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error saving harga real tanah: {e}")
            return False

    @staticmethod
    def get_all(limit=100, offset=0):
        """Ambil semua data harga real tanah dengan pagination"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT h.id, h.prediksi_id, p.kecamatan, p.kelurahan, p.luas_tanah_m2, 
                       p.harga_prediksi_tanah, h.harga_real, h.catatan, 
                       h.updated_by, h.updated_at
                FROM harga_tanah_real h
                JOIN prediksi_properti_tanah p ON h.prediksi_id = p.id
                ORDER BY h.updated_at DESC 
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            cur.close()
            
            result = []
            for row in rows:
                result.append({
                    'id': row[0],
                    'prediksi_id': row[1],
                    'kecamatan': row[2],
                    'kelurahan': row[3],
                    'luas_tanah_m2': row[4],
                    'harga_prediksi': row[5],
                    'harga_real': row[6],
                    'catatan': row[7],
                    'updated_by': row[8],
                    'updated_at': row[9]
                })
            return result
        except Exception as e:
            print(f"Error getting all harga real tanah: {e}")
            return []

    @staticmethod
    def get_statistics():
        """Ambil statistik harga real tanah"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT COUNT(*), AVG(harga_real), MIN(harga_real), MAX(harga_real)
                FROM harga_tanah_real 
                WHERE harga_real IS NOT NULL AND harga_real > 0
            """)
            stats = cur.fetchone()
            cur.close()
            return stats
        except Exception as e:
            print(f"Error getting statistics for harga real tanah: {e}")
            return (0, 0, 0, 0)


class HargaBangunanTanahReal:
    def __init__(self, id=None, prediksi_id=None, harga_real=None, catatan=None, 
                 updated_by=None, updated_at=None):
        self.id = id
        self.prediksi_id = prediksi_id
        self.harga_real = harga_real
        self.catatan = catatan
        self.updated_by = updated_by
        self.updated_at = updated_at

    @staticmethod
    def get_by_prediksi_id(prediksi_id):
        """Ambil data harga real berdasarkan id prediksi"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, prediksi_id, harga_real, catatan, updated_by, updated_at
                FROM harga_bangunan_tanah_real 
                WHERE prediksi_id = %s
            """, (prediksi_id,))
            row = cur.fetchone()
            cur.close()
            
            if row:
                return {
                    'id': row[0],
                    'prediksi_id': row[1],
                    'harga_real': row[2],
                    'catatan': row[3],
                    'updated_by': row[4],
                    'updated_at': row[5]
                }
            return None
        except Exception as e:
            print(f"Error getting harga real bangunan tanah: {e}")
            return None

    def save(self):
        """Simpan atau update harga real"""
        try:
            cur = mysql.connection.cursor()
            # Check if record exists
            cur.execute("SELECT id FROM harga_bangunan_tanah_real WHERE prediksi_id = %s", (self.prediksi_id,))
            existing = cur.fetchone()
            
            if existing:
                # Update existing record
                cur.execute("""
                    UPDATE harga_bangunan_tanah_real 
                    SET harga_real = %s, catatan = %s, updated_by = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE prediksi_id = %s
                """, (self.harga_real, self.catatan, self.updated_by, self.prediksi_id))
            else:
                # Insert new record
                cur.execute("""
                    INSERT INTO harga_bangunan_tanah_real 
                    (prediksi_id, harga_real, catatan, updated_by, updated_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (self.prediksi_id, self.harga_real, self.catatan, self.updated_by))
            
            mysql.connection.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"Error saving harga real bangunan tanah: {e}")
            return False

    @staticmethod
    def get_all(limit=100, offset=0):
        """Ambil semua data harga real bangunan tanah dengan pagination"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT h.id, h.prediksi_id, p.kecamatan, p.luas_tanah_m2, p.luas_bangunan_m2,
                       p.harga_prediksi_total, h.harga_real, h.catatan, 
                       h.updated_by, h.updated_at
                FROM harga_bangunan_tanah_real h
                JOIN prediksi_properti_bangunan_tanah p ON h.prediksi_id = p.id
                ORDER BY h.updated_at DESC 
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            cur.close()
            
            result = []
            for row in rows:
                result.append({
                    'id': row[0],
                    'prediksi_id': row[1],
                    'kecamatan': row[2],
                    'luas_tanah_m2': row[3],
                    'luas_bangunan_m2': row[4],
                    'harga_prediksi': row[5],
                    'harga_real': row[6],
                    'catatan': row[7],
                    'updated_by': row[8],
                    'updated_at': row[9]
                })
            return result
        except Exception as e:
            print(f"Error getting all harga real bangunan tanah: {e}")
            return []

    @staticmethod
    def get_statistics():
        """Ambil statistik harga real bangunan tanah"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT COUNT(*), AVG(harga_real), MIN(harga_real), MAX(harga_real)
                FROM harga_bangunan_tanah_real 
                WHERE harga_real IS NOT NULL AND harga_real > 0
            """)
            stats = cur.fetchone()
            cur.close()
            return stats
        except Exception as e:
            print(f"Error getting statistics for harga real bangunan tanah: {e}")
            return (0, 0, 0, 0)
