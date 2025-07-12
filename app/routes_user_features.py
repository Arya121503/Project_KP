from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import mysql
from .models import User
from datetime import datetime

# Create the Blueprint with name matching what's imported in __init__.py
user_features = Blueprint('user_features', __name__)

@user_features.route('/rental-applications')
def user_rental_applications():
    """View user's rental applications"""
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'warning')
        return redirect(url_for('main.login'))
    
    # Get user's rental applications from database
    try:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT ra.*, p.kecamatan, p.alamat, p.luas_tanah_m2, p.harga_sewa
            FROM rental_applications ra
            JOIN prediksi_properti_rental p ON ra.property_id = p.id
            WHERE ra.user_id = %s
            ORDER BY ra.created_at DESC
        """, (user_id,))
        
        applications = []
        for row in cur.fetchall():
            application = {
                'id': row[0],
                'property_id': row[1],
                'user_id': row[2],
                'start_date': row[3].strftime('%d-%m-%Y') if row[3] else None,
                'duration_months': row[4],
                'status': row[5],
                'message': row[6],
                'admin_message': row[7],
                'created_at': row[8].strftime('%d-%m-%Y %H:%M') if row[8] else None,
                'updated_at': row[9].strftime('%d-%m-%Y %H:%M') if row[9] else None,
                'kecamatan': row[10] if len(row) > 10 else None,
                'alamat': row[11] if len(row) > 11 else None,
                'luas_tanah_m2': row[12] if len(row) > 12 else None,
                'harga_sewa': row[13] if len(row) > 13 else None
            }
            applications.append(application)
        
        cur.close()
        return render_template('user_rental_applications.html', applications=applications)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('main.user_dashboard'))

@user_features.route('/api/favorit/add', methods=['POST'])
def add_to_favorit():
    """Add asset to favorites"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        aset_id = data.get('aset_id')
        tipe_aset = data.get('tipe_aset', 'tanah')  # Default to tanah if not specified
        
        if not aset_id:
            return jsonify({'success': False, 'message': 'Asset ID required'}), 400
        
        # Add to favorit table
        cur = mysql.connection.cursor()
        
        # First check if already favorited
        cur.execute(
            "SELECT id FROM favorit WHERE user_id = %s AND aset_id = %s AND tipe_aset = %s", 
            (user_id, aset_id, tipe_aset)
        )
        existing = cur.fetchone()
        
        if existing:
            cur.close()
            return jsonify({'success': False, 'message': 'Asset already in favorites'}), 400
        
        # Insert new favorite
        cur.execute(
            "INSERT INTO favorit (user_id, aset_id, tipe_aset, created_at) VALUES (%s, %s, %s, NOW())",
            (user_id, aset_id, tipe_aset)
        )
        mysql.connection.commit()
        favorit_id = cur.lastrowid
        cur.close()
        
        return jsonify({
            'success': True, 
            'message': 'Asset added to favorites successfully',
            'favorit_id': favorit_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@user_features.route('/api/favorit/remove', methods=['POST'])
def remove_from_favorit():
    """Remove asset from favorites"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        aset_id = data.get('aset_id')
        
        if not aset_id:
            return jsonify({'success': False, 'message': 'Asset ID required'}), 400
        
        # Remove from favorit table
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE FROM favorit WHERE user_id = %s AND aset_id = %s", 
            (user_id, aset_id)
        )
        mysql.connection.commit()
        deleted = cur.rowcount > 0
        cur.close()
        
        message = 'Asset removed from favorites' if deleted else 'Asset not found in favorites'
        return jsonify({'success': deleted, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@user_features.route('/api/favorit/list')
def get_favorit_list():
    """Get user's favorite assets"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        user_id = session['user_id']
        
        # Get favorites from database with join to get asset details
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT f.id, f.aset_id, f.tipe_aset, f.created_at,
                   CASE 
                       WHEN f.tipe_aset = 'tanah' THEN pt.kecamatan
                       WHEN f.tipe_aset = 'bangunan' THEN pb.kecamatan
                       ELSE NULL
                   END as kecamatan,
                   CASE 
                       WHEN f.tipe_aset = 'tanah' THEN pt.luas_tanah_m2
                       WHEN f.tipe_aset = 'bangunan' THEN pb.luas_tanah_m2
                       ELSE NULL
                   END as luas_tanah,
                   CASE 
                       WHEN f.tipe_aset = 'tanah' THEN NULL
                       WHEN f.tipe_aset = 'bangunan' THEN pb.luas_bangunan_m2
                       ELSE NULL
                   END as luas_bangunan,
                   CASE 
                       WHEN f.tipe_aset = 'tanah' THEN pt.harga_prediksi_tanah
                       WHEN f.tipe_aset = 'bangunan' THEN pb.harga_prediksi_bangunan
                       ELSE NULL
                   END as harga_prediksi
            FROM favorit f
            LEFT JOIN prediksi_properti_tanah pt ON f.aset_id = pt.id AND f.tipe_aset = 'tanah'
            LEFT JOIN prediksi_properti_bangunan_tanah pb ON f.aset_id = pb.id AND f.tipe_aset = 'bangunan'
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
        """, (user_id,))
        
        favorit_list = []
        for row in cur.fetchall():
            favorit_list.append({
                'id': row[0],
                'aset_id': row[1],
                'tipe_aset': row[2],
                'created_at': row[3].strftime('%Y-%m-%d %H:%M:%S') if row[3] else None,
                'kecamatan': row[4],
                'luas_tanah': float(row[5]) if row[5] else None,
                'luas_bangunan': float(row[6]) if row[6] else None,
                'harga_prediksi': float(row[7]) if row[7] else None
            })
        
        cur.close()
        return jsonify({'success': True, 'data': favorit_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@user_features.route('/api/favorit/count')
def get_favorit_count():
    """Get count of user's favorite assets"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM favorit WHERE user_id = %s", (user_id,))
        count = cur.fetchone()[0]
        cur.close()
        
        return jsonify({'success': True, 'count': count})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@user_features.route('/api/favorit/clear', methods=['POST'])
def clear_all_favorit():
    """Clear all user's favorite assets"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM favorit WHERE user_id = %s", (user_id,))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'All favorites cleared'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

# ===========================================
# NOTIFIKASI ROUTES
# ===========================================

@user_features.route('/api/notifikasi/list')
def get_notifikasi_list():
    """Get user's notifications"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        user_id = session['user_id']
        
        # Get notifications from database
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, judul, pesan, status_dibaca, created_at
            FROM notifikasi
            WHERE user_id = %s OR user_id = 0
            ORDER BY created_at DESC
            LIMIT 50
        """, (user_id,))
        
        notif_list = []
        for row in cur.fetchall():
            notif_list.append({
                'id': row[0],
                'judul': row[1],
                'pesan': row[2],
                'is_read': bool(row[3]),
                'created_at': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else None
            })
        
        cur.close()
        return jsonify({'success': True, 'data': notif_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

@user_features.route('/api/notifikasi/mark-read', methods=['POST'])
def mark_notifikasi_read():
    """Mark notification as read"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        notification_id = data.get('notification_id')
        
        if not notification_id:
            return jsonify({'success': False, 'message': 'Notification ID required'}), 400
        
        # Mark notification as read with direct SQL
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE notifikasi 
                SET status_dibaca = 1 
                WHERE id = %s AND (user_id = %s OR user_id = 0)
            """, (notification_id, user_id))
            
            success = cur.rowcount > 0
            mysql.connection.commit()
            cur.close()
            
            message = 'Notification marked as read' if success else 'Failed to mark as read'
            return jsonify({'success': success, 'message': message})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@user_features.route('/api/notifikasi/mark-all-read', methods=['POST'])
def mark_all_notifikasi_read():
    """Mark all notifications as read"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        user_id = session['user_id']
        # Mark all notifications as read with direct SQL
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE notifikasi 
                SET status_dibaca = 1 
                WHERE (user_id = %s OR user_id = 0) AND status_dibaca = 0
            """, (user_id,))
            
            success = True
            mysql.connection.commit()
            cur.close()
            
            return jsonify({'success': success, 'message': 'All notifications marked as read'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@user_features.route('/api/notifikasi/unread-count')
def get_unread_count():
    """Get count of unread notifications"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        user_id = session['user_id']
        # Get unread count with direct SQL
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT COUNT(id) FROM notifikasi 
                WHERE (user_id = %s OR user_id = 0) AND status_dibaca = 0
            """, (user_id,))
            
            count = cur.fetchone()[0]
            cur.close()
            
            return jsonify({'success': True, 'count': count})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

# ===========================================
# HISTORI SEWA ROUTES
# ===========================================

@user_features.route('/api/histori/list')
def get_histori_list():
    """Get user's rental history"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401
    
    try:
        user_id = session['user_id']
        # Get rental history with direct SQL
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                h.id, 
                h.aset_id, 
                h.jenis_aset,
                p.alamat,
                p.kecamatan,
                p.kelurahan,
                p.luas_tanah_m2,
                p.luas_bangunan_m2,
                p.harga_sewa,
                h.status_sewa,
                h.tanggal_mulai,
                h.tanggal_berakhir,
                h.created_at
            FROM histori_sewa h
            LEFT JOIN prediksi_properti_rental p ON h.aset_id = p.id AND h.jenis_aset = 'tanah'
            WHERE h.user_id = %s
            ORDER BY h.created_at DESC
        """, (user_id,))
        
        # Convert to list of dictionaries
        histori_list = []
        for hist in cur.fetchall():
            histori_list.append({
                'id': hist[0],
                'aset_id': hist[1],
                'jenis_aset': hist[2],
                'alamat': hist[3],
                'kecamatan': hist[4],
                'kelurahan': hist[5],
                'luas_tanah': float(hist[6]) if hist[6] else None,
                'luas_bangunan': float(hist[7]) if hist[7] else None,
                'harga_sewa': float(hist[8]) if hist[8] else None,
                'status_sewa': hist[9],
                'tanggal_mulai': hist[10].strftime('%Y-%m-%d') if hist[10] else None,
                'tanggal_berakhir': hist[11].strftime('%Y-%m-%d') if hist[11] else None,
                'created_at': hist[12].strftime('%Y-%m-%d %H:%M:%S') if hist[12] else None
            })
        cur.close()
        
        return jsonify({'success': True, 'data': histori_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

# ===========================================
# ASET SEWA ROUTES
# ===========================================

@user_features.route('/api/aset/available')
def get_available_assets():
    """Get all available rental assets"""
    try:
        # Get all available rental assets with direct SQL
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT 
                id, 
                'tanah' as jenis,
                alamat,
                kecamatan,
                kelurahan,
                luas_tanah_m2 as luas_tanah,
                luas_bangunan_m2 as luas_bangunan,
                kamar_tidur,
                kamar_mandi,
                lantai,
                harga_prediksi,
                harga_sewa,
                status,
                created_at
            FROM prediksi_properti_rental
            WHERE status = 'available'
            ORDER BY created_at DESC
        """)
        
        # Convert to list of dictionaries
        aset_list = []
        for aset in cur.fetchall():
            aset_list.append({
                'id': aset[0],
                'jenis': aset[1],
                'alamat': aset[2],
                'kecamatan': aset[3],
                'kelurahan': aset[4],
                'luas_tanah': float(aset[5]) if aset[5] else None,
                'luas_bangunan': float(aset[6]) if aset[6] else None,
                'kamar_tidur': aset[7],
                'kamar_mandi': aset[8],
                'jumlah_lantai': aset[9],
                'harga_prediksi': float(aset[10]) if aset[10] else None,
                'harga_sewa': float(aset[11]) if aset[11] else None,
                'status': aset[12],
                'created_at': aset[13].strftime('%Y-%m-%d %H:%M:%S') if aset[13] else None
            })
        cur.close()
        
        return jsonify({'success': True, 'data': aset_list})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@user_features.route('/api/aset/create', methods=['POST'])
def create_rental_asset():
    """Create new rental asset from prediction"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        
        # Create asset from prediction data with direct SQL
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO prediksi_properti_rental (
                kecamatan, 
                kelurahan, 
                alamat, 
                luas_tanah_m2, 
                luas_bangunan_m2, 
                kamar_tidur, 
                kamar_mandi, 
                lantai, 
                harga_prediksi, 
                harga_sewa,
                status,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'available', NOW())
        """, (
            data.get('kecamatan'),
            data.get('kelurahan'),
            data.get('alamat'),
            data.get('luas_tanah'),
            data.get('luas_bangunan'),
            data.get('kamar_tidur'),
            data.get('kamar_mandi'),
            data.get('jumlah_lantai'),
            data.get('harga_prediksi'),
            data.get('harga_sewa')
        ))
        
        asset_id = cur.lastrowid
        mysql.connection.commit()
        
        if asset_id:
            # Create notification for all users with direct SQL
            cur.execute("""
                INSERT INTO notifikasi (
                    user_id, 
                    jenis, 
                    judul, 
                    pesan, 
                    status_dibaca,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                0,  # System notification (for all users)
                'sistem',
                'Aset Baru Tersedia',
                f'Aset baru tersedia untuk disewa di {data.get("kecamatan")}, {data.get("kelurahan")}',
                0  # Unread
            ))
            mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'success': bool(asset_id), 
            'message': 'Asset created successfully' if asset_id else 'Failed to create asset',
            'asset_id': asset_id
        }), 200 if asset_id else 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

# ===========================================
# ADMIN NOTIFICATION ROUTES
# ===========================================

@user_features.route('/admin/send-notification', methods=['POST'])
def send_notification():
    """Send notification to users (admin only)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        
        # Get target users
        target_users = data.get('target_users', 'all')  # 'all' or list of user_ids
        
        if target_users == 'all':
            # Send to all users with direct SQL
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE role = 'pengguna'")
            users = cur.fetchall()
            
            success_count = 0
            for user in users:
                try:
                    # Add notification to database
                    cur.execute("""
                        INSERT INTO notifikasi (
                            user_id, 
                            jenis, 
                            judul, 
                            pesan, 
                            action_url,
                            status_dibaca,
                            created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        user[0],
                        data.get('jenis', 'sistem'),
                        data.get('judul'),
                        data.get('pesan'),
                        data.get('action_url', ''),
                        0  # Unread
                    ))
                    mysql.connection.commit()
                    success_count += 1
                except Exception as e:
                    # Continue with next user if one fails
                    continue
            
            cur.close()
            return jsonify({
                'success': True, 
                'message': f'Notification sent to {success_count} users'
            })
        else:
            # Send to specific users with direct SQL
            cur = mysql.connection.cursor()
            success_count = 0
            
            for user_id in target_users:
                try:
                    # Add notification to database
                    cur.execute("""
                        INSERT INTO notifikasi (
                            user_id, 
                            jenis, 
                            judul, 
                            pesan, 
                            action_url,
                            status_dibaca,
                            created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        user_id,
                        data.get('jenis', 'sistem'),
                        data.get('judul'),
                        data.get('pesan'),
                        data.get('action_url', ''),
                        0  # Unread
                    ))
                    mysql.connection.commit()
                    success_count += 1
                except Exception as e:
                    # Continue with next user if one fails
                    continue
            
            cur.close()
            return jsonify({
                'success': True, 
                'message': f'Notification sent to {success_count} users'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500
