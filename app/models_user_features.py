"""
Models for user-related features: favorit, notifikasi, histori, and asset management
"""

from flask import current_app
from app import mysql
from datetime import datetime

class FavoritAset:
    """Model for favorite assets"""
    
    def __init__(self, user_id, aset_id, catatan=None):
        self.user_id = user_id
        self.aset_id = aset_id
        self.catatan = catatan
    
    def save(self):
        """Save favorite asset to database"""
        try:
            cur = mysql.connection.cursor()
            
            # Check if already exists
            cur.execute("""
                SELECT id FROM favorit_aset 
                WHERE user_id = %s AND aset_id = %s
            """, (self.user_id, self.aset_id))
            
            if cur.fetchone():
                cur.close()
                return False, "Asset sudah ada di favorit"
            
            # Insert new favorite
            cur.execute("""
                INSERT INTO favorit_aset (user_id, aset_id, catatan, created_at)
                VALUES (%s, %s, %s, %s)
            """, (self.user_id, self.aset_id, self.catatan, datetime.now()))
            
            mysql.connection.commit()
            cur.close()
            return True, "Asset berhasil ditambahkan ke favorit"
            
        except Exception as e:
            current_app.logger.error(f"Error saving favorite: {str(e)}")
            return False, "Gagal menambahkan ke favorit"
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get all favorites for a user"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT f.id, f.aset_id, f.catatan, f.created_at,
                       a.jenis, a.alamat, a.kecamatan, a.kelurahan,
                       a.luas_tanah, a.luas_bangunan, a.harga_sewa, a.status
                FROM favorit_aset f
                JOIN aset_sewa a ON f.aset_id = a.id
                WHERE f.user_id = %s
                ORDER BY f.created_at DESC
            """, (user_id,))
            
            favorites = cur.fetchall()
            cur.close()
            return favorites
            
        except Exception as e:
            current_app.logger.error(f"Error getting favorites: {str(e)}")
            return []
    
    @staticmethod
    def delete(user_id, aset_id):
        """Remove asset from favorites"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                DELETE FROM favorit_aset 
                WHERE user_id = %s AND aset_id = %s
            """, (user_id, aset_id))
            
            mysql.connection.commit()
            deleted = cur.rowcount > 0
            cur.close()
            
            return deleted
            
        except Exception as e:
            current_app.logger.error(f"Error deleting favorite: {str(e)}")
            return False

class NotifikasiUser:
    """Model for user notifications"""
    
    def __init__(self, user_id, jenis, judul, pesan, action_url=None):
        self.user_id = user_id
        self.jenis = jenis  # 'kontrak', 'pembayaran', 'sistem', 'promo'
        self.judul = judul
        self.pesan = pesan
        self.action_url = action_url
    
    def save(self):
        """Save notification to database"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO notifikasi_user (user_id, jenis, judul, pesan, action_url, is_read, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (self.user_id, self.jenis, self.judul, self.pesan, 
                  self.action_url, False, datetime.now()))
            
            mysql.connection.commit()
            cur.close()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error saving notification: {str(e)}")
            return False
    
    @staticmethod
    def get_by_user_id(user_id, limit=20):
        """Get notifications for a user"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, jenis, judul, pesan, action_url, is_read, created_at
                FROM notifikasi_user 
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
            
            notifications = cur.fetchall()
            cur.close()
            return notifications
            
        except Exception as e:
            current_app.logger.error(f"Error getting notifications: {str(e)}")
            return []
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark notification as read"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE notifikasi_user 
                SET is_read = %s, updated_at = %s
                WHERE id = %s AND user_id = %s
            """, (True, datetime.now(), notification_id, user_id))
            
            mysql.connection.commit()
            cur.close()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM notifikasi_user 
                WHERE user_id = %s AND is_read = 0
            """, (user_id,))
            
            count = cur.fetchone()[0]
            cur.close()
            return count
            
        except Exception as e:
            current_app.logger.error(f"Error getting unread count: {str(e)}")
            return 0

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE notifikasi_user 
                SET is_read = %s, updated_at = %s
                WHERE user_id = %s AND is_read = 0
            """, (True, datetime.now(), user_id))
            
            mysql.connection.commit()
            cur.close()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error marking all notifications as read: {str(e)}")
            return False
    
