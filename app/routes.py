from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql
from .models import User
from .data_processor import AssetDataProcessor, TanahDataProcessor
from .prediction_models import PrediksiPropertiTanah, PrediksiPropertiBangunanTanah
from .ml_predictor import PropertyPricePredictor
from datetime import datetime
import json

main = Blueprint('main', __name__)

data_processor = AssetDataProcessor()
tanah_processor = TanahDataProcessor()

@main.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        else:
            return redirect(url_for('main.user_dashboard'))
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, password, role, email, phone, address, updated_at FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['role'] = user[3]
            session['user_email'] = user[4]
            session['user_phone'] = user[5] if user[5] else ''
            session['user_address'] = user[6] if user[6] else ''
            session['join_date'] = user[7].strftime('%d %B %Y') if user[7] else 'N/A'
            session['username'] = user[4]  # Use email as username display

            if user[3] == 'admin':
                flash('Login admin berhasil.', 'success')
                return redirect(url_for('main.admin_dashboard'))
            else:
                flash('Login pengguna berhasil.', 'success')
                return redirect(url_for('main.user_dashboard'))
        else:
            flash('Email atau password salah.', 'error')

    return render_template('login_register.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'pengguna')

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Email sudah terdaftar.', 'error')
        else:
            hashed_password = generate_password_hash(password)
            cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                        (name, email, hashed_password, role))
            mysql.connection.commit()
            flash('Registrasi berhasil. Silakan login.', 'success')
            cur.close()
            return redirect(url_for('main.login'))

        cur.close()

    return render_template('login_register.html')

