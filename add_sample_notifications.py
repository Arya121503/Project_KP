#!/usr/bin/env python3
"""
Script untuk menambahkan sample data notifikasi user
"""

import mysql.connector
from datetime import datetime, timedelta
import random

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'db_kp'
}

def add_sample_notifications():
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Sample notification data
        sample_notifications = [
            {
                'user_id': 2,
                'jenis': 'kontrak',
                'judul': 'Kontrak Sewa Akan Berakhir',
                'pesan': 'Kontrak sewa Anda untuk properti di Jl. Raya Surabaya akan berakhir dalam 30 hari. Silakan hubungi admin untuk perpanjangan.',
                'is_read': False,
                'action_url': '#histori-sewa',
                'created_at': datetime.now() - timedelta(hours=2)
            },
            {
                'user_id': 2,
                'jenis': 'pembayaran',
                'judul': 'Reminder Pembayaran Sewa',
                'pesan': 'Pembayaran sewa bulan ini akan jatuh tempo dalam 7 hari. Jangan lupa untuk melakukan pembayaran tepat waktu.',
                'is_read': False,
                'action_url': None,
                'created_at': datetime.now() - timedelta(hours=6)
            },
            {
                'user_id': 2,
                'jenis': 'sistem',
                'judul': 'Pembaruan Sistem',
                'pesan': 'Sistem akan menjalani maintenance pada Minggu, 14 Juli 2025 pukul 02:00-04:00 WIB. Mohon maaf atas ketidaknyamanannya.',
                'is_read': True,
                'action_url': None,
                'created_at': datetime.now() - timedelta(days=1)
            },
            {
                'user_id': 2,
                'jenis': 'promo',
                'judul': 'Promo Spesial: Diskon Sewa 20%',
                'pesan': 'Dapatkan diskon 20% untuk sewa properti baru! Promo berlaku sampai akhir bulan ini. Hubungi admin untuk info lebih lanjut.',
                'is_read': False,
                'action_url': 'tel:+62211234567',
                'created_at': datetime.now() - timedelta(hours=12)
            },
            {
                'user_id': 2,
                'jenis': 'kontrak',
                'judul': 'Dokumen Kontrak Telah Diperbarui',
                'pesan': 'Dokumen kontrak sewa untuk properti di Jl. Diponegoro telah diperbarui. Silakan unduh dokumen terbaru dari halaman histori sewa.',
                'is_read': True,
                'action_url': '#histori-sewa',
                'created_at': datetime.now() - timedelta(days=2)
            },
            {
                'user_id': 2,
                'jenis': 'sistem',
                'judul': 'Selamat Datang di Portal Telkom Aset',
                'pesan': 'Terima kasih telah bergabung dengan Portal Telkom Aset. Jelajahi fitur-fitur yang tersedia dan nikmati pengalaman sewa properti yang mudah.',
                'is_read': True,
                'action_url': '#dashboard-home',
                'created_at': datetime.now() - timedelta(days=7)
            },
            {
                'user_id': 2,
                'jenis': 'pembayaran',
                'judul': 'Pembayaran Berhasil Dikonfirmasi',
                'pesan': 'Pembayaran sewa untuk periode Juni 2025 telah berhasil dikonfirmasi. Terima kasih atas pembayaran yang tepat waktu.',
                'is_read': False,
                'action_url': None,
                'created_at': datetime.now() - timedelta(hours=4)
            },
            {
                'user_id': 2,
                'jenis': 'promo',
                'judul': 'Tips Hemat: Manfaatkan Ruang Secara Optimal',
                'pesan': 'Pelajari tips dan trik dari Telkom untuk memaksimalkan pemanfaatan ruang properti sewa Anda. Klik untuk membaca artikel lengkap.',
                'is_read': True,
                'action_url': 'https://telkom.co.id/tips-properti',
                'created_at': datetime.now() - timedelta(days=3)
            }
        ]
        
        # Check if notifikasi_user already has data
        cursor.execute("SELECT COUNT(*) FROM notifikasi_user WHERE user_id = 2")
        notif_count = cursor.fetchone()[0]
        
        if notif_count == 0:
            print("Adding sample notification data...")
            for notif in sample_notifications:
                query = """
                    INSERT INTO notifikasi_user 
                    (user_id, jenis, judul, pesan, is_read, action_url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                values = (
                    notif['user_id'], notif['jenis'], notif['judul'],
                    notif['pesan'], notif['is_read'], notif['action_url'],
                    notif['created_at']
                )
                
                cursor.execute(query, values)
            
            conn.commit()
            print(f"✅ Successfully added {len(sample_notifications)} notification records")
        else:
            print(f"ℹ️ notifikasi_user table already has {notif_count} records for user 2")
        
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_sample_notifications()