class HistoriSewa:
    """Model for rental history"""
    
    def __init__(self, user_id, aset_id, jenis_aset, alamat, kecamatan, kelurahan,
                 luas_tanah, luas_bangunan, harga_sewa, status_sewa, 
                 tanggal_mulai, tanggal_berakhir):
        self.user_id = user_id
        self.aset_id = aset_id
        self.jenis_aset = jenis_aset
        self.alamat = alamat
        self.kecamatan = kecamatan
        self.kelurahan = kelurahan
        self.luas_tanah = luas_tanah
        self.luas_bangunan = luas_bangunan
        self.harga_sewa = harga_sewa
        self.status_sewa = status_sewa
        self.tanggal_mulai = tanggal_mulai
        self.tanggal_berakhir = tanggal_berakhir
    
    def save(self):
        """Save rental history to database"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO histori_sewa (
                    user_id, aset_id, jenis_aset, alamat, kecamatan, kelurahan,
                    luas_tanah, luas_bangunan, harga_sewa, status_sewa,
                    tanggal_mulai, tanggal_berakhir, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.user_id, self.aset_id, self.jenis_aset, self.alamat,
                self.kecamatan, self.kelurahan, self.luas_tanah, self.luas_bangunan,
                self.harga_sewa, self.status_sewa, self.tanggal_mulai,
                self.tanggal_berakhir, datetime.now()
            ))
            
            mysql.connection.commit()
            cur.close()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error saving rental history: {str(e)}")
            return False
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get rental history for a user"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, aset_id, jenis_aset, alamat, kecamatan, kelurahan,
                       luas_tanah, luas_bangunan, harga_sewa, status_sewa,
                       tanggal_mulai, tanggal_berakhir, created_at
                FROM histori_sewa 
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            
            history = cur.fetchall()
            cur.close()
            return history
            
        except Exception as e:
            current_app.logger.error(f"Error getting rental history: {str(e)}")
            return []

class AsetSewa:
    """Model for rental assets"""
    
    def __init__(self, jenis, alamat, kecamatan, kelurahan, luas_tanah,
                 luas_bangunan=None, kamar_tidur=None, kamar_mandi=None,
                 jumlah_lantai=None, harga_prediksi=None, harga_sewa=None):
        self.jenis = jenis
        self.alamat = alamat
        self.kecamatan = kecamatan
        self.kelurahan = kelurahan
        self.luas_tanah = luas_tanah
        self.luas_bangunan = luas_bangunan
        self.kamar_tidur = kamar_tidur
        self.kamar_mandi = kamar_mandi
        self.jumlah_lantai = jumlah_lantai
        self.harga_prediksi = harga_prediksi
        self.harga_sewa = harga_sewa
    
    def save(self):
        """Save asset to database"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO aset_sewa (
                    jenis, alamat, kecamatan, kelurahan, luas_tanah,
                    luas_bangunan, kamar_tidur, kamar_mandi, jumlah_lantai,
                    harga_prediksi, harga_sewa, status, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.jenis, self.alamat, self.kecamatan, self.kelurahan,
                self.luas_tanah, self.luas_bangunan, self.kamar_tidur,
                self.kamar_mandi, self.jumlah_lantai, self.harga_prediksi,
                self.harga_sewa, 'tersedia', datetime.now()
            ))
            
            mysql.connection.commit()
            asset_id = cur.lastrowid
            cur.close()
            return asset_id
            
        except Exception as e:
            current_app.logger.error(f"Error saving asset: {str(e)}")
            return None
    
    @staticmethod
    def get_all_available():
        """Get all available assets"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, jenis, alamat, kecamatan, kelurahan, luas_tanah,
                       luas_bangunan, kamar_tidur, kamar_mandi, jumlah_lantai,
                       harga_prediksi, harga_sewa, status, created_at
                FROM aset_sewa 
                WHERE status = 'tersedia'
                ORDER BY created_at DESC
            """)
            
            assets = cur.fetchall()
            cur.close()
            return assets
            
        except Exception as e:
            current_app.logger.error(f"Error getting available assets: {str(e)}")
            return []
    
    @staticmethod
    def get_by_id(asset_id):
        """Get asset by ID"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, jenis, alamat, kecamatan, kelurahan, luas_tanah,
                       luas_bangunan, kamar_tidur, kamar_mandi, jumlah_lantai,
                       harga_prediksi, harga_sewa, status, created_at
                FROM aset_sewa 
                WHERE id = %s
            """, (asset_id,))
            
            asset = cur.fetchone()
            cur.close()
            return asset
            
        except Exception as e:
            current_app.logger.error(f"Error getting asset by ID: {str(e)}")
            return None
    
    @staticmethod
    def update_status(asset_id, status):
        """Update asset status"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE aset_sewa 
                SET status = %s, updated_at = %s
                WHERE id = %s
            """, (status, datetime.now(), asset_id))
            
            mysql.connection.commit()
            cur.close()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error updating asset status: {str(e)}")
            return False