@main.route('/admin-dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))

    # Dapatkan statistik untuk dashboard
    stats = data_processor.get_statistics()
    stats_tanah = PrediksiPropertiTanah.get_statistics()
    stats_bangunan = PrediksiPropertiBangunanTanah.get_statistics()
    
    # Dapatkan jumlah pengguna
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(id) FROM users WHERE role = 'pengguna'")
    total_users = cur.fetchone()[0]
    cur.close()
    
    # Gabungkan statistik (stats_tanah dan stats_bangunan adalah tuple dari fetchone())
    total_tanah = stats_tanah[0] if stats_tanah and stats_tanah[0] else 0
    avg_price_tanah = stats_tanah[1] if stats_tanah and stats_tanah[1] else 0
    
    total_bangunan = stats_bangunan[0] if stats_bangunan and stats_bangunan[0] else 0
    avg_price_bangunan = stats_bangunan[1] if stats_bangunan and stats_bangunan[1] else 0

    combined_stats = {
        'total_properties': total_tanah + total_bangunan,
        'avg_price': (avg_price_tanah + avg_price_bangunan) / 2 if avg_price_tanah > 0 or avg_price_bangunan > 0 else 0,
        'total_locations': 31,  # Total kecamatan di Surabaya
        'total_users': total_users
    }

    return render_template('dashboard_admin.html', 
                         stats=combined_stats, 
                         stats_tanah=stats_tanah, 
                         stats_bangunan=stats_bangunan,
                         current_date=datetime.now().strftime('%d %B %Y, %H:%M'))

@main.route('/user-dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('main.login'))
    
    # Initialize empty lists since we removed harga_real feature
    all_real_data = []
    
    # Sort by update date
    all_real_data.sort(key=lambda x: x['updated_at'], reverse=True)

    return render_template('dashboard_user.html', properties=all_real_data)

@main.route('/logout')
def logout_user():
    session.clear()
    flash('Logout berhasil.', 'success')
    return redirect(url_for('main.login'))

# API Routes untuk Visualisasi Data
@main.route('/api/visualization/stats')
def get_visualization_stats():
    """Get statistics for visualization dashboard"""
    data_type = request.args.get('data_type', 'prediksi')
    try:
        # All data is now prediction data since harga_real feature is removed
        stats_tanah = PrediksiPropertiTanah.get_statistics()
        stats_bangunan = PrediksiPropertiBangunanTanah.get_statistics()
        
        # Calculate combined statistics
        total_tanah = stats_tanah[0] if stats_tanah and stats_tanah[0] else 0
        total_bangunan = stats_bangunan[0] if stats_bangunan and stats_bangunan[0] else 0
        
        avg_price_tanah = stats_tanah[1] if stats_tanah and stats_tanah[1] else 0
        avg_price_bangunan = stats_bangunan[1] if stats_bangunan and stats_bangunan[1] else 0
        
        min_price_tanah = stats_tanah[2] if stats_tanah and stats_tanah[2] else 0
        min_price_bangunan = stats_bangunan[2] if stats_bangunan and stats_bangunan[2] else 0
        
        max_price_tanah = stats_tanah[3] if stats_tanah and stats_tanah[3] else 0
        max_price_bangunan = stats_bangunan[3] if stats_bangunan and stats_bangunan[3] else 0
        
        # Calculate weighted averages and totals
        total_properties = total_tanah + total_bangunan
        avg_price = ((avg_price_tanah * total_tanah) + (avg_price_bangunan * total_bangunan)) / total_properties if total_properties > 0 else 0
        min_price = min(min_price_tanah, min_price_bangunan) if min_price_tanah > 0 and min_price_bangunan > 0 else max(min_price_tanah, min_price_bangunan)
        max_price = max(max_price_tanah, max_price_bangunan)
        
        return jsonify({
            'success': True,
            'data': {
                'total_assets': total_properties,
                'avg_price': avg_price,
                'min_price': min_price,
                'max_price': max_price,
                'total_tanah': total_tanah,
                'total_bangunan': total_bangunan,
                'avg_price_tanah': avg_price_tanah,
                'avg_price_bangunan': avg_price_bangunan
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/visualization/location-analysis')
def get_location_analysis():
    """Get location-based analysis for all kecamatan (Optimized and cleaned)"""
    try:
        cur = mysql.connection.cursor()
        
        # Only use prediction data since real data feature is removed
        query = """
            SELECT 
                k.kecamatan,
                COALESCE(t.tanah_count, 0) as tanah_count,
                COALESCE(t.tanah_total_value, 0) as tanah_total_value,
                COALESCE(t.tanah_avg_price, 0) as tanah_avg_price,
                COALESCE(b.bangunan_count, 0) as bangunan_count,
                COALESCE(b.bangunan_total_value, 0) as bangunan_total_value,
                COALESCE(b.bangunan_avg_price, 0) as bangunan_avg_price,
                (COALESCE(t.tanah_count, 0) + COALESCE(b.bangunan_count, 0)) as total_properties,
                (COALESCE(t.tanah_total_value, 0) + COALESCE(b.bangunan_total_value, 0)) as total_value
            FROM (
                SELECT DISTINCT kecamatan FROM prediksi_properti_tanah 
                WHERE kecamatan NOT LIKE '%prajurit%'
                UNION
                SELECT DISTINCT kecamatan FROM prediksi_properti_bangunan_tanah
                WHERE kecamatan NOT LIKE '%prajurit%'
            ) k
            LEFT JOIN (
                SELECT 
                    kecamatan,
                    COUNT(*) as tanah_count,
                    SUM(harga_prediksi_tanah) as tanah_total_value,
                    AVG(harga_prediksi_tanah) as tanah_avg_price,
                    MIN(harga_prediksi_tanah) as tanah_min_price,
                    MAX(harga_prediksi_tanah) as tanah_max_price
                FROM prediksi_properti_tanah 
                WHERE kecamatan NOT LIKE '%prajurit%'
                GROUP BY kecamatan
            ) t ON k.kecamatan = t.kecamatan
            LEFT JOIN (
                SELECT 
                    kecamatan,
                    COUNT(*) as bangunan_count,
                    SUM(harga_prediksi_total) as bangunan_total_value,
                    AVG(harga_prediksi_total) as bangunan_avg_price,
                    MIN(harga_prediksi_total) as bangunan_min_price,
                    MAX(harga_prediksi_total) as bangunan_max_price
                FROM prediksi_properti_bangunan_tanah 
                WHERE kecamatan NOT LIKE '%prajurit%'
                GROUP BY kecamatan
            ) b ON k.kecamatan = b.kecamatan
            WHERE (COALESCE(t.tanah_count, 0) + COALESCE(b.bangunan_count, 0)) > 0
            ORDER BY total_value DESC
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        
        # Process optimized data
        location_data = []
        for row in rows:
            total_properties = row[7]
            total_value = row[8]
            avg_price = total_value / total_properties if total_properties > 0 else 0
            
            location_data.append({
                'kecamatan': row[0],
                'tanah_count': row[1],
                'bangunan_count': row[4],
                'total_properties': total_properties,
                'tanah_avg': row[3],
                'bangunan_avg': row[6],
                'avg_price': avg_price,
                'total_value': total_value,
                'min_price': min(row[3] or 0, row[6] or 0) if (row[3] and row[6]) else (row[3] or row[6] or 0),
                'max_price': max(row[3] or 0, row[6] or 0)
            })
        
        return jsonify({
            'success': True,
            'data': location_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/visualization/property-type-distribution')
def get_property_type_distribution():
    """Get property type distribution"""
    try:
        cur = mysql.connection.cursor()
        
        # Get counts from both tables
        cur.execute("SELECT COUNT(*) FROM prediksi_properti_tanah")
        tanah_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM prediksi_properti_bangunan_tanah")
        bangunan_count = cur.fetchone()[0]
        
        cur.close()
        
        return jsonify({
            'success': True,
            'data': [
                {'type': 'Tanah', 'count': tanah_count, 'percentage': tanah_count / (tanah_count + bangunan_count) * 100 if (tanah_count + bangunan_count) > 0 else 0},
                {'type': 'Bangunan + Tanah', 'count': bangunan_count, 'percentage': bangunan_count / (tanah_count + bangunan_count) * 100 if (tanah_count + bangunan_count) > 0 else 0}
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/visualization/certificate-analysis')
def get_certificate_analysis():
    """Get certificate analysis from both tables (excluding Prajuritkulon)"""
    try:
        cur = mysql.connection.cursor()
        
        # Get certificate distribution from both tables with Prajuritkulon filter
        cur.execute("""
            SELECT 
                jenis_sertifikat as certificate,
                COUNT(*) as count,
                AVG(harga_prediksi_tanah) as avg_price,
                'tanah' as type
            FROM prediksi_properti_tanah 
            WHERE jenis_sertifikat IS NOT NULL AND jenis_sertifikat != ''
            AND kecamatan NOT LIKE '%prajurit%'
            GROUP BY jenis_sertifikat
            
            UNION ALL
            
            SELECT 
                sertifikat as certificate,
                COUNT(*) as count,
                AVG(harga_prediksi_total) as avg_price,
                'bangunan' as type
            FROM prediksi_properti_bangunan_tanah 
            WHERE sertifikat IS NOT NULL AND sertifikat != ''
            AND kecamatan NOT LIKE '%prajurit%'
            GROUP BY sertifikat
        """)
        
        rows = cur.fetchall()
        cur.close()
        
        # Process data to combine certificates
        cert_data = {}
        for row in rows:
            cert = row[0]
            if cert not in cert_data:
                cert_data[cert] = {
                    'certificate': cert,
                    'total_count': 0,
                    'total_value': 0,
                    'avg_price': 0
                }
            
            cert_data[cert]['total_count'] += row[1]
            cert_data[cert]['total_value'] += (row[2] if row[2] else 0) * row[1]
        
        # Calculate average prices
        for cert in cert_data:
            if cert_data[cert]['total_count'] > 0:
                cert_data[cert]['avg_price'] = cert_data[cert]['total_value'] / cert_data[cert]['total_count']
        
        sorted_data = sorted(cert_data.values(), key=lambda x: x['total_count'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': sorted_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/visualization/price-range-distribution')
def get_price_range_distribution():
    """Get price range distribution"""
    try:
        cur = mysql.connection.cursor()
        
        # Define price ranges
        price_ranges = [
            (0, 500000000, "< 500 Juta"),
            (500000000, 1000000000, "500 Juta - 1 Milyar"),
            (1000000000, 2000000000, "1 - 2 Milyar"),
            (2000000000, 5000000000, "2 - 5 Milyar"),
            (5000000000, float('inf'), "> 5 Milyar")
        ]
        
        result_data = []
        
        for min_price, max_price, label in price_ranges:
            # Count from tanah table
            if max_price == float('inf'):
                cur.execute("""
                    SELECT COUNT(*) FROM prediksi_properti_tanah 
                    WHERE harga_prediksi_tanah >= %s
                """, (min_price,))
                tanah_count = cur.fetchone()[0]
                
                cur.execute("""
                    SELECT COUNT(*) FROM prediksi_properti_bangunan_tanah 
                    WHERE harga_prediksi_total >= %s
                """, (min_price,))
                bangunan_count = cur.fetchone()[0]
            else:
                cur.execute("""
                    SELECT COUNT(*) FROM prediksi_properti_tanah 
                    WHERE harga_prediksi_tanah >= %s AND harga_prediksi_tanah < %s
                """, (min_price, max_price))
                tanah_count = cur.fetchone()[0]
                
                cur.execute("""
                    SELECT COUNT(*) FROM prediksi_properti_bangunan_tanah 
                    WHERE harga_prediksi_total >= %s AND harga_prediksi_total < %s
                """, (min_price, max_price))
                bangunan_count = cur.fetchone()[0]
            
            total_count = tanah_count + bangunan_count
            result_data.append({
                'range': label,
                'count': total_count,
                'tanah_count': tanah_count,
                'bangunan_count': bangunan_count
            })
        
        cur.close()
        
        return jsonify({
            'success': True,
            'data': result_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/visualization/building-condition-analysis')
def get_building_condition_analysis():
    """Get building condition analysis"""
    try:
        # Get building condition analysis
        condition_data = PrediksiPropertiBangunanTanah.get_building_condition_analysis()
        
        result_data = []
        for row in condition_data:
            result_data.append({
                'condition': row[0],
                'count': row[1],
                'avg_price': row[2] if row[2] else 0,
                'avg_price_per_m2': row[3] if row[3] else 0
            })
        
        return jsonify({
            'success': True,
            'data': result_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/visualization/trend-analysis')
def get_trend_analysis():
    """Get trend analysis data"""
    try:
        cur = mysql.connection.cursor()
        
        # Get monthly trends (simulated based on creation dates)
        cur.execute("""
            SELECT 
                DATE_FORMAT(created_at, '%Y-%m') as month,
                COUNT(*) as total_properties,
                AVG(harga_prediksi_tanah) as avg_price,
                'tanah' as type
            FROM prediksi_properti_tanah 
            GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            
            UNION ALL
            
            SELECT 
                DATE_FORMAT(created_at, '%Y-%m') as month,
                COUNT(*) as total_properties,
                AVG(harga_prediksi_total) as avg_price,
                'bangunan' as type
            FROM prediksi_properti_bangunan_tanah 
            GROUP BY DATE_FORMAT(created_at, '%Y-%m')
            
            ORDER BY month
        """)
        
        rows = cur.fetchall()
        cur.close()
        
        # Process data to combine by month
        trend_data = {}
        for row in rows:
            month = row[0]
            if month not in trend_data:
                trend_data[month] = {
                    'month': month,
                    'total_properties': 0,
                    'total_value': 0,
                    'avg_price': 0
                }
            
            trend_data[month]['total_properties'] += row[1]
            trend_data[month]['total_value'] += (row[2] if row[2] else 0) * row[1]
        
        # Calculate averages
        for month in trend_data:
            data = trend_data[month]
            if data['total_properties'] > 0:
                data['avg_price'] = data['total_value'] / data['total_properties']
        
        sorted_data = sorted(trend_data.values(), key=lambda x: x['month'])
        
        return jsonify({
            'success': True,
            'data': sorted_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/visualization/model-performance')
def get_model_performance():
    """Get model performance metrics"""
    try:
        # This would typically come from model evaluation results
        # For now, return static data based on typical ML model performance
        performance_data = {
            'random_forest': {
                'accuracy': 94.2,
                'precision': 93.8,
                'recall': 94.5,
                'f1_score': 94.1,
                'mse': 0.058,
                'r2_score': 0.942
            },
            'xgboost': {
                'accuracy': 92.8,
                'precision': 92.3,
                'recall': 93.1,
                'f1_score': 92.7,
                'mse': 0.072,
                'r2_score': 0.928
            },
            'catboost': {
                'accuracy': 93.5,
                'precision': 93.2,
                'recall': 93.8,
                'f1_score': 93.5,
                'mse': 0.065,
                'r2_score': 0.935
            }
        }
        
        return jsonify({
            'success': True,
            'data': performance_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main.route('/api/visualization/data-info')
def get_data_info():
    """Get information about data freshness and last updates"""
    try:
        cur = mysql.connection.cursor()
        
        # Get last update times
        cur.execute("SELECT MAX(created_at) FROM prediksi_properti_tanah")
        last_tanah_update = cur.fetchone()[0]
        
        cur.execute("SELECT MAX(created_at) FROM prediksi_properti_bangunan_tanah")
        last_bangunan_update = cur.fetchone()[0]
        
        cur.close()
        
        # Get counts
        stats_tanah = PrediksiPropertiTanah.get_statistics()
        stats_bangunan = PrediksiPropertiBangunanTanah.get_statistics()
        
        return jsonify({
            'success': True,
            'data': {
                'last_tanah_update': last_tanah_update.isoformat() if last_tanah_update else None,
                'last_bangunan_update': last_bangunan_update.isoformat() if last_bangunan_update else None,
                'total_tanah': stats_tanah[0] if stats_tanah else 0,
                'total_bangunan': stats_bangunan[0] if stats_bangunan else 0,
                'data_freshness': 'real-time'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Optimized API for filtered data
@main.route('/api/visualization/filtered-data', methods=['POST'])
def get_filtered_data():
    """Get filtered data for visualization with optimized performance"""
    try:
        filters = request.get_json() or {}
        
        # Start with base queries
        tanah_query = """
            SELECT kecamatan, COUNT(*) as count, AVG(harga_prediksi_tanah) as avg_price,
                   SUM(harga_prediksi_tanah) as total_value, 'tanah' as type
            FROM prediksi_properti_tanah
            WHERE 1=1
        """
        
        bangunan_query = """
            SELECT kecamatan, COUNT(*) as count, AVG(harga_prediksi_total) as avg_price,
                   SUM(harga_prediksi_total) as total_value, 'bangunan' as type
            FROM prediksi_properti_bangunan_tanah
            WHERE 1=1
        """
        
        # Add filters
        filter_conditions = []
        filter_values = []
        
        if filters.get('filterKecamatan'):
            filter_conditions.append("kecamatan = %s")
            filter_values.append(filters['filterKecamatan'])
        
        if filters.get('filterPriceRange'):
            price_range = filters['filterPriceRange']
            if '-' in price_range:
                min_price, max_price = price_range.split('-')
                if min_price:
                    filter_conditions.append("harga_prediksi_tanah >= %s")
                    filter_values.append(float(min_price))
                if max_price:
                    filter_conditions.append("harga_prediksi_tanah <= %s")
                    filter_values.append(float(max_price))
        
        # Apply filters to queries
        if filter_conditions:
            filter_clause = " AND " + " AND ".join(filter_conditions)
            tanah_query += filter_clause
            bangunan_query += filter_clause.replace('harga_prediksi_tanah', 'harga_prediksi_total')
        
        # Add GROUP BY
        tanah_query += " GROUP BY kecamatan"
        bangunan_query += " GROUP BY kecamatan"
        
        cur = mysql.connection.cursor()
        
        # Execute queries
        cur.execute(tanah_query, filter_values)
        tanah_results = cur.fetchall()
        
        cur.execute(bangunan_query, filter_values)
        bangunan_results = cur.fetchall()
        
        cur.close()
        
        # Process results
        location_data = {}
        
        # Process tanah results
        for row in tanah_results:
            kecamatan = row[0]
            if kecamatan not in location_data:
                location_data[kecamatan] = {
                    'kecamatan': kecamatan,
                    'total_properties': 0,
                    'total_value': 0,
                    'avg_price': 0,
                    'tanah_count': 0,
                    'bangunan_count': 0
                }
            
            location_data[kecamatan]['tanah_count'] = row[1]
            location_data[kecamatan]['total_properties'] += row[1]
            location_data[kecamatan]['total_value'] += row[3] if row[3] else 0
        
        # Process bangunan results
        for row in bangunan_results:
            kecamatan = row[0]
            if kecamatan not in location_data:
                location_data[kecamatan] = {
                    'kecamatan': kecamatan,
                    'total_properties': 0,
                    'total_value': 0,
                    'avg_price': 0,
                    'tanah_count': 0,
                    'bangunan_count': 0
                }
            
            location_data[kecamatan]['bangunan_count'] = row[1]
            location_data[kecamatan]['total_properties'] += row[1]
            location_data[kecamatan]['total_value'] += row[3] if row[3] else 0
        
        # Calculate averages
        for kecamatan in location_data:
            data = location_data[kecamatan]
            if data['total_properties'] > 0:
                data['avg_price'] = data['total_value'] / data['total_properties']
        
        # Sort by average price
        sorted_data = sorted(location_data.values(), key=lambda x: x['avg_price'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'location_analysis': sorted_data,
                'total_filtered': len(sorted_data)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/visualization/quick-stats')
def get_quick_stats():
    """Get quick statistics for immediate display"""
    try:
        cur = mysql.connection.cursor()
        
        # Get basic counts quickly
        cur.execute("SELECT COUNT(*) FROM prediksi_properti_tanah")
        tanah_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM prediksi_properti_bangunan_tanah")
        bangunan_count = cur.fetchone()[0]
        
        # Get average prices with simple query
        cur.execute("SELECT AVG(harga_prediksi_tanah) FROM prediksi_properti_tanah")
        avg_tanah = cur.fetchone()[0] or 0
        
        cur.execute("SELECT AVG(harga_prediksi_total) FROM prediksi_properti_bangunan_tanah")
        avg_bangunan = cur.fetchone()[0] or 0
        
        # Get min/max prices
        cur.execute("SELECT MIN(harga_prediksi_tanah), MAX(harga_prediksi_tanah) FROM prediksi_properti_tanah")
        min_tanah, max_tanah = cur.fetchone()
        
        cur.execute("SELECT MIN(harga_prediksi_total), MAX(harga_prediksi_total) FROM prediksi_properti_bangunan_tanah")
        min_bangunan, max_bangunan = cur.fetchone()
        
        cur.close()
        
        # Calculate combined stats
        total_properties = tanah_count + bangunan_count
        combined_avg = ((avg_tanah * tanah_count) + (avg_bangunan * bangunan_count)) / total_properties if total_properties > 0 else 0
        
        min_price = min(min_tanah or 0, min_bangunan or 0)
        max_price = max(max_tanah or 0, max_bangunan or 0)
        
        return jsonify({
            'success': True,
            'data': {
                'total_assets': total_properties,
                'avg_price': combined_avg,
                'min_price': min_price,
                'max_price': max_price,
                'total_tanah': tanah_count,
                'total_bangunan': bangunan_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# --- API Endpoints ---

@main.route('/api/locations')
def api_locations():
    return jsonify({'locations': ['Kecamatan A', 'Kecamatan B']})

@main.route('/api/properties')
def api_properties():
    return jsonify({
        'properties': [],
        'total': 0,
        'page': 1,
        'per_page': 12,
        'total_pages': 1
    })

@main.route('/api/property/<int:property_id>')
def api_property_detail(property_id):
    return jsonify({
        'id': property_id,
        'title': 'Contoh Properti',
        'location': 'Kecamatan A',
        'certificate': 'SHM',
        'bedrooms': 3,
        'bathrooms': 2,
        'land_area': 120,
        'building_area': 90,
        'price': 800000000,
        'condition': 'bagus',
        'furnished': 'Semi Furnished',
        'floors': 2,
        'facing': 'Timur',
        'water_source': 'PDAM',
        'internet': 'Ya',
        'hook': 'Ya',
        'power': 2200,
        'road_width': '6 meter',
        'dining_room': 'Ada',
        'living_room': 'Ada'
    })

@main.route('/api/statistics')
def api_statistics():
    stats = data_processor.get_statistics()
    location_prices = data_processor.get_price_by_location()
    return jsonify({
        'locations': [loc for loc in stats.get('locations', [])],
        'location_prices': [p for p in location_prices.values()]
    })

@main.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json()
    land_area = data.get('land_area')
    building_area = data.get('building_area')
    price = (int(land_area) * 5000000) + (int(building_area) * 7000000)
    return jsonify({'predicted_price': price})

# Routes untuk Prediksi Properti
@main.route('/prediksi-tanah')
def prediksi_tanah():
    """Halaman prediksi harga tanah"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    page = request.args.get('page', 1, type=int)
    kecamatan = request.args.get('kecamatan', '')
    per_page = 20
    offset = (page - 1) * per_page
    
    # Ambil data prediksi
    if kecamatan:
        predictions = PrediksiPropertiTanah.search_by_kecamatan(kecamatan, per_page)
    else:
        predictions = PrediksiPropertiTanah.get_all(per_page, offset)
    
    # Ambil statistik
    stats = PrediksiPropertiTanah.get_statistics()
    
    return render_template('prediksi_tanah.html', 
                         predictions=predictions, 
                         stats=stats, 
                         kecamatan=kecamatan,
                         page=page)

@main.route('/prediksi-bangunan-tanah')
def prediksi_bangunan_tanah():
    """Halaman prediksi harga bangunan + tanah"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    page = request.args.get('page', 1, type=int)
    kecamatan = request.args.get('kecamatan', '')
    min_luas = request.args.get('min_luas', type=int)
    max_luas = request.args.get('max_luas', type=int)
    kamar_tidur = request.args.get('kamar_tidur', type=int)
    min_harga = request.args.get('min_harga', type=int)
    max_harga = request.args.get('max_harga', type=int)
    
    per_page = 20
    offset = (page - 1) * per_page
    
    # Ambil data prediksi berdasarkan filter
    if any([kecamatan, min_luas, max_luas, kamar_tidur, min_harga, max_harga]):
        predictions = PrediksiPropertiBangunanTanah.search_by_criteria(
            kecamatan=kecamatan,
            min_luas_bangunan=min_luas,
            max_luas_bangunan=max_luas,
            kamar_tidur=kamar_tidur,
            min_harga=min_harga,
            max_harga=max_harga,
            limit=per_page
        )
    else:
        predictions = PrediksiPropertiBangunanTanah.get_all(per_page, offset)
    
    # Ambil statistik
    stats = PrediksiPropertiBangunanTanah.get_statistics()
    kecamatan_stats = PrediksiPropertiBangunanTanah.get_by_kecamatan_stats()
    
    return render_template('prediksi_bangunan_tanah.html', 
                         predictions=predictions, 
                         stats=stats,
                         kecamatan_stats=kecamatan_stats,
                         filters={
                             'kecamatan': kecamatan,
                             'min_luas': min_luas,
                             'max_luas': max_luas,
                             'kamar_tidur': kamar_tidur,
                             'min_harga': min_harga,
                             'max_harga': max_harga
                         },
                         page=page)

@main.route('/api/prediksi-tanah')
def api_prediksi_tanah():
    """API untuk mendapatkan data prediksi tanah"""
    kecamatan = request.args.get('kecamatan', '')
    limit = request.args.get('limit', 50, type=int)
    
    # Use real prices when available
    predictions = PrediksiPropertiTanah.get_all_with_real_prices(limit, 0)
    
    # Convert to list of dictionaries
    data = []
    for p in predictions:
        data.append({
            'id': p[0],
            'kecamatan': p[1],
            'kelurahan': p[2],
            'luas_tanah_m2': p[3],
            'njop_tanah_per_m2': float(p[4]),
            'zona_nilai_tanah': p[5],
            'kelas_tanah': p[6],
            'jenis_sertifikat': p[7],
            'harga_display': float(p[8]),  # This is either real price or predicted price
            'harga_prediksi_tanah': float(p[9]),
            'harga_per_m2_tanah': float(p[10]),
            'model_predictor': p[11],
            'confidence_score': float(p[12]) if p[12] else None,
            'created_at': p[13].isoformat() if p[13] else None,
            'has_real_price': bool(p[14]) if len(p) > 14 else False
        })
    
    return jsonify({
        'status': 'success',
        'data': data,
        'total': len(data)
    })

@main.route('/api/prediksi-bangunan-tanah')
def api_prediksi_bangunan_tanah():
    """API untuk mendapatkan data prediksi bangunan + tanah"""
    kecamatan = request.args.get('kecamatan', '')
    limit = request.args.get('limit', 50, type=int)
    
    # Use real prices when available
    predictions = PrediksiPropertiBangunanTanah.get_all_with_real_prices(limit, 0)
    
    # Convert to list of dictionaries
    data = []
    for p in predictions:
        data.append({
            'id': p[0],
            'kecamatan': p[1],
            'luas_tanah_m2': p[2],
            'luas_bangunan_m2': p[3],
            'jumlah_kamar_tidur': p[4],
            'jumlah_kamar_mandi': p[5],
            'jumlah_lantai': float(p[6]) if p[6] else None,
            'tahun_dibangun': p[7],
            'daya_listrik': p[8],
            'sertifikat': p[9],
            'kondisi_properti': p[10],
            'tingkat_keamanan': p[11],
            'aksesibilitas': p[12],
            'tipe_iklan': p[13],
            'njop_per_m2': float(p[14]),
            'rasio_bangunan_tanah': float(p[15]),
            'umur_bangunan': p[16],
            'harga_display': float(p[17]),  # This is either real price or predicted price
            'harga_prediksi_total': float(p[18]),
            'harga_prediksi_tanah': float(p[19]),
            'harga_prediksi_bangunan': float(p[20]),
            'harga_per_m2_bangunan': float(p[21]),
            'model_predictor': p[22],
            'confidence_score': float(p[23]) if p[23] else None,
            'created_at': p[24].isoformat() if p[24] else None,
            'has_real_price': bool(p[25]) if len(p) > 25 else False,
            'created_at': p[23].isoformat() if p[23] else None
        })
    
    return jsonify({
        'status': 'success',
        'data': data,
        'total': len(data)
    })

# Route untuk API mendapatkan semua data tanah
@main.route('/api/all-data-tanah')
def api_all_data_tanah():
    """API untuk mendapatkan SEMUA data prediksi tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Ambil SEMUA data tanah
    predictions = PrediksiPropertiTanah.get_all(limit=100000, offset=0)
    
    # Convert to list of dictionaries
    data = []
    for p in predictions:
        data.append({
            'id': p[0],
            'kecamatan': p[1],
            'kelurahan': p[2],
            'luas_tanah_m2': p[3],
            'njop_tanah_per_m2': float(p[4]),
            'zona_nilai_tanah': p[5],
            'kelas_tanah': p[6],
            'jenis_sertifikat': p[7],
            'harga_prediksi_tanah': float(p[8]),
            'harga_per_m2_tanah': float(p[9]),
            'model_predictor': p[10],
            'confidence_score': float(p[11]) if p[11] else None,
            'created_at': p[12].isoformat() if p[12] else None
        })
    
    return jsonify({
        'status': 'success',
        'data': data,
        'total': len(data)
    })

# Route untuk API mendapatkan semua data bangunan
@main.route('/api/all-data-bangunan')
def api_all_data_bangunan():
    """API untuk mendapatkan SEMUA data prediksi bangunan"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Ambil SEMUA data bangunan
    predictions = PrediksiPropertiBangunanTanah.get_all(limit=100000, offset=0)
    
    # Convert to list of dictionaries
    data = []
    for p in predictions:
        data.append({
            'id': p[0],
            'kecamatan': p[1],
            'luas_tanah_m2': p[2],
            'luas_bangunan_m2': p[3],
            'jumlah_kamar_tidur': p[4],
            'jumlah_kamar_mandi': p[5],
            'jumlah_lantai': float(p[6]) if p[6] else None,
            'tahun_dibangun': p[7],
            'daya_listrik': p[8],
            'sertifikat': p[9],
            'kondisi_properti': p[10],
            'tingkat_keamanan': p[11],
            'aksesibilitas': p[12],
            'tipe_iklan': p[13],
            'njop_per_m2': float(p[14]),
            'rasio_bangunan_tanah': float(p[15]),
            'umur_bangunan': p[16],
            'harga_prediksi_total': float(p[17]),
            'harga_prediksi_tanah': float(p[18]),
            'harga_prediksi_bangunan': float(p[19]),
            'harga_per_m2_bangunan': float(p[20]),
            'model_predictor': p[21],
            'confidence_score': float(p[22]) if p[22] else None,
            'created_at': p[23].isoformat() if p[23] else None
        })
    
    return jsonify({
        'status': 'success',
        'data': data,
        'total': len(data)
    })

# Routes untuk CRUD Data Aset
@main.route('/tambah-tanah', methods=['GET', 'POST'])
def tambah_tanah():
    """Halaman tambah data prediksi tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            # Ambil data dari form
            data = {
                'kecamatan': request.form.get('kecamatan'),
                'kelurahan': request.form.get('kelurahan'),
                'luas_tanah_m2': float(request.form.get('luas_tanah_m2', 0)),
                'njop_tanah_per_m2': float(request.form.get('njop_tanah_per_m2', 0)),
                'zona_nilai_tanah': request.form.get('zona_nilai_tanah'),
                'kelas_tanah': request.form.get('kelas_tanah'),
                'jenis_sertifikat': request.form.get('jenis_sertifikat'),
                'model_predictor': request.form.get('model_predictor', 'Manual Input'),
                'confidence_score': float(request.form.get('confidence_score', 0.95))
            }
            
            # Hitung harga prediksi (formula sederhana)
            harga_prediksi_tanah = data['luas_tanah_m2'] * data['njop_tanah_per_m2']
            harga_per_m2_tanah = data['njop_tanah_per_m2']
            
            # Simpan ke database
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO prediksi_properti_tanah 
                (kecamatan, kelurahan, luas_tanah_m2, njop_tanah_per_m2, zona_nilai_tanah, 
                 kelas_tanah, jenis_sertifikat, harga_prediksi_tanah, harga_per_m2_tanah, 
                 model_predictor, confidence_score, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                data['kecamatan'], data['kelurahan'], data['luas_tanah_m2'], 
                data['njop_tanah_per_m2'], data['zona_nilai_tanah'], data['kelas_tanah'],
                data['jenis_sertifikat'], harga_prediksi_tanah, harga_per_m2_tanah,
                data['model_predictor'], data['confidence_score']
            ))
            mysql.connection.commit()
            cur.close()
            
            flash('Data prediksi tanah berhasil ditambahkan!', 'success')
            return redirect(url_for('main.admin_dashboard'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('form_tanah.html')

@main.route('/tambah-bangunan', methods=['GET', 'POST'])
def tambah_bangunan():
    """Halaman tambah data prediksi bangunan"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            # Ambil data dari form
            data = {
                'kecamatan': request.form.get('kecamatan'),
                'kelurahan': request.form.get('kelurahan'),
                'luas_tanah_m2': float(request.form.get('luas_tanah_m2', 0)),
                'luas_bangunan_m2': float(request.form.get('luas_bangunan_m2', 0)),
                'jumlah_kamar_tidur': int(request.form.get('jumlah_kamar_tidur', 0)),
                'jumlah_kamar_mandi': int(request.form.get('jumlah_kamar_mandi', 0)),
                'jumlah_lantai': float(request.form.get('jumlah_lantai', 1)),
                'tahun_dibangun': int(request.form.get('tahun_dibangun', 2020)),
                'daya_listrik': int(request.form.get('daya_listrik', 1300)),
                'sertifikat': request.form.get('sertifikat'),
                'kondisi_properti': request.form.get('kondisi_properti'),
                'tingkat_keamanan': request.form.get('tingkat_keamanan'),
                'aksesibilitas': request.form.get('aksesibilitas'),
                'tipe_iklan': request.form.get('tipe_iklan', 'Sewa'),
                'njop_per_m2': float(request.form.get('njop_per_m2', 0)),
                'model_predictor': request.form.get('model_predictor', 'Manual Input'),
                'confidence_score': float(request.form.get('confidence_score', 0.95))
            }
            
            # Hitung nilai turunan
            current_year = datetime.now().year
            umur_bangunan = current_year - data['tahun_dibangun']
            rasio_bangunan_tanah = data['luas_bangunan_m2'] / data['luas_tanah_m2'] if data['luas_tanah_m2'] > 0 else 0
            
            # Hitung harga prediksi (formula sederhana)
            harga_prediksi_tanah = data['luas_tanah_m2'] * data['njop_per_m2']
            harga_prediksi_bangunan = data['luas_bangunan_m2'] * data['njop_per_m2'] * 1.5  # Building premium
            harga_prediksi_total = harga_prediksi_tanah + harga_prediksi_bangunan
            harga_per_m2_bangunan = harga_prediksi_bangunan / data['luas_bangunan_m2'] if data['luas_bangunan_m2'] > 0 else 0
            
            # Simpan ke database
            cur = mysql.connection.cursor()
            
            # Check if kelurahan column exists, if not add it
            try:
                cur.execute("ALTER TABLE prediksi_properti_bangunan_tanah ADD COLUMN kelurahan VARCHAR(100) AFTER kecamatan")
                mysql.connection.commit()
            except Exception:
                # Column probably already exists, continue
                pass
            
            cur.execute("""
                INSERT INTO prediksi_properti_bangunan_tanah 
                (kecamatan, kelurahan, luas_tanah_m2, luas_bangunan_m2, jumlah_kamar_tidur, jumlah_kamar_mandi, 
                 jumlah_lantai, tahun_dibangun, daya_listrik, sertifikat, kondisi_properti, 
                 tingkat_keamanan, aksesibilitas, tipe_iklan, njop_per_m2, rasio_bangunan_tanah, 
                 umur_bangunan, harga_prediksi_total, harga_prediksi_tanah, harga_prediksi_bangunan, 
                 harga_per_m2_bangunan, model_predictor, confidence_score, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                data['kecamatan'], data['kelurahan'], data['luas_tanah_m2'], data['luas_bangunan_m2'], 
                data['jumlah_kamar_tidur'], data['jumlah_kamar_mandi'], data['jumlah_lantai'],
                data['tahun_dibangun'], data['daya_listrik'], data['sertifikat'],
                data['kondisi_properti'], data['tingkat_keamanan'], data['aksesibilitas'],
                data['tipe_iklan'], data['njop_per_m2'], rasio_bangunan_tanah, umur_bangunan,
                harga_prediksi_total, harga_prediksi_tanah, harga_prediksi_bangunan,
                harga_per_m2_bangunan, data['model_predictor'], data['confidence_score']
            ))
            mysql.connection.commit()
            cur.close()
            
            flash('Data prediksi bangunan berhasil ditambahkan!', 'success')
            return redirect(url_for('main.admin_dashboard'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('form_bangunan.html')

@main.route('/edit-tanah/<int:id>', methods=['GET', 'POST'])
def edit_tanah(id):
    """Edit data prediksi tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            # Ambil data dari form
            data = {
                'kecamatan': request.form.get('kecamatan'),
                'kelurahan': request.form.get('kelurahan'),
                'luas_tanah_m2': float(request.form.get('luas_tanah_m2', 0)),
                'njop_tanah_per_m2': float(request.form.get('njop_tanah_per_m2', 0)),
                'zona_nilai_tanah': request.form.get('zona_nilai_tanah'),
                'kelas_tanah': request.form.get('kelas_tanah'),
                'jenis_sertifikat': request.form.get('jenis_sertifikat'),
                'model_predictor': request.form.get('model_predictor', 'Manual Input'),
                'confidence_score': float(request.form.get('confidence_score', 0.95))
            }
            
            # Hitung harga prediksi (formula sederhana)
            harga_prediksi_tanah = data['luas_tanah_m2'] * data['njop_tanah_per_m2']
            harga_per_m2_tanah = data['njop_tanah_per_m2']
            
            # Update ke database
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE prediksi_properti_tanah 
                SET kecamatan=%s, kelurahan=%s, luas_tanah_m2=%s, njop_tanah_per_m2=%s, 
                    zona_nilai_tanah=%s, kelas_tanah=%s, jenis_sertifikat=%s, 
                    harga_prediksi_tanah=%s, harga_per_m2_tanah=%s, 
                    model_predictor=%s, confidence_score=%s, updated_at=NOW()
                WHERE id=%s
            """, (
                data['kecamatan'], data['kelurahan'], data['luas_tanah_m2'], 
                data['njop_tanah_per_m2'], data['zona_nilai_tanah'], data['kelas_tanah'],
                data['jenis_sertifikat'], harga_prediksi_tanah, harga_per_m2_tanah,
                data['model_predictor'], data['confidence_score'], id
            ))
            mysql.connection.commit()
            cur.close()
            
            flash('Data prediksi tanah berhasil diperbarui!', 'success')
            return redirect(url_for('main.total_properti_prediksi'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    # GET - ambil data untuk form edit
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, kecamatan, kelurahan, luas_tanah_m2, njop_tanah_per_m2, 
                   zona_nilai_tanah, kelas_tanah, jenis_sertifikat, 
                   harga_prediksi_tanah, harga_per_m2_tanah, 
                   model_predictor, confidence_score, created_at, updated_at
            FROM prediksi_properti_tanah WHERE id = %s
        """, (id,))
        result = cur.fetchone()
        cur.close()
        
        if not result:
            flash('Data tidak ditemukan', 'error')
            return redirect(url_for('main.total_properti_prediksi'))
        
        # Convert tuple to dictionary for easier template access
        columns = ['id', 'kecamatan', 'kelurahan', 'luas_tanah_m2', 'njop_tanah_per_m2', 
                  'zona_nilai_tanah', 'kelas_tanah', 'jenis_sertifikat', 
                  'harga_prediksi_tanah', 'harga_per_m2_tanah', 
                  'model_predictor', 'confidence_score', 'created_at', 'updated_at']
        data = dict(zip(columns, result))
            
        return render_template('form_tanah_edit.html', data=data)
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('main.total_properti_prediksi'))

@main.route('/edit-bangunan/<int:id>', methods=['GET', 'POST'])
def edit_bangunan(id):
    """Edit data prediksi bangunan"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            # Ambil data dari form
            data = {
                'kecamatan': request.form.get('kecamatan'),
                'kelurahan': request.form.get('kelurahan'),
                'luas_tanah_m2': float(request.form.get('luas_tanah_m2', 0)),
                'luas_bangunan_m2': float(request.form.get('luas_bangunan_m2', 0)),
                'jumlah_kamar_tidur': int(request.form.get('jumlah_kamar_tidur', 0)),
                'jumlah_kamar_mandi': int(request.form.get('jumlah_kamar_mandi', 0)),
                'jumlah_lantai': float(request.form.get('jumlah_lantai', 1)),
                'tahun_dibangun': int(request.form.get('tahun_dibangun', 2020)),
                'daya_listrik': int(request.form.get('daya_listrik', 1300)),
                'sertifikat': request.form.get('sertifikat'),
                'kondisi_properti': request.form.get('kondisi_properti'),
                'tingkat_keamanan': request.form.get('tingkat_keamanan'),
                'aksesibilitas': request.form.get('aksesibilitas'),
                'tipe_iklan': request.form.get('tipe_iklan', 'Sewa'),
                'njop_per_m2': float(request.form.get('njop_per_m2', 0)),
                'model_predictor': request.form.get('model_predictor', 'Manual Input'),
                'confidence_score': float(request.form.get('confidence_score', 0.95))
            }
            
            # Hitung nilai turunan
            current_year = datetime.now().year
            umur_bangunan = current_year - data['tahun_dibangun']
            rasio_bangunan_tanah = data['luas_bangunan_m2'] / data['luas_tanah_m2'] if data['luas_tanah_m2'] > 0 else 0
            
            # Hitung harga prediksi (formula sederhana)
            harga_prediksi_tanah = data['luas_tanah_m2'] * data['njop_per_m2']
            harga_prediksi_bangunan = data['luas_bangunan_m2'] * data['njop_per_m2'] * 1.5  # Building premium
            harga_prediksi_total = harga_prediksi_tanah + harga_prediksi_bangunan
            harga_per_m2_bangunan = harga_prediksi_bangunan / data['luas_bangunan_m2'] if data['luas_bangunan_m2'] > 0 else 0
            
            # Update ke database
            cur = mysql.connection.cursor()
            
            # Check if kelurahan column exists, if not add it
            try:
                cur.execute("ALTER TABLE prediksi_properti_bangunan_tanah ADD COLUMN kelurahan VARCHAR(100) AFTER kecamatan")
                mysql.connection.commit()
            except Exception:
                # Column probably already exists, continue
                pass
            
            cur.execute("""
                UPDATE prediksi_properti_bangunan_tanah 
                SET kecamatan=%s, kelurahan=%s, luas_tanah_m2=%s, luas_bangunan_m2=%s, 
                    jumlah_kamar_tidur=%s, jumlah_kamar_mandi=%s, jumlah_lantai=%s, 
                    tahun_dibangun=%s, daya_listrik=%s, sertifikat=%s, kondisi_properti=%s, 
                    tingkat_keamanan=%s, aksesibilitas=%s, tipe_iklan=%s, njop_per_m2=%s, 
                    rasio_bangunan_tanah=%s, umur_bangunan=%s, harga_prediksi_total=%s, 
                    harga_prediksi_tanah=%s, harga_prediksi_bangunan=%s, harga_per_m2_bangunan=%s, 
                    model_predictor=%s, confidence_score=%s, updated_at=NOW()
                WHERE id=%s
            """, (
                data['kecamatan'], data['kelurahan'], data['luas_tanah_m2'], data['luas_bangunan_m2'], 
                data['jumlah_kamar_tidur'], data['jumlah_kamar_mandi'], data['jumlah_lantai'],
                data['tahun_dibangun'], data['daya_listrik'], data['sertifikat'],
                data['kondisi_properti'], data['tingkat_keamanan'], data['aksesibilitas'],
                data['tipe_iklan'], data['njop_per_m2'], rasio_bangunan_tanah, umur_bangunan,
                harga_prediksi_total, harga_prediksi_tanah, harga_prediksi_bangunan,
                harga_per_m2_bangunan, data['model_predictor'], data['confidence_score'], id
            ))
            mysql.connection.commit()
            cur.close()
            
            flash('Data prediksi bangunan berhasil diperbarui!', 'success')
            return redirect(url_for('main.total_properti_prediksi'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    # GET - ambil data untuk form edit
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, kecamatan, kelurahan, luas_tanah_m2, luas_bangunan_m2, 
                   jumlah_kamar_tidur, jumlah_kamar_mandi, jumlah_lantai, 
                   tahun_dibangun, daya_listrik, sertifikat, kondisi_properti, 
                   tingkat_keamanan, aksesibilitas, tipe_iklan, njop_per_m2, 
                   rasio_bangunan_tanah, umur_bangunan, harga_prediksi_total, 
                   harga_prediksi_tanah, harga_prediksi_bangunan, harga_per_m2_bangunan, 
                   model_predictor, confidence_score, created_at, updated_at
            FROM prediksi_properti_bangunan_tanah WHERE id = %s
        """, (id,))
        result = cur.fetchone()
        cur.close()
        
        if not result:
            flash('Data tidak ditemukan', 'error')
            return redirect(url_for('main.total_properti_prediksi'))
        
        # Convert tuple to dictionary for easier template access
        columns = ['id', 'kecamatan', 'kelurahan', 'luas_tanah_m2', 'luas_bangunan_m2', 
                  'jumlah_kamar_tidur', 'jumlah_kamar_mandi', 'jumlah_lantai', 
                  'tahun_dibangun', 'daya_listrik', 'sertifikat', 'kondisi_properti', 
                  'tingkat_keamanan', 'aksesibilitas', 'tipe_iklan', 'njop_per_m2', 
                  'rasio_bangunan_tanah', 'umur_bangunan', 'harga_prediksi_total', 
                  'harga_prediksi_tanah', 'harga_prediksi_bangunan', 'harga_per_m2_bangunan', 
                  'model_predictor', 'confidence_score', 'created_at', 'updated_at']
        data = dict(zip(columns, result))
            
        return render_template('form_bangunan_edit.html', data=data)
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('main.total_properti_prediksi'))

@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    """Route untuk edit profil user"""
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            cur = mysql.connection.cursor()
            
            # Check if this is a password change request
            if 'current_password' in request.form and request.form.get('current_password'):
                # Handle password change
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
                # Verify current password
                cur.execute("SELECT password FROM users WHERE id = %s", (user_id,))
                user_data = cur.fetchone()
                
                if not user_data or not check_password_hash(user_data[0], current_password):
                    flash('Password saat ini tidak benar.', 'error')
                    cur.close()
                    return redirect(url_for('main.edit_profile'))
                
                # Validate new password
                if new_password != confirm_password:
                    flash('Konfirmasi password tidak cocok.', 'error')
                    cur.close()
                    return redirect(url_for('main.edit_profile'))
                
                if len(new_password) < 8:
                    flash('Password baru harus minimal 8 karakter.', 'error')
                    cur.close()
                    return redirect(url_for('main.edit_profile'))
                
                # Update password
                hashed_password = generate_password_hash(new_password)
                cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
                mysql.connection.commit()
                flash('Password berhasil diubah!', 'success')
                
            else:
                # Handle profile update
                user_name = request.form.get('user_name')
                email = request.form.get('email')
                phone = request.form.get('phone')
                address = request.form.get('address')
                
                # Check if email already exists for other users
                cur.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id))
                if cur.fetchone():
                    flash('Email sudah digunakan oleh user lain.', 'error')
                    cur.close()
                    return redirect(url_for('main.edit_profile'))
                
                # Update user profile
                cur.execute("""
                    UPDATE users 
                    SET name = %s, email = %s, phone = %s, address = %s 
                    WHERE id = %s
                """, (user_name, email, phone, address, user_id))
                mysql.connection.commit()
                
                # Update session data
                session['user_name'] = user_name
                session['user_email'] = email
                session['user_phone'] = phone if phone else ''
                session['user_address'] = address if address else ''
                
                flash('Profil berhasil diperbarui!', 'success')
            
            cur.close()
            return redirect(url_for('main.edit_profile'))
            
        except Exception as e:
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return redirect(url_for('main.edit_profile'))
    
    # GET request - load user data and show edit profile form
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT name, email, phone, address, updated_at FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            # Update session with current data
            session['user_name'] = user_data[0]
            session['user_email'] = user_data[1]
            session['user_phone'] = user_data[2] if user_data[2] else ''
            session['user_address'] = user_data[3] if user_data[3] else ''
            session['join_date'] = user_data[4].strftime('%d %B %Y') if user_data[4] else 'N/A'
            
    except Exception as e:
        flash(f'Terjadi kesalahan dalam memuat data: {str(e)}', 'error')
    
    return render_template('edit_profile.html')


@main.route('/api/delete-tanah/<int:id>', methods=['DELETE'])
def delete_tanah(id):
    """API untuk menghapus data tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Akses ditolak'}), 403
    
    try:
        cur = mysql.connection.cursor()
        
        # Check if tanah exists
        cur.execute("SELECT id FROM prediksi_properti_tanah WHERE id = %s", (id,))
        tanah = cur.fetchone()
        
        if not tanah:
            cur.close()
            return jsonify({'success': False, 'error': 'Data tanah tidak ditemukan'}), 404
        
        # Delete the tanah record
        cur.execute("DELETE FROM prediksi_properti_tanah WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'success': True,
            'message': f'Data tanah ID {id} berhasil dihapus'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@main.route('/api/delete-bangunan/<int:id>', methods=['DELETE'])
def delete_bangunan(id):
    """API untuk menghapus data bangunan"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'error': 'Akses ditolak'}), 403
    
    try:
        cur = mysql.connection.cursor()
        
        # Check if bangunan exists
        cur.execute("SELECT id FROM prediksi_properti_bangunan_tanah WHERE id = %s", (id,))
        bangunan = cur.fetchone()
        
        if not bangunan:
            cur.close()
            return jsonify({'success': False, 'error': 'Data bangunan tidak ditemukan'}), 404
        
        # Delete the bangunan record
        cur.execute("DELETE FROM prediksi_properti_bangunan_tanah WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'success': True,
            'message': f'Data bangunan ID {id} berhasil dihapus'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/total-properti-prediksi')
def total_properti_prediksi():
    """Halaman untuk melihat semua data properti prediksi"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        cur = mysql.connection.cursor()
        
        # Get statistics directly from database
        cur.execute("SELECT COUNT(*), COALESCE(AVG(harga_prediksi_tanah), 0) FROM prediksi_properti_tanah")
        stats_tanah = cur.fetchone()
        
        cur.execute("SELECT COUNT(*), COALESCE(AVG(harga_prediksi_total), 0) FROM prediksi_properti_bangunan_tanah")
        stats_bangunan = cur.fetchone()
        
        # Calculate totals with safe defaults
        total_tanah = stats_tanah[0] if stats_tanah and stats_tanah[0] else 0
        total_bangunan = stats_bangunan[0] if stats_bangunan and stats_bangunan[0] else 0
        
        avg_price_tanah = stats_tanah[1] if stats_tanah and stats_tanah[1] else 0
        avg_price_bangunan = stats_bangunan[1] if stats_bangunan and stats_bangunan[1] else 0
        
        total_nilai = (avg_price_tanah * total_tanah) + (avg_price_bangunan * total_bangunan)




        # Get unique kecamatan list from both tables
        cur.execute("""
            SELECT DISTINCT kecamatan FROM prediksi_properti_tanah 
            WHERE kecamatan IS NOT NULL AND kecamatan != ''
            UNION
            SELECT DISTINCT kecamatan FROM prediksi_properti_bangunan_tanah 
            WHERE kecamatan IS NOT NULL AND kecamatan != ''
            ORDER BY kecamatan
        """)
        kecamatan_result = cur.fetchall()
        kecamatan_list = [row[0] for row in kecamatan_result]
        
        cur.close()
        
        return render_template('total_properti_prediksi.html',
                             stats_tanah=stats_tanah,
                             stats_bangunan=stats_bangunan,
                             total_tanah=total_tanah,
                             total_bangunan=total_bangunan,
                             total_nilai=total_nilai,
                             kecamatan_list=kecamatan_list)
                             
    except Exception as e:
        flash(f'Error loading data: {str(e)}', 'error')
        return render_template('total_properti_prediksi.html',
                             stats_tanah=(0, 0),
                             stats_bangunan=(0, 0),
                             total_tanah=0,
                             total_bangunan=0,
                             total_nilai=0,
                             kecamatan_list=[])

@main.route('/manajemen-aset')
def manajemen_aset():
    """Halaman manajemen aset lengkap"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        cur = mysql.connection.cursor()
        
        # Get basic statistics
        cur.execute("SELECT COUNT(*), COALESCE(AVG(harga_prediksi_tanah), 0) FROM prediksi_properti_tanah")
        stats_tanah = cur.fetchone()
        
        cur.execute("SELECT COUNT(*), COALESCE(AVG(harga_prediksi_total), 0) FROM prediksi_properti_bangunan_tanah")
        stats_bangunan = cur.fetchone()
        
        cur.close()
        
        return render_template('manajemen_aset.html',
                             stats_tanah=stats_tanah,
                             stats_bangunan=stats_bangunan)
                             
    except Exception as e:
        flash(f'Error loading data: {str(e)}', 'error')
        return render_template('manajemen_aset.html',
                             stats_tanah=(0, 0),
                             stats_bangunan=(0, 0))

@main.route('/manajemen-prediksi-harga-aset')
def manajemen_prediksi_harga_aset():
    """Halaman manajemen prediksi harga aset dengan CRUD"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        cur = mysql.connection.cursor()
        
        # Get statistics
        cur.execute("SELECT COUNT(*) FROM prediksi_properti_tanah")
        total_tanah = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM prediksi_properti_bangunan_tanah")
        total_bangunan = cur.fetchone()[0]
        
        # Get assets sent to users
        cur.execute("""
            SELECT COUNT(*) FROM prediksi_properti_bangunan_tanah 
            WHERE status_kirim_user = 'sent'
        """)
        total_sent = cur.fetchone()[0]
        
        cur.close()
        
        return render_template('manajemen_prediksi_harga_aset.html',
                             total_tanah=total_tanah,
                             total_bangunan=total_bangunan,
                             total_sent=total_sent)
                             
    except Exception as e:
        print(f"Error in manajemen_prediksi_harga_aset: {e}")
        flash(f'Error loading data: {str(e)}', 'error')
        return render_template('manajemen_prediksi_harga_aset.html',
                             total_tanah=0,
                             total_bangunan=0,
                             total_sent=0)

@main.route('/api/predict-price', methods=['POST'])
def predict_price():
    """API untuk prediksi harga properti"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['Kecamatan', 'Kamar Tidur', 'Kamar Mandi', 'Luas Tanah', 
                          'Luas Bangunan', 'Sertifikat', 'Daya Listrik', 'Jumlah Lantai',
                          'Hadap', 'Hook', 'Kondisi Properti', 'Tipe Iklan', 
                          'Aksesibilitas', 'Tingkat_Keamanan', 'NJOP_Rp_per_m2']
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Initialize predictor
        predictor = PropertyPricePredictor()
        
        # Get model type from request
        model_type = data.get('model_type', 'random_forest')
        
        # Make prediction
        result = predictor.predict_price(data, model_type)
        
        if result['prediction'] is None:
            return jsonify({
                'error': result.get('error', 'Prediction failed')
            }), 500
        
        return jsonify({
            'status': 'success',
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'model_used': result['model_used']
        })
        
    except Exception as e:
        print(f"Error in predict_price: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/predict-all-models', methods=['POST'])
def predict_all_models():
    """API untuk prediksi harga dengan semua model"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        
        # Initialize predictor
        predictor = PropertyPricePredictor()
        
        # Get predictions from all models
        results = predictor.predict_all_models(data)
        
        return jsonify({
            'status': 'success',
            'predictions': results
        })
        
    except Exception as e:
        print(f"Error in predict_all_models: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/save-prediction', methods=['POST'])
def save_prediction():
    """API untuk menyimpan prediksi ke database"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        
        cur = mysql.connection.cursor()
        
        # Insert prediction into database
        cur.execute("""
            INSERT INTO prediksi_properti_bangunan_tanah (
                kecamatan, kelurahan, luas_tanah_m2, luas_bangunan_m2,
                jumlah_kamar_tidur, jumlah_kamar_mandi, jumlah_lantai,
                tahun_dibangun, daya_listrik, sertifikat, kondisi_properti,
                tingkat_keamanan, aksesibilitas, tipe_iklan, njop_per_m2,
                harga_prediksi_total, harga_prediksi_tanah, harga_prediksi_bangunan,
                harga_per_m2_bangunan, model_predictor, confidence_score,
                status_kirim_user, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, NOW()
            )
        """, (
            data['kecamatan'], data.get('kelurahan', ''),
            data['luas_tanah'], data['luas_bangunan'],
            data['kamar_tidur'], data['kamar_mandi'], data['jumlah_lantai'],
            data.get('tahun_dibangun', 2020), data['daya_listrik'],
            data['sertifikat'], data['kondisi_properti'],
            data['tingkat_keamanan'], data['aksesibilitas'], data['tipe_iklan'],
            data['njop_per_m2'], data['harga_prediksi_total'],
            data.get('harga_prediksi_tanah', 0), data.get('harga_prediksi_bangunan', 0),
            data.get('harga_per_m2_bangunan', 0), data['model_predictor'],
            data['confidence_score'], 'sent'
        ))
        
        prediction_id = cur.lastrowid
        
        # Create rental asset from prediction
        alamat = f"{data['kecamatan']}, {data.get('kelurahan', '')}"
        jenis_aset = 'tanah_bangunan' if data.get('luas_bangunan', 0) > 0 else 'tanah'
        
        # Calculate rental price (monthly) - use predicted price / 12 as base
        harga_sewa = float(data['harga_prediksi_total']) / 12
        
        cur.execute("""
            INSERT INTO aset_sewa (
                jenis, alamat, kecamatan, kelurahan, luas_tanah,
                luas_bangunan, kamar_tidur, kamar_mandi, jumlah_lantai,
                harga_prediksi, harga_sewa, status, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
        """, (
            jenis_aset, alamat, data['kecamatan'], data.get('kelurahan', ''),
            data['luas_tanah'], data.get('luas_bangunan', 0),
            data.get('kamar_tidur', 0), data.get('kamar_mandi', 0),
            data.get('jumlah_lantai', 0), data['harga_prediksi_total'],
            harga_sewa, 'tersedia'
        ))
        
        asset_id = cur.lastrowid
        
        # Create notification for all users about new asset
        cur.execute("SELECT id FROM users WHERE role = 'pengguna'")
        users = cur.fetchall()
        
        for user in users:
            cur.execute("""
                INSERT INTO notifikasi_user (user_id, jenis, judul, pesan, is_read, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                user[0], 'sistem', 'Aset Baru Tersedia',
                f'Aset baru tersedia untuk disewa di {data["kecamatan"]} dengan luas tanah {data["luas_tanah"]} m²',
                False
            ))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Prediction saved and asset created successfully',
            'prediction_id': prediction_id,
            'asset_id': asset_id
        })
        
    except Exception as e:
        print(f"Error in save_prediction: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/send-to-user/<int:prediction_id>', methods=['POST'])
def send_to_user(prediction_id):
    """API untuk mengirim aset ke user dashboard"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        cur = mysql.connection.cursor()
        
        # Update status to 'sent'
        cur.execute("""
            UPDATE prediksi_properti_bangunan_tanah 
            SET status_kirim_user = 'sent', updated_at = NOW()
            WHERE id = %s
        """, (prediction_id,))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Asset sent to user dashboard successfully'
        })
        
    except Exception as e:
        print(f"Error in send_to_user: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/prediksi-list')
def get_prediksi_list():
    """API untuk mendapatkan daftar prediksi"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        cur = mysql.connection.cursor()
        
        # Get parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        
        # Get filters
        kecamatan = request.args.get('kecamatan', '')
        status = request.args.get('status', '')
        
        # Build query
        where_conditions = []
        params = []
        
        if kecamatan:
            where_conditions.append("kecamatan = %s")
            params.append(kecamatan)
        
        if status:
            where_conditions.append("status_kirim_user = %s")
            params.append(status)
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get total count
        cur.execute(f"SELECT COUNT(*) FROM prediksi_properti_bangunan_tanah{where_clause}", params)
        total_items = cur.fetchone()[0]
        
        # Get paginated data (exclude NJOP_Rp_per_m2 from display)
        cur.execute(f"""
            SELECT id, kecamatan, kelurahan, luas_tanah_m2, luas_bangunan_m2,
                   jumlah_kamar_tidur, jumlah_kamar_mandi, jumlah_lantai,
                   tahun_dibangun, daya_listrik, sertifikat, kondisi_properti,
                   tingkat_keamanan, aksesibilitas, tipe_iklan,
                   harga_prediksi_total, harga_prediksi_tanah, harga_prediksi_bangunan,
                   harga_per_m2_bangunan, model_predictor, confidence_score,
                   status_kirim_user, created_at
            FROM prediksi_properti_bangunan_tanah{where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        rows = cur.fetchall()
        cur.close()
        
        # Format data
        predictions = []
        for row in rows:
            predictions.append({
                'id': row[0],
                'kecamatan': row[1],
                'kelurahan': row[2],
                'luas_tanah_m2': row[3],
                'luas_bangunan_m2': row[4],
                'jumlah_kamar_tidur': row[5],
                'jumlah_kamar_mandi': row[6],
                'jumlah_lantai': row[7],
                'tahun_dibangun': row[8],
                'daya_listrik': row[9],
                'sertifikat': row[10],
                'kondisi_properti': row[11],
                'tingkat_keamanan': row[12],
                'aksesibilitas': row[13],
                'tipe_iklan': row[14],
                'harga_prediksi_total': row[15],
                'harga_prediksi_tanah': row[16],
                'harga_prediksi_bangunan': row[17],
                'harga_per_m2_bangunan': row[18],
                'model_predictor': row[19],
                'confidence_score': row[20],
                'status_kirim_user': row[21],
                'created_at': row[22].strftime('%Y-%m-%d %H:%M:%S') if row[22] else None
            })
        
        return jsonify({
            'status': 'success',
            'data': predictions,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': (total_items + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        print(f"Error in get_prediksi_list: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/aset-tersedia')
def get_aset_tersedia():
    """API untuk mendapatkan daftar aset yang tersedia untuk disewa"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 6, type=int)
        jenis = request.args.get('jenis', '')
        kecamatan = request.args.get('kecamatan', '')
        
        cur = mysql.connection.cursor()
        
        # Base query
        where_conditions = ["status = 'tersedia'"]
        params = []
        
        if jenis:
            where_conditions.append("jenis = %s")
            params.append(jenis)
        
        if kecamatan:
            where_conditions.append("kecamatan = %s")
            params.append(kecamatan)
        
        where_clause = " AND ".join(where_conditions)
        
        # Count total records
        count_query = f"SELECT COUNT(*) FROM aset_sewa WHERE {where_clause}"
        cur.execute(count_query, params)
        total_records = cur.fetchone()[0]
        
        # Calculate pagination
        offset = (page - 1) * per_page
        total_pages = (total_records + per_page - 1) // per_page
        
        # Get paginated data
        data_query = f"""
            SELECT id, jenis, alamat, kecamatan, kelurahan, luas_tanah,
                   luas_bangunan, kamar_tidur, kamar_mandi, jumlah_lantai,
                   harga_prediksi, harga_sewa, status, created_at
            FROM aset_sewa 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        
        cur.execute(data_query, params)
        aset_data = cur.fetchall()
        cur.close()
        
        # Format data
        aset_list = []
        for aset in aset_data:
            aset_list.append({
                'id': aset[0],
                'jenis': aset[1],
                'alamat': aset[2],
                'kecamatan': aset[3],
                'kelurahan': aset[4],
                'luas_tanah': float(aset[5]) if aset[5] else 0,
                'luas_bangunan': float(aset[6]) if aset[6] else 0,
                'kamar_tidur': aset[7],
                'kamar_mandi': aset[8],
                'jumlah_lantai': aset[9],
                'harga_prediksi': float(aset[10]) if aset[10] else 0,
                'harga_sewa': float(aset[11]) if aset[11] else 0,
                'status': aset[12],
                'created_at': aset[13].strftime('%Y-%m-%d %H:%M:%S') if aset[13] else None
            })
        
        return jsonify({
            'success': True,
            'data': aset_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'total_records': total_records,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
        
    except Exception as e:
        print(f"Error in get_aset_tersedia: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/api/kecamatan-list')
def get_kecamatan_list():
    """API untuk mendapatkan daftar kecamatan yang tersedia"""
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT DISTINCT kecamatan FROM aset_sewa WHERE kecamatan IS NOT NULL ORDER BY kecamatan")
        kecamatan_data = cur.fetchall()
        cur.close()
        
        kecamatan_list = [row[0] for row in kecamatan_data]
        
        return jsonify({
            'success': True,
            'data': kecamatan_list
        })
        
    except Exception as e:
        print(f"Error in get_kecamatan_list: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== TANAH API ROUTES ====================

@main.route('/api/predict-tanah-price', methods=['POST'])
def predict_tanah_price():
    """API untuk prediksi harga tanah menggunakan ensemble (gabungan semua model)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Initialize predictor
        predictor = PropertyPricePredictor()
        
        # Use ensemble prediction by default
        result = predictor.predict_tanah_ensemble(data)
        
        if result.get('error'):
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'status': 'success',
            'prediction': result['prediction'],
            'price_per_m2': result['price_per_m2'],
            'model_used': result['model_used'],
            'confidence': result['confidence']
        })
        
    except Exception as e:
        print(f"Error in predict_tanah_price: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/predict-tanah-all-models', methods=['POST'])
def predict_tanah_all_models():
    """API untuk prediksi harga tanah menggunakan semua model"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Initialize predictor
        predictor = PropertyPricePredictor()
        
        # Get predictions from all models
        predictions = {}
        models = ['random_forest', 'xgboost', 'catboost']
        
        for model in models:
            try:
                result = predictor.predict_tanah_price(data, model)
                predictions[model] = result
            except Exception as e:
                print(f"Error with model {model}: {e}")
                predictions[model] = {'error': str(e)}
        
        return jsonify({
            'status': 'success',
            'predictions': predictions
        })
        
    except Exception as e:
        print(f"Error in predict_tanah_all_models: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/save-tanah-prediction', methods=['POST'])
def save_tanah_prediction():
    """API untuk menyimpan prediksi tanah ke database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        cur = mysql.connection.cursor()
        
        # Check if the table exists, if not create it
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prediksi_properti_tanah (
                id INT AUTO_INCREMENT PRIMARY KEY,
                kecamatan VARCHAR(100),
                kelurahan VARCHAR(100),
                luas_tanah_m2 INT,
                njop_tanah_per_m2 DECIMAL(15,2),
                zona_nilai_tanah VARCHAR(50),
                kelas_tanah VARCHAR(10),
                jenis_sertifikat VARCHAR(50),
                harga_prediksi_tanah DECIMAL(15,2),
                harga_per_m2_tanah DECIMAL(15,2),
                model_predictor VARCHAR(50),
                confidence_score DECIMAL(5,2),
                status_kirim_user ENUM('pending', 'sent') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Insert the prediction
        cur.execute("""
            INSERT INTO prediksi_properti_tanah (
                kecamatan, kelurahan, luas_tanah_m2, njop_tanah_per_m2, 
                zona_nilai_tanah, kelas_tanah, jenis_sertifikat, 
                harga_prediksi_tanah, harga_per_m2_tanah, model_predictor, 
                confidence_score
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('Kecamatan', ''),
            data.get('Kelurahan', ''),
            data.get('Luas Tanah', 0),
            data.get('NJOP_Tanah_per_m2', 0),
            data.get('Zona_Nilai_Tanah', ''),
            data.get('Kelas_Tanah', ''),
            data.get('Jenis_Sertifikat', ''),
            data.get('prediction', 0),
            data.get('price_per_m2', 0),
            data.get('model_used', ''),
            data.get('confidence', 0)
        ))
        
        mysql.connection.commit()
        asset_id = cur.lastrowid
        cur.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Prediksi tanah berhasil disimpan',
            'asset_id': asset_id
        })
        
    except Exception as e:
        print(f"Error in save_tanah_prediction: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/tanah-list')
def get_tanah_list():
    """API untuk mendapatkan daftar prediksi tanah"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        
        cur = mysql.connection.cursor()
        
        # Get total count
        cur.execute("SELECT COUNT(*) FROM prediksi_properti_tanah")
        total_count = cur.fetchone()[0]
        
        # Get paginated data
        cur.execute("""
            SELECT id, kecamatan, kelurahan, luas_tanah_m2, njop_tanah_per_m2, 
                   zona_nilai_tanah, kelas_tanah, jenis_sertifikat, 
                   harga_prediksi_tanah, harga_per_m2_tanah, model_predictor, 
                   confidence_score, status_kirim_user, created_at
            FROM prediksi_properti_tanah 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        rows = cur.fetchall()
        cur.close()
        
        # Convert to list of dictionaries
        assets = []
        for row in rows:
            assets.append({
                'id': row[0],
                'kecamatan': row[1],
                'kelurahan': row[2],
                'luas_tanah_m2': row[3],
                'njop_tanah_per_m2': row[4],
                'zona_nilai_tanah': row[5],
                'kelas_tanah': row[6],
                'jenis_sertifikat': row[7],
                'harga_prediksi_tanah': row[8],
                'harga_per_m2_tanah': row[9],
                'model_predictor': row[10],
                'confidence_score': row[11],
                'status_kirim_user': row[12],
                'created_at': row[13].strftime('%Y-%m-%d %H:%M:%S') if row[13] else None
            })
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        
        return jsonify({
            'status': 'success',
            'data': assets,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'per_page': per_page,
                'total_count': total_count
            }
        })
        
    except Exception as e:
        print(f"Error in get_tanah_list: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/tanah-search')
def search_tanah():
    """API untuk mencari prediksi tanah berdasarkan kecamatan"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        cur = mysql.connection.cursor()
        
        cur.execute("""
            SELECT id, kecamatan, kelurahan, luas_tanah_m2, njop_tanah_per_m2, 
                   zona_nilai_tanah, kelas_tanah, jenis_sertifikat, 
                   harga_prediksi_tanah, harga_per_m2_tanah, model_predictor, 
                   confidence_score, status_kirim_user, created_at
            FROM prediksi_properti_tanah 
            WHERE kecamatan LIKE %s OR kelurahan LIKE %s
            ORDER BY harga_prediksi_tanah DESC 
            LIMIT 50
        """, (f'%{query}%', f'%{query}%'))
        
        rows = cur.fetchall()
        cur.close()
        
        # Convert to list of dictionaries
        assets = []
        for row in rows:
            assets.append({
                'id': row[0],
                'kecamatan': row[1],
                'kelurahan': row[2],
                'luas_tanah_m2': row[3],
                'njop_tanah_per_m2': row[4],
                'zona_nilai_tanah': row[5],
                'kelas_tanah': row[6],
                'jenis_sertifikat': row[7],
                'harga_prediksi_tanah': row[8],
                'harga_per_m2_tanah': row[9],
                'model_predictor': row[10],
                'confidence_score': row[11],
                'status_kirim_user': row[12],
                'created_at': row[13].strftime('%Y-%m-%d %H:%M:%S') if row[13] else None
            })
        
        return jsonify({
            'status': 'success',
            'data': assets
        })
        
    except Exception as e:
        print(f"Error in search_tanah: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/tanah-delete/<int:asset_id>', methods=['DELETE'])
def delete_tanah_asset(asset_id):
    """API untuk menghapus prediksi tanah"""
    try:
        cur = mysql.connection.cursor()
        
        # Check if asset exists
        cur.execute("SELECT id FROM prediksi_properti_tanah WHERE id = %s", (asset_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({'error': 'Asset not found'}), 404
        
        # Delete the asset
        cur.execute("DELETE FROM prediksi_properti_tanah WHERE id = %s", (asset_id,))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Aset tanah berhasil dihapus'
        })
        
    except Exception as e:
        print(f"Error in delete_tanah: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/send-tanah-to-user/<int:asset_id>', methods=['POST'])
def send_tanah_to_user(asset_id):
    """API untuk mengirim aset tanah ke user dashboard"""
    try:
        cur = mysql.connection.cursor()
        
        # Check if asset exists
        cur.execute("SELECT id FROM prediksi_properti_tanah WHERE id = %s", (asset_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({'error': 'Asset not found'}), 404
        
        # Update status to sent
        cur.execute("""
            UPDATE prediksi_properti_tanah 
            SET status_kirim_user = 'sent' 
            WHERE id = %s
        """, (asset_id,))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Aset tanah berhasil dikirim ke user'
        })
        
    except Exception as e:
        print(f"Error in send_tanah_to_user: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/rentals')
def api_rentals():
    return jsonify({
        'rentals': [],
        'total': 0,
        'page': 1,
        'per_page': 12,
        'total_pages': 1
    })

@main.route('/api/rental/<int:rental_id>')
def api_rental_detail(rental_id):
    return jsonify({
        'id': rental_id,
        'property_type': 'bangunan',
        'location': 'Kecamatan A',
        'bedrooms': 3,
        'bathrooms': 2,
        'land_area': 120,
        'building_area': 90,
        'monthly_rent': 5000000,
        'condition': 'bagus',
        'furnished': 'Semi Furnished',
        'floors': 2,
        'facing': 'Timur',
        'water_source': 'PDAM',
        'internet': 'Ya',
        'hook': 'Ya',
        'power': 2200,
        'road_width': '6 meter',
        'dining_room': 'Ada',
        'living_room': 'Ada'
    })

# ==================== RENTAL PRICE PREDICTION API ROUTES ====================

@main.route('/api/predict-rental-price', methods=['POST'])
def predict_rental_price():
    """API untuk prediksi harga sewa bulanan properti"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        property_type = data.get('property_type', 'bangunan')
        
        # Initialize predictor
        predictor = PropertyPricePredictor()
        
        # Get rental price predictions
        result = predictor.predict_rental_price_ensemble(data, property_type)
        
        return jsonify({
            'status': 'success',
            'predictions': result.get('predictions', {}),
            'ensemble_price': result.get('ensemble', 0),
            'confidence': result.get('confidence', 0.85),
            'model_type': result.get('model_type', 'ensemble'),
            'property_type': property_type
        })
        
    except Exception as e:
        print(f"Error in predict_rental_price: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/save-rental-prediction', methods=['POST'])
def save_rental_prediction():
    """API untuk menyimpan prediksi harga sewa ke database"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        cur = mysql.connection.cursor()
        
        # Insert into rental predictions table
        cur.execute("""
            INSERT INTO prediksi_sewa_bulanan 
            (kecamatan, kelurahan, luas_tanah_m2, luas_bangunan_m2, 
             kamar_tidur, kamar_mandi, jumlah_lantai, tahun_dibangun, 
             daya_listrik, sertifikat, kondisi_properti, tingkat_keamanan, 
             aksesibilitas, tipe_iklan, NJOP_Rp_per_m2,
             harga_sewa_rf, harga_sewa_xgb, harga_sewa_catboost,
             harga_sewa_ensemble, confidence_score, model_predictor, 
             property_type, status_kirim_user, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            data.get('kecamatan', ''),
            data.get('kelurahan', ''),
            data.get('luas_tanah_m2', 0),
            data.get('luas_bangunan_m2', 0),
            data.get('kamar_tidur', 0),
            data.get('kamar_mandi', 0),
            data.get('jumlah_lantai', 0),
            data.get('tahun_dibangun', 0),
            data.get('daya_listrik', 0),
            data.get('sertifikat', ''),
            data.get('kondisi_properti', ''),
            data.get('tingkat_keamanan', ''),
            data.get('aksesibilitas', ''),
            data.get('tipe_iklan', ''),
            data.get('njop_per_m2', 0),
            data.get('harga_sewa_rf', 0),
            data.get('harga_sewa_xgb', 0),
            data.get('harga_sewa_catboost', 0),
            data.get('harga_sewa_ensemble', 0),
            data.get('confidence_score', 0),
            'ensemble',
            data.get('property_type', 'bangunan'),
            'pending'
        ))
        
        mysql.connection.commit()
        prediction_id = cur.lastrowid
        cur.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Prediksi sewa berhasil disimpan',
            'prediction_id': prediction_id
        })
        
    except Exception as e:
        print(f"Error in save_rental_prediction: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/send-rental-to-user/<int:prediction_id>', methods=['POST'])
def send_rental_to_user(prediction_id):
    """API untuk mengirim aset sewa ke user dashboard"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        cur = mysql.connection.cursor()
        
        # Update status to 'sent' for rental
        cur.execute("""
            UPDATE prediksi_sewa_bulanan 
            SET status_kirim_user = 'sent', updated_at = NOW()
            WHERE id = %s
        """, (prediction_id,))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Aset sewa berhasil disewakan ke pelanggan'
        })
        
    except Exception as e:
        print(f"Error in send_rental_to_user: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/rental-predictions-list')
def get_rental_predictions_list():
    """API untuk mendapatkan daftar prediksi sewa"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        cur = mysql.connection.cursor()
        
        # Get parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        offset = (page - 1) * per_page
        
        # Get filters
        kecamatan = request.args.get('kecamatan', '')
        status = request.args.get('status', '')
        property_type = request.args.get('property_type', '')
        
        # Build query
        where_conditions = []
        params = []
        
        if kecamatan:
            where_conditions.append("kecamatan = %s")
            params.append(kecamatan)
        
        if status:
            where_conditions.append("status_kirim_user = %s")
            params.append(status)
        
        if property_type:
            where_conditions.append("property_type = %s")
            params.append(property_type)
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Get total count
        cur.execute(f"SELECT COUNT(*) FROM prediksi_sewa_bulanan{where_clause}", params)
        total_items = cur.fetchone()[0]
        
        # Get paginated data
        cur.execute(f"""
            SELECT id, kecamatan, kelurahan, luas_tanah_m2, luas_bangunan_m2,
                   kamar_tidur, kamar_mandi, jumlah_lantai, tahun_dibangun, 
                   daya_listrik, sertifikat, kondisi_properti, tingkat_keamanan,
                   aksesibilitas, tipe_iklan, NJOP_Rp_per_m2,
                   harga_sewa_rf, harga_sewa_xgb, harga_sewa_catboost,
                   harga_sewa_ensemble, confidence_score, model_predictor,
                   property_type, status_kirim_user, created_at
            FROM prediksi_sewa_bulanan{where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        rows = cur.fetchall()
        cur.close()
        
        # Format data
        predictions = []
        for row in rows:
            predictions.append({
                'id': row[0],
                'kecamatan': row[1],
                'kelurahan': row[2],
                'luas_tanah_m2': row[3],
                'luas_bangunan_m2': row[4],
                'kamar_tidur': row[5],
                'kamar_mandi': row[6],
                'jumlah_lantai': row[7],
                'tahun_dibangun': row[8],
                'daya_listrik': row[9],
                'sertifikat': row[10],
                'kondisi_properti': row[11],
                'tingkat_keamanan': row[12],
                'aksesibilitas': row[13],
                'tipe_iklan': row[14],
                'njop_per_m2': row[15],
                'harga_sewa_rf': row[16],
                'harga_sewa_xgb': row[17],
                'harga_sewa_catboost': row[18],
                'harga_sewa_ensemble': row[19],
                'confidence_score': row[20],
                'model_predictor': row[21],
                'property_type': row[22],
                'status_kirim_user': row[23],
                'created_at': row[24].strftime('%Y-%m-%d %H:%M:%S') if row[24] else None
            })
        
        return jsonify({
            'status': 'success',
            'data': predictions,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_items': total_items,
                'total_pages': (total_items + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        print(f"Error in get_rental_predictions_list: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/rental-aset-tersedia')
def get_rental_aset_tersedia():
    """API untuk mendapatkan aset sewa yang tersedia (dikirim dari admin)"""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        offset = (page - 1) * per_page
        
        # Get filter parameters
        kecamatan = request.args.get('kecamatan', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        min_area = request.args.get('min_area', '')
        max_area = request.args.get('max_area', '')
        property_type = request.args.get('property_type', '')
        
        cur = mysql.connection.cursor()
        
        # Build WHERE conditions
        where_conditions = ["status_kirim_user = 'sent'"]
        params = []
        
        if kecamatan:
            where_conditions.append("kecamatan = %s")
            params.append(kecamatan)
        
        if min_price:
            where_conditions.append("harga_sewa_ensemble >= %s")
            params.append(float(min_price))
        
        if max_price:
            where_conditions.append("harga_sewa_ensemble <= %s")
            params.append(float(max_price))
        
        if min_area:
            where_conditions.append("luas_tanah_m2 >= %s")
            params.append(int(min_area))
        
        if max_area:
            where_conditions.append("luas_tanah_m2 <= %s")
            params.append(int(max_area))
        
        if property_type:
            where_conditions.append("property_type = %s")
            params.append(property_type)
        
        where_clause = " WHERE " + " AND ".join(where_conditions)
        
        # Get total count
        cur.execute(f"SELECT COUNT(*) FROM prediksi_sewa_bulanan{where_clause}", params)
        total_items = cur.fetchone()[0]
        
        # Get paginated data
        cur.execute(f"""
            SELECT id, kecamatan, kelurahan, luas_tanah_m2, luas_bangunan_m2,
                   kamar_tidur, kamar_mandi, jumlah_lantai, tahun_dibangun,
                   daya_listrik, sertifikat, kondisi_properti, tingkat_keamanan,
                   aksesibilitas, tipe_iklan, NJOP_Rp_per_m2,
                   harga_sewa_rf, harga_sewa_xgb, harga_sewa_catboost,
                   harga_sewa_ensemble, confidence_score, model_predictor,
                   property_type, created_at
            FROM prediksi_sewa_bulanan{where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        
        rows = cur.fetchall()
        cur.close()
        
        # Format data
        assets = []
        for row in rows:
            assets.append({
                'id': row[0],
                'jenis': 'sewa_' + row[22],  # sewa_bangunan or sewa_tanah
                'kecamatan': row[1],
                'kelurahan': row[2],
                'luas_tanah': float(row[3]) if row[3] else 0,
                'luas_bangunan': float(row[4]) if row[4] else 0,
                'kamar_tidur': row[5],
                'kamar_mandi': row[6],
                'jumlah_lantai': row[7],
                'tahun_dibangun': row[8],
                'daya_listrik': row[9],
                'sertifikat': row[10],
                'kondisi_properti': row[11],
                'tingkat_keamanan': row[12],
                'aksesibilitas': row[13],
                'tipe_iklan': row[14],
                'njop_per_m2': row[15],
                'harga_sewa_rf': row[16],
                'harga_sewa_xgb': row[17],
                'harga_sewa_catboost': row[18],
                'harga_sewa_ensemble': row[19],
                'confidence_score': row[20],
                'model_predictor': row[21],
                'property_type': row[22],
                'created_at': row[23].strftime('%Y-%m-%d %H:%M:%S') if row[23] else None,
                'alamat': f"{row[1]}, Surabaya"
            })
        
        # Calculate pagination info
        total_pages = (total_items + per_page - 1) // per_page
        
        return jsonify({
            'status': 'success',
            'data': assets,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'per_page': per_page,
                'total_count': total_items
            }
        })
        
    except Exception as e:
        print(f"Error in get_rental_aset_tersedia: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/api/aset-tanah-detail/<int:asset_id>')
def get_aset_tanah_detail(asset_id):
    """API untuk mendapatkan detail aset tanah"""
    try:
        cur = mysql.connection.cursor()
        
        # Get asset details (exclude NJOP from user view)
        cur.execute("""
            SELECT id, kecamatan, kelurahan, luas_tanah_m2, 
                   zona_nilai_tanah, kelas_tanah, jenis_sertifikat, 
                   harga_prediksi_tanah, harga_per_m2_tanah, model_predictor, 
                   confidence_score, created_at
            FROM prediksi_properti_tanah 
            WHERE id = %s AND status_kirim_user = 'sent'
        """, (asset_id,))
        
        row = cur.fetchone()
        cur.close()
        
        if not row:
            return jsonify({'error': 'Asset not found'}), 404
        
        asset = {
            'id': row[0],
            'kecamatan': row[1],
            'kelurahan': row[2],
            'luas_tanah_m2': row[3],
            'zona_nilai_tanah': row[4],
            'kelas_tanah': row[5],
            'jenis_sertifikat': row[6],
            'harga_prediksi_tanah': row[7],
            'harga_per_m2_tanah': row[8],
            'model_predictor': row[9],
            'confidence_score': row[10],
            'created_at': row[11].strftime('%Y-%m-%d %H:%M:%S') if row[11] else None,
            'alamat': f"{row[1]}, Surabaya"
        }
        
        return jsonify({
            'status': 'success',
            'data': asset
        })
        
    except Exception as e:
        print(f"Error in get_aset_tanah_detail: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/user-rent-form')
def user_rent_form():
    """Route untuk menampilkan form sewa aset"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    return render_template('user_rent_form.html')

@main.route('/submit-rent-application', methods=['POST'])
def submit_rent_application():
    """API untuk mengirim pengajuan sewa"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'User not logged in'}), 401
        
        # Get form data
        user_id = session['user_id']
        aset_id = request.form.get('aset_id')
        jenis_aset = request.form.get('jenis_aset')
        nama_penyewa = request.form.get('nama_penyewa')
        email = request.form.get('email')
        telepon = request.form.get('telepon')
        durasi_sewa = request.form.get('durasi_sewa')
        tanggal_mulai = request.form.get('tanggal_mulai')
        pesan = request.form.get('pesan', '')
        
        # Validate required fields
        if not all([aset_id, jenis_aset, nama_penyewa, email, telepon, durasi_sewa, tanggal_mulai]):
            return jsonify({'error': 'All required fields must be filled'}), 400
        
        cur = mysql.connection.cursor()
        
        # Check if the pengajuan_sewa table exists, if not create it
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pengajuan_sewa (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                aset_id INT NOT NULL,
                jenis_aset ENUM('tanah', 'tanah_bangunan') NOT NULL,
                nama_penyewa VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                telepon VARCHAR(20) NOT NULL,
                durasi_sewa INT NOT NULL COMMENT 'dalam bulan',
                tanggal_mulai DATE NOT NULL,
                pesan TEXT,
                status ENUM('pending', 'approved', 'rejected', 'completed') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # Convert jenis_aset to match enum
        jenis_aset_enum = 'tanah' if jenis_aset == 'tanah' else 'tanah_bangunan'
        
        # Insert the rent application
        cur.execute("""
            INSERT INTO pengajuan_sewa (
                user_id, aset_id, jenis_aset, nama_penyewa, email, telepon, 
                durasi_sewa, tanggal_mulai, pesan
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, aset_id, jenis_aset_enum, nama_penyewa, email, telepon,
            durasi_sewa, tanggal_mulai, pesan
        ))
        
        mysql.connection.commit()
        application_id = cur.lastrowid
        cur.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Pengajuan sewa berhasil dikirim',
            'application_id': application_id
        })
        
    except Exception as e:
        print(f"Error in submit_rent_application: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/user-available-assets')
def user_available_assets():
    """Route untuk menampilkan aset yang tersedia untuk user"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    return render_template('user_available_assets.html')









