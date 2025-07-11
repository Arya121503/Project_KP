"""
Routes untuk manajemen harga real properti
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import mysql
from .models_harga_real import HargaTanahReal, HargaBangunanTanahReal
from .prediction_models import PrediksiPropertiTanah, PrediksiPropertiBangunanTanah
from datetime import datetime
from flask import current_app

harga_real = Blueprint('harga_real', __name__)

@harga_real.route('/admin/harga-real/tanah', methods=['GET'])
def manajemen_harga_real_tanah():
    """Halaman manajemen harga real tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini', 'danger')
        return redirect(url_for('main.login'))
    
    page = request.args.get('page', 1, type=int)
    limit = 10
    offset = (page - 1) * limit
    
    # Get data prediksi tanah
    prediksi_tanah_tuples = PrediksiPropertiTanah.get_all(limit=limit, offset=offset)
    
    # Convert tuples to lists so we can modify them
    prediksi_tanah = []
    
    # Get harga real for each prediksi if available
    for tanah in prediksi_tanah_tuples:
        tanah_list = list(tanah)
        harga_real = HargaTanahReal.get_by_prediksi_id(tanah[0])
        if harga_real:
            tanah_list.extend([harga_real['harga_real'], harga_real['catatan']])
        else:
            tanah_list.extend([None, None])
        prediksi_tanah.append(tanah_list)
    
    # Get total count for pagination
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM prediksi_properti_tanah")
    total_items = cur.fetchone()[0]
    cur.close()
    
    total_pages = (total_items + limit - 1) // limit
    
    return render_template('manajemen_harga_real_tanah.html', 
                           prediksi_tanah=prediksi_tanah,
                           page=page,
                           total_pages=total_pages)

@harga_real.route('/admin/harga-real/bangunan-tanah', methods=['GET'])
def manajemen_harga_real_bangunan_tanah():
    """Halaman manajemen harga real bangunan tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Anda tidak memiliki akses ke halaman ini', 'danger')
        return redirect(url_for('main.login'))
    
    page = request.args.get('page', 1, type=int)
    limit = 10
    offset = (page - 1) * limit
    
    # Get data prediksi bangunan tanah
    prediksi_bangunan_tuples = PrediksiPropertiBangunanTanah.get_all(limit=limit, offset=offset)
    
    # Convert tuples to lists so we can modify them
    prediksi_bangunan = []
    
    # Get harga real for each prediksi if available
    for bangunan in prediksi_bangunan_tuples:
        bangunan_list = list(bangunan)
        harga_real = HargaBangunanTanahReal.get_by_prediksi_id(bangunan[0])
        if harga_real:
            bangunan_list.extend([harga_real['harga_real'], harga_real['catatan']])
        else:
            bangunan_list.extend([None, None])
        prediksi_bangunan.append(bangunan_list)
    
    # Get total count for pagination
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM prediksi_properti_bangunan_tanah")
    total_items = cur.fetchone()[0]
    cur.close()
    
    total_pages = (total_items + limit - 1) // limit
    
    return render_template('manajemen_harga_real_bangunan_tanah.html', 
                           prediksi_bangunan=prediksi_bangunan,
                           page=page,
                           total_pages=total_pages)

@harga_real.route('/admin/harga-real/tanah/save', methods=['POST'])
def save_harga_real_tanah():
    """Simpan atau update harga real tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
    
    try:
        data = request.get_json()
        prediksi_id = data.get('prediksi_id')
        harga_real = data.get('harga_real')
        catatan = data.get('catatan', '')
        
        if not prediksi_id or not harga_real:
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Convert harga_real from string to number if needed
        try:
            harga_real = float(harga_real.replace(',', '').replace('.', '')) if isinstance(harga_real, str) else float(harga_real)
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid price format'}), 400
            
        harga_obj = HargaTanahReal(
            prediksi_id=prediksi_id,
            harga_real=harga_real,
            catatan=catatan,
            updated_by=session.get('user_name', 'Admin')
        )
        
        if harga_obj.save():
            return jsonify({'success': True, 'message': 'Harga real tanah berhasil disimpan'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save data'}), 500
    except Exception as e:
        current_app.logger.error(f"Error saving harga real tanah: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@harga_real.route('/admin/harga-real/bangunan-tanah/save', methods=['POST'])
def save_harga_real_bangunan_tanah():
    """Simpan atau update harga real bangunan tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
    
    try:
        data = request.get_json()
        prediksi_id = data.get('prediksi_id')
        harga_real = data.get('harga_real')
        catatan = data.get('catatan', '')
        
        if not prediksi_id or not harga_real:
            return jsonify({'success': False, 'error': 'Missing required data'}), 400
        
        # Convert harga_real from string to number if needed
        try:
            harga_real = float(harga_real.replace(',', '').replace('.', '')) if isinstance(harga_real, str) else float(harga_real)
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid price format'}), 400
            
        harga_obj = HargaBangunanTanahReal(
            prediksi_id=prediksi_id,
            harga_real=harga_real,
            catatan=catatan,
            updated_by=session.get('user_name', 'Admin')
        )
        
        if harga_obj.save():
            return jsonify({'success': True, 'message': 'Harga real bangunan+tanah berhasil disimpan'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save data'}), 500
    except Exception as e:
        current_app.logger.error(f"Error saving harga real bangunan tanah: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# API routes to get real prices
@harga_real.route('/api/harga-real/tanah/<int:prediksi_id>', methods=['GET'])
def get_harga_real_tanah(prediksi_id):
    """Get harga real tanah by prediksi_id"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
    
    harga_real = HargaTanahReal.get_by_prediksi_id(prediksi_id)
    if harga_real:
        return jsonify({'success': True, 'data': harga_real})
    else:
        return jsonify({'success': False, 'error': 'Data not found'}), 404

@harga_real.route('/api/harga-real/bangunan-tanah/<int:prediksi_id>', methods=['GET'])
def get_harga_real_bangunan_tanah(prediksi_id):
    """Get harga real bangunan tanah by prediksi_id"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
    
    harga_real = HargaBangunanTanahReal.get_by_prediksi_id(prediksi_id)
    if harga_real:
        return jsonify({'success': True, 'data': harga_real})
    else:
        return jsonify({'success': False, 'error': 'Data not found'}), 404
