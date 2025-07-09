from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql
from flask import jsonify
from .models import User
from .data_processor import AssetDataProcessor
from .prediction_models import PrediksiPropertiTanah, PrediksiPropertiBangunanTanah

main = Blueprint('main', __name__)

data_processor = AssetDataProcessor()

@main.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        else:
            return redirect(url_for('main.user_dashboard'))
    return render_template('index.html')

@main.route('/home')
def home_page():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name, password, role FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]  # SIMPAN NAMA
            session['role'] = user[3]

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
        role = request.form.get('role', 'user')

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
    
    # Gabungkan statistik (stats_tanah dan stats_bangunan adalah tuple dari fetchone())
    total_tanah = stats_tanah[0] if stats_tanah and stats_tanah[0] else 0
    avg_price_tanah = stats_tanah[1] if stats_tanah and stats_tanah[1] else 0
    
    total_bangunan = stats_bangunan[0] if stats_bangunan and stats_bangunan[0] else 0
    avg_price_bangunan = stats_bangunan[1] if stats_bangunan and stats_bangunan[1] else 0
    
    combined_stats = {
        'total_properties': total_tanah + total_bangunan,
        'avg_price': (avg_price_tanah + avg_price_bangunan) / 2 if avg_price_tanah > 0 or avg_price_bangunan > 0 else 0,
        'total_locations': 31  # Total kecamatan di Surabaya
    }

    return render_template('dashboard_admin.html', 
                         stats=combined_stats, 
                         stats_tanah=stats_tanah, 
                         stats_bangunan=stats_bangunan)

@main.route('/user-dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('main.login'))
    
    stats = data_processor.get_statistics()
    return render_template('dashboard_user.html', stats=stats)

@main.route('/logout')
def logout_user():
    session.clear()
    flash('Logout berhasil.', 'success')
    return redirect(url_for('main.login'))

@main.route('/data')
def data():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('main.login'))
    return render_template('data.html')

@main.route('/visualization')
def visualization():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('main.login'))
    return render_template('visualization.html')

# Route untuk Total Properti
@main.route('/total-properti')
def total_properti():
    """Halaman untuk menampilkan seluruh data prediksi"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))
    
    # Ambil SEMUA data prediksi tanah dan bangunan tanpa limit
    prediksi_tanah = PrediksiPropertiTanah.get_all(limit=10000, offset=0)  # Ambil semua data
    prediksi_bangunan = PrediksiPropertiBangunanTanah.get_all(limit=10000, offset=0)  # Ambil semua data
    
    # Ambil statistik
    stats_tanah = PrediksiPropertiTanah.get_statistics()
    stats_bangunan = PrediksiPropertiBangunanTanah.get_statistics()
    
    return render_template('total_properti.html', 
                         prediksi_tanah=prediksi_tanah,
                         prediksi_bangunan=prediksi_bangunan,
                         stats_tanah=stats_tanah,
                         stats_bangunan=stats_bangunan)

# Route untuk Manajemen Data Aset
@main.route('/manajemen-aset')
def manajemen_aset():
    """Halaman untuk CRUD manajemen data aset"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
        return redirect(url_for('main.login'))
    
    return render_template('manajemen_aset.html')

# Route untuk menambah data tanah
@main.route('/tambah-tanah', methods=['GET', 'POST'])
def tambah_tanah():
    """Route untuk menambah data tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            # Ambil data dari form
            kecamatan = request.form['kecamatan']
            kelurahan = request.form['kelurahan'] 
            luas_tanah = int(request.form['luas_tanah_m2'])
            njop_tanah = float(request.form['njop_tanah_per_m2'])
            zona_nilai = int(request.form['zona_nilai_tanah'])
            kelas_tanah = request.form['kelas_tanah']
            sertifikat = request.form['jenis_sertifikat']
            
            # Hitung harga prediksi sederhana
            # Faktor zona berdasarkan angka (1=premium, 5=ekonomis)
            zona_factor = 1.6 - (zona_nilai * 0.1)  # 1.5, 1.4, 1.3, 1.2, 1.1
            
            harga_prediksi = luas_tanah * njop_tanah * zona_factor
            harga_per_m2 = harga_prediksi / luas_tanah
            
            # Insert ke database
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO prediksi_properti_tanah 
                (kecamatan, kelurahan, luas_tanah_m2, njop_tanah_per_m2, 
                 zona_nilai_tanah, kelas_tanah, jenis_sertifikat, 
                 harga_prediksi_tanah, harga_per_m2_tanah, model_predictor)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (kecamatan, kelurahan, luas_tanah, njop_tanah, zona_nilai, 
                  kelas_tanah, sertifikat, harga_prediksi, harga_per_m2, 'Manual Input'))
            
            mysql.connection.commit()
            cur.close()
            
            flash('Data tanah berhasil ditambahkan!', 'success')
            return redirect(url_for('main.manajemen_aset'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('form_tanah.html')

# Route untuk menambah data bangunan
@main.route('/tambah-bangunan', methods=['GET', 'POST'])
def tambah_bangunan():
    """Route untuk menambah data bangunan + tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            # Ambil data dari form
            kecamatan = request.form['kecamatan']
            luas_tanah = int(request.form['luas_tanah_m2'])
            luas_bangunan = int(request.form['luas_bangunan_m2'])
            kamar_tidur = int(request.form['jumlah_kamar_tidur'])
            kamar_mandi = int(request.form['jumlah_kamar_mandi'])
            lantai = float(request.form['jumlah_lantai'])
            tahun_dibangun = int(request.form['tahun_dibangun'])
            daya_listrik = int(request.form['daya_listrik'])
            sertifikat = request.form['sertifikat']
            kondisi = request.form['kondisi_properti']
            keamanan = request.form['tingkat_keamanan']
            aksesibilitas = request.form['aksesibilitas']
            tipe_iklan = request.form['tipe_iklan']
            njop_per_m2 = float(request.form['njop_per_m2'])
            
            # Hitung nilai tambahan
            rasio_bangunan_tanah = luas_bangunan / luas_tanah
            umur_bangunan = 2024 - tahun_dibangun
            
            # Hitung harga sederhana
            harga_tanah = luas_tanah * njop_per_m2
            harga_bangunan = luas_bangunan * 8000000  # Asumsi 8jt per m2
            harga_total = harga_tanah + harga_bangunan
            harga_per_m2_bangunan = harga_bangunan / luas_bangunan
            
            # Insert ke database
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO prediksi_properti_bangunan_tanah 
                (kecamatan, luas_tanah_m2, luas_bangunan_m2, jumlah_kamar_tidur, 
                 jumlah_kamar_mandi, jumlah_lantai, tahun_dibangun, daya_listrik, 
                 sertifikat, kondisi_properti, tingkat_keamanan, aksesibilitas, 
                 tipe_iklan, njop_per_m2, rasio_bangunan_tanah, umur_bangunan,
                 harga_prediksi_total, harga_prediksi_tanah, harga_prediksi_bangunan, 
                 harga_per_m2_bangunan, model_predictor)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (kecamatan, luas_tanah, luas_bangunan, kamar_tidur, kamar_mandi, 
                  lantai, tahun_dibangun, daya_listrik, sertifikat, kondisi, 
                  keamanan, aksesibilitas, tipe_iklan, njop_per_m2, rasio_bangunan_tanah, 
                  umur_bangunan, harga_total, harga_tanah, harga_bangunan, 
                  harga_per_m2_bangunan, 'Manual Input'))
            
            mysql.connection.commit()
            cur.close()
            
            flash('Data bangunan berhasil ditambahkan!', 'success')
            return redirect(url_for('main.manajemen_aset'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('form_bangunan.html')

# Route untuk menghapus data tanah
@main.route('/hapus-tanah/<int:id>', methods=['POST'])
def hapus_tanah(id):
    """Route untuk menghapus data tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM prediksi_properti_tanah WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        
        flash('Data tanah berhasil dihapus!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('main.total_properti'))

# Route untuk menghapus data bangunan
@main.route('/hapus-bangunan/<int:id>', methods=['POST'])
def hapus_bangunan(id):
    """Route untuk menghapus data bangunan"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('main.login'))
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM prediksi_properti_bangunan_tanah WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        
        flash('Data bangunan berhasil dihapus!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('main.total_properti'))

# Route untuk edit data tanah
@main.route('/edit-tanah/<int:id>', methods=['GET', 'POST'])
def edit_tanah(id):
    """Route untuk edit data tanah"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            # Ambil data dari form
            kecamatan = request.form['kecamatan']
            kelurahan = request.form['kelurahan']
            luas_tanah = int(request.form['luas_tanah_m2'])
            njop_tanah = float(request.form['njop_tanah_per_m2'])
            zona_nilai = int(request.form['zona_nilai_tanah'])
            kelas_tanah = request.form['kelas_tanah']
            sertifikat = request.form['jenis_sertifikat']
            
            # Hitung harga prediksi sederhana
            zona_factor = 1.6 - (zona_nilai * 0.1)
            harga_prediksi = luas_tanah * njop_tanah * zona_factor
            harga_per_m2 = harga_prediksi / luas_tanah
            
            # Update ke database
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE prediksi_properti_tanah SET
                kecamatan = %s, kelurahan = %s, luas_tanah_m2 = %s, 
                njop_tanah_per_m2 = %s, zona_nilai_tanah = %s, kelas_tanah = %s,
                jenis_sertifikat = %s, harga_prediksi_tanah = %s, harga_per_m2_tanah = %s
                WHERE id = %s
            """, (kecamatan, kelurahan, luas_tanah, njop_tanah, zona_nilai,
                  kelas_tanah, sertifikat, harga_prediksi, harga_per_m2, id))
            
            mysql.connection.commit()
            cur.close()
            
            flash('Data tanah berhasil diupdate!', 'success')
            return redirect(url_for('main.total_properti'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    # Ambil data existing untuk form
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM prediksi_properti_tanah WHERE id = %s", (id,))
        data = cur.fetchone()
        cur.close()
        
        if not data:
            flash('Data tidak ditemukan!', 'error')
            return redirect(url_for('main.total_properti'))
        
        return render_template('form_tanah.html', data=data, is_edit=True)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('main.total_properti'))

# Route untuk edit data bangunan
@main.route('/edit-bangunan/<int:id>', methods=['GET', 'POST'])
def edit_bangunan(id):
    """Route untuk edit data bangunan"""
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Akses ditolak.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            # Ambil data dari form
            kecamatan = request.form['kecamatan']
            luas_tanah = int(request.form['luas_tanah_m2'])
            luas_bangunan = int(request.form['luas_bangunan_m2'])
            kamar_tidur = int(request.form['jumlah_kamar_tidur'])
            kamar_mandi = int(request.form['jumlah_kamar_mandi'])
            lantai = float(request.form['jumlah_lantai'])
            tahun_dibangun = int(request.form['tahun_dibangun'])
            daya_listrik = int(request.form['daya_listrik'])
            sertifikat = request.form['sertifikat']
            kondisi = request.form['kondisi_properti']
            keamanan = request.form['tingkat_keamanan']
            aksesibilitas = request.form['aksesibilitas']
            tipe_iklan = request.form['tipe_iklan']
            njop_per_m2 = float(request.form['njop_per_m2'])
            
            # Hitung nilai tambahan
            rasio_bangunan_tanah = luas_bangunan / luas_tanah
            umur_bangunan = 2024 - tahun_dibangun
            
            # Hitung harga sederhana
            harga_tanah = luas_tanah * njop_per_m2
            harga_bangunan = luas_bangunan * 8000000  # Asumsi 8jt per m2
            harga_total = harga_tanah + harga_bangunan
            harga_per_m2_bangunan = harga_bangunan / luas_bangunan
            
            # Update ke database
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE prediksi_properti_bangunan_tanah SET
                kecamatan = %s, luas_tanah_m2 = %s, luas_bangunan_m2 = %s, 
                jumlah_kamar_tidur = %s, jumlah_kamar_mandi = %s, jumlah_lantai = %s,
                tahun_dibangun = %s, daya_listrik = %s, sertifikat = %s, kondisi_properti = %s,
                tingkat_keamanan = %s, aksesibilitas = %s, tipe_iklan = %s, njop_per_m2 = %s,
                rasio_bangunan_tanah = %s, umur_bangunan = %s, harga_prediksi_total = %s,
                harga_prediksi_tanah = %s, harga_prediksi_bangunan = %s, harga_per_m2_bangunan = %s
                WHERE id = %s
            """, (kecamatan, luas_tanah, luas_bangunan, kamar_tidur, kamar_mandi, lantai,
                  tahun_dibangun, daya_listrik, sertifikat, kondisi, keamanan, aksesibilitas,
                  tipe_iklan, njop_per_m2, rasio_bangunan_tanah, umur_bangunan, harga_total,
                  harga_tanah, harga_bangunan, harga_per_m2_bangunan, id))
            
            mysql.connection.commit()
            cur.close()
            
            flash('Data bangunan berhasil diupdate!', 'success')
            return redirect(url_for('main.total_properti'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    # Ambil data existing untuk form
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM prediksi_properti_bangunan_tanah WHERE id = %s", (id,))
        data = cur.fetchone()
        cur.close()
        
        if not data:
            flash('Data tidak ditemukan!', 'error')
            return redirect(url_for('main.total_properti'))
        
        return render_template('form_bangunan.html', data=data, is_edit=True)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('main.total_properti'))

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
    
    if kecamatan:
        predictions = PrediksiPropertiTanah.search_by_kecamatan(kecamatan, limit)
    else:
        predictions = PrediksiPropertiTanah.get_all(limit, 0)
    
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

@main.route('/api/prediksi-bangunan-tanah')
def api_prediksi_bangunan_tanah():
    """API untuk mendapatkan data prediksi bangunan + tanah"""
    kecamatan = request.args.get('kecamatan', '')
    limit = request.args.get('limit', 50, type=int)
    
    if kecamatan:
        predictions = PrediksiPropertiBangunanTanah.search_by_criteria(kecamatan=kecamatan, limit=limit)
    else:
        predictions = PrediksiPropertiBangunanTanah.get_all(limit, 0)
    
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

@main.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        # Cek apakah ini form ubah password atau edit profil
        if 'current_password' in request.form:
            # Handler untuk ubah password
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validasi input password
            if not current_password or not new_password or not confirm_password:
                flash('Semua field password wajib diisi.', 'error')
                return render_template('edit_profile.html')
            
            if new_password != confirm_password:
                flash('Password baru dan konfirmasi password tidak cocok.', 'error')
                return render_template('edit_profile.html')
            
            if len(new_password) < 8:
                flash('Password baru minimal 8 karakter.', 'error')
                return render_template('edit_profile.html')
            
            try:
                cur = mysql.connection.cursor()
                
                # Ambil password lama dari database
                cur.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
                user_data = cur.fetchone()
                
                if not user_data:
                    flash('User tidak ditemukan.', 'error')
                    cur.close()
                    return render_template('edit_profile.html')
                
                # Verifikasi password lama
                if not check_password_hash(user_data[0], current_password):
                    flash('Password saat ini salah.', 'error')
                    cur.close()
                    return render_template('edit_profile.html')
                
                # Hash password baru
                new_password_hash = generate_password_hash(new_password)
                
                # Update password di database
                cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_password_hash, session['user_id']))
                mysql.connection.commit()
                cur.close()
                
                flash('Password berhasil diubah. Silakan login ulang.', 'success')
                session.clear()  # Logout user setelah ubah password
                return redirect(url_for('main.login'))
                
            except Exception as e:
                flash(f'Terjadi kesalahan saat mengubah password: {str(e)}', 'error')
                return render_template('edit_profile.html')
        
        else:
            # Handler untuk edit profil
            user_name = request.form.get('user_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            company = request.form.get('company')
            address = request.form.get('address')
            
            # Validasi input
            if not user_name or not email:
                flash('Nama dan email wajib diisi.', 'error')
                return render_template('edit_profile.html')
            
            try:
                cur = mysql.connection.cursor()
                
                # Cek apakah email sudah digunakan oleh user lain
                cur.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, session['user_id']))
                existing_user = cur.fetchone()
                
                if existing_user:
                    flash('Email sudah digunakan oleh user lain.', 'error')
                    cur.close()
                    return render_template('edit_profile.html')
                
                # Update data user
                cur.execute("""
                    UPDATE users 
                    SET name = %s, email = %s, phone = %s, company = %s, address = %s 
                    WHERE id = %s
                """, (user_name, email, phone, company, address, session['user_id']))
                
                mysql.connection.commit()
                cur.close()
                
                # Update session data
                session['user_name'] = user_name
                session['user_email'] = email
                session['user_phone'] = phone
                session['user_company'] = company
                session['user_address'] = address
                
                flash('Profil berhasil diperbarui.', 'success')
                return redirect(url_for('main.edit_profile'))
                
            except Exception as e:
                flash(f'Terjadi kesalahan: {str(e)}', 'error')
                return render_template('edit_profile.html')
    
    # GET request - ambil data user dari database
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT name, email, phone, company, address FROM users WHERE id = %s", (session['user_id'],))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data:
            session['user_name'] = user_data[0] or session.get('user_name', '')
            session['user_email'] = user_data[1] or ''
            session['user_phone'] = user_data[2] or ''
            session['user_company'] = user_data[3] or ''
            session['user_address'] = user_data[4] or ''
    except Exception as e:
        flash(f'Error mengambil data: {str(e)}', 'error')
    
    return render_template('edit_profile.html')

@main.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """
    Route untuk backward compatibility - redirect ke edit_profile
    karena fitur ubah password sudah digabung dengan edit profil
    """
    if request.method == 'GET':
        flash('Fitur ubah password sudah digabung dengan edit profil.', 'info')
        return redirect(url_for('main.edit_profile'))
    
    # Untuk POST request, tetap redirect tapi dengan pesan yang lebih spesifik
    flash('Silakan gunakan form edit profil untuk mengubah password.', 'info')
    return redirect(url_for('main.edit_profile'))

# API Routes untuk Dashboard User
@main.route('/api/aset-tersedia')
def api_aset_tersedia():
    """
    API endpoint untuk mendapatkan daftar aset yang tersedia untuk disewa
    """
    try:
        # Get filter parameters
        jenis = request.args.get('jenis', '')
        kecamatan = request.args.get('kecamatan', '')
        
        cur = mysql.connection.cursor()
        
        aset_list = []
        
        # Get data tanah
        if not jenis or jenis == 'tanah':
            tanah_query = """
                SELECT id, kecamatan, kelurahan, luas_tanah_m2, 
                       harga_prediksi_tanah, created_at
                FROM prediksi_properti_tanah 
                WHERE 1=1
            """
            tanah_params = []
            
            if kecamatan:
                tanah_query += " AND kecamatan = %s"
                tanah_params.append(kecamatan)
                
            tanah_query += " ORDER BY created_at DESC LIMIT 10"
            
            cur.execute(tanah_query, tanah_params)
            tanah_data = cur.fetchall()
            
            for tanah in tanah_data:
                # Calculate estimated rental price (assume 0.5% of property value per month)
                harga_sewa = int(tanah[4] * 0.005) if tanah[4] else 0
                
                aset_list.append({
                    'id': f"tanah_{tanah[0]}",
                    'alamat': f"{tanah[2]}, {tanah[1]}" if tanah[2] else tanah[1],
                    'kecamatan': tanah[1],
                    'luas_tanah': tanah[3],
                    'luas_bangunan': 0,
                    'harga_sewa': harga_sewa,
                    'jenis': 'tanah',
                    'status': 'Tersedia'
                })
        
        # Get data bangunan
        if not jenis or jenis == 'tanah_bangunan':
            bangunan_query = """
                SELECT id, kecamatan, kelurahan, luas_tanah_m2, luas_bangunan_m2,
                       harga_prediksi_bangunan_tanah, created_at
                FROM prediksi_properti_bangunan_tanah 
                WHERE 1=1
            """
            bangunan_params = []
            
            if kecamatan:
                bangunan_query += " AND kecamatan = %s"
                bangunan_params.append(kecamatan)
                
            bangunan_query += " ORDER BY created_at DESC LIMIT 10"
            
            cur.execute(bangunan_query, bangunan_params)
            bangunan_data = cur.fetchall()
            
            for bangunan in bangunan_data:
                # Calculate estimated rental price (assume 0.5% of property value per month)
                harga_sewa = int(bangunan[5] * 0.005) if bangunan[5] else 0
                
                aset_list.append({
                    'id': f"bangunan_{bangunan[0]}",
                    'alamat': f"{bangunan[2]}, {bangunan[1]}" if bangunan[2] else bangunan[1],
                    'kecamatan': bangunan[1],
                    'luas_tanah': bangunan[3],
                    'luas_bangunan': bangunan[4],
                    'harga_sewa': harga_sewa,
                    'jenis': 'tanah_bangunan',
                    'status': 'Tersedia'
                })
        
        cur.close()
        
        # Sort by latest first (since we can't sort by created_at due to potential differences)
        aset_list.reverse()
        
        return jsonify({
            'success': True,
            'data': aset_list[:20],  # Limit to 20 results
            'total': len(aset_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/kecamatan-list')
def api_kecamatan_list():
    """
    API endpoint untuk mendapatkan daftar kecamatan yang tersedia
    """
    try:
        cur = mysql.connection.cursor()
        
        # Get kecamatan from both tables
        kecamatan_set = set()
        
        # From tanah table
        cur.execute("SELECT DISTINCT kecamatan FROM prediksi_properti_tanah WHERE kecamatan IS NOT NULL")
        tanah_kecamatan = cur.fetchall()
        for kec in tanah_kecamatan:
            kecamatan_set.add(kec[0])
        
        # From bangunan table
        cur.execute("SELECT DISTINCT kecamatan FROM prediksi_properti_bangunan_tanah WHERE kecamatan IS NOT NULL")
        bangunan_kecamatan = cur.fetchall()
        for kec in bangunan_kecamatan:
            kecamatan_set.add(kec[0])
        
        cur.close()
        
        kecamatan_list = sorted(list(kecamatan_set))
        
        return jsonify({
            'success': True,
            'data': kecamatan_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/aset-detail/<aset_id>')
def api_aset_detail(aset_id):
    """
    API endpoint untuk mendapatkan detail aset berdasarkan ID
    """
    try:
        # Parse aset_id to get type and actual id
        if aset_id.startswith('tanah_'):
            actual_id = aset_id.replace('tanah_', '')
            table = 'prediksi_properti_tanah'
            jenis = 'tanah'
        elif aset_id.startswith('bangunan_'):
            actual_id = aset_id.replace('bangunan_', '')
            table = 'prediksi_properti_bangunan_tanah'
            jenis = 'tanah_bangunan'
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid aset ID format'
            }), 400
        
        cur = mysql.connection.cursor()
        
        if jenis == 'tanah':
            cur.execute("""
                SELECT id, kecamatan, kelurahan, luas_tanah_m2, njop_tanah_per_m2,
                       zona_nilai_tanah, kelas_tanah, jenis_sertifikat,
                       harga_prediksi_tanah, harga_per_m2_tanah
                FROM prediksi_properti_tanah 
                WHERE id = %s
            """, (actual_id,))
        else:
            cur.execute("""
                SELECT id, kecamatan, kelurahan, luas_tanah_m2, luas_bangunan_m2,
                       jumlah_kamar_tidur, jumlah_kamar_mandi, jumlah_lantai,
                       harga_prediksi_bangunan_tanah, harga_per_m2_bangunan
                FROM prediksi_properti_bangunan_tanah 
                WHERE id = %s
            """, (actual_id,))
        
        aset_data = cur.fetchone()
        cur.close()
        
        if not aset_data:
            return jsonify({
                'success': False,
                'error': 'Aset tidak ditemukan'
            }, 404)
        
        if jenis == 'tanah':
            harga_sewa = int(aset_data[8] * 0.005) if aset_data[8] else 0
            aset_detail = {
                'id': aset_id,
                'jenis': jenis,
                'alamat': f"{aset_data[2]}, {aset_data[1]}",
                'kecamatan': aset_data[1],
                'kelurahan': aset_data[2],
                'luas_tanah': aset_data[3],
                'luas_bangunan': 0,
                'njop_tanah': aset_data[4],
                'zona_nilai': aset_data[5],
                'kelas_tanah': aset_data[6],
                'sertifikat': aset_data[7],
                'harga_prediksi': aset_data[8],
                'harga_per_m2': aset_data[9],
                'harga_sewa': harga_sewa
            }
        else:
            harga_sewa = int(aset_data[8] * 0.005) if aset_data[8] else 0
            aset_detail = {
                'id': aset_id,
                'jenis': jenis,
                'alamat': f"{aset_data[2]}, {aset_data[1]}",
                'kecamatan': aset_data[1],
                'kelurahan': aset_data[2],
                'luas_tanah': aset_data[3],
                'luas_bangunan': aset_data[4],
                'kamar_tidur': aset_data[5],
                'kamar_mandi': aset_data[6],
                'jumlah_lantai': aset_data[7],
                'harga_prediksi': aset_data[8],
                'harga_per_m2': aset_data[9],
                'harga_sewa': harga_sewa
            }
        
        return jsonify({
            'success': True,
            'data': aset_detail
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/histori-sewa')
def api_histori_sewa():
    """
    API endpoint untuk mendapatkan histori sewa user
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get filter parameters
        status = request.args.get('status', '')
        jenis = request.args.get('jenis', '')
        periode = request.args.get('periode', '')
        
        cur = mysql.connection.cursor()
        
        # Build query with filters
        query = """
            SELECT id, user_id, aset_id, jenis_aset, alamat, kecamatan, kelurahan,
                   luas_tanah, luas_bangunan, harga_sewa, status_sewa,
                   tanggal_mulai, tanggal_berakhir, created_at
            FROM histori_sewa 
            WHERE user_id = %s
        """
        params = [session['user_id']]
        
        if status:
            query += " AND status_sewa = %s"
            params.append(status)
            
        if jenis:
            query += " AND jenis_aset = %s"
            params.append(jenis)
            
        if periode:
            if periode == '6bulan':
                query += " AND tanggal_mulai >= DATE_SUB(NOW(), INTERVAL 6 MONTH)"
            elif periode == '1tahun':
                query += " AND tanggal_mulai >= DATE_SUB(NOW(), INTERVAL 1 YEAR)"
            # 'semua' tidak menambah filter
            
        query += " ORDER BY created_at DESC LIMIT 50"
        
        cur.execute(query, params)
        histori_data = cur.fetchall()
        cur.close()

        histori_list = []
        for item in histori_data:
            histori_list.append({
                'id': item[0],
                'user_id': item[1],
                'aset_id': item[2],
                'jenis_aset': item[3],
                'alamat': item[4],
                'kecamatan': item[5],
                'kelurahan': item[6],
                'luas_tanah': item[7],
                'luas_bangunan': item[8],
                'harga_sewa': item[9],
                'status': item[10],
                'tanggal_mulai': item[11].strftime('%Y-%m-%d') if item[11] else None,
                'tanggal_berakhir': item[12].strftime('%Y-%m-%d') if item[12] else None,
                'created_at': item[13].strftime('%Y-%m-%d %H:%M:%S') if item[13] else None
            })
        
        return jsonify({
            'success': True,
            'data': histori_list,
            'total': len(histori_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== USER NOTIFICATION API ENDPOINTS =====

@main.route('/api/notifikasi-user')
def api_notifikasi_user():
    """
    API endpoint untuk mendapatkan notifikasi user
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get filter parameters
        jenis = request.args.get('jenis', '')
        status = request.args.get('status', '')
        periode = request.args.get('periode', '')
        
        cur = mysql.connection.cursor()
        
        # Build query with filters
        query = """
            SELECT id, user_id, jenis, judul, pesan, is_read, action_url, created_at
            FROM notifikasi_user 
            WHERE user_id = %s
        """
        params = [session['user_id']]
        
        if jenis:
            query += " AND jenis = %s"
            params.append(jenis)
            
        if status:
            if status == 'read':
                query += " AND is_read = 1"
            elif status == 'unread':
                query += " AND is_read = 0"
            
        if periode:
            if periode == 'today':
                query += " AND DATE(created_at) = CURDATE()"
            elif periode == 'week':
                query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 1 WEEK)"
            elif periode == 'month':
                query += " AND created_at >= DATE_SUB(NOW(), INTERVAL 1 MONTH)"
            
        query += " ORDER BY created_at DESC LIMIT 50"
        
        cur.execute(query, params)
        notif_data = cur.fetchall()
        
        # Get unread count
        cur.execute("SELECT COUNT(*) FROM notifikasi_user WHERE user_id = %s AND is_read = 0", [session['user_id']])
        unread_count = cur.fetchone()[0]
        
        cur.close()

        notif_list = []
        for item in notif_data:
            notif_list.append({
                'id': item[0],
                'user_id': item[1],
                'jenis': item[2],
                'judul': item[3],
                'pesan': item[4],
                'is_read': bool(item[5]),
                'action_url': item[6],
                'created_at': item[7].strftime('%Y-%m-%d %H:%M:%S') if item[7] else None
            })
        
        return jsonify({
            'success': True,
            'data': notif_list,
            'unread_count': unread_count,
            'total': len(notif_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/notifikasi-mark-read/<int:notif_id>', methods=['POST'])
def api_mark_notification_read(notif_id):
    """
    API endpoint untuk menandai notifikasi sebagai telah dibaca
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        cur = mysql.connection.cursor()
        
        # Update notification as read
        cur.execute("""
            UPDATE notifikasi_user 
            SET is_read = 1 
            WHERE id = %s AND user_id = %s
        """, (notif_id, session['user_id']))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/notifikasi-mark-all-read', methods=['POST'])
def api_mark_all_notifications_read():
    """
    API endpoint untuk menandai semua notifikasi sebagai telah dibaca
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        cur = mysql.connection.cursor()
        
        # Update all notifications as read for the user
        cur.execute("""
            UPDATE notifikasi_user 
            SET is_read = 1 
            WHERE user_id = %s
        """, [session['user_id']])
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/notifikasi-clear-all', methods=['DELETE'])
def api_clear_all_notifications():
    """
    API endpoint untuk menghapus semua notifikasi user
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        cur = mysql.connection.cursor()
        
        # Delete all notifications for the user
        cur.execute("""
            DELETE FROM notifikasi_user 
            WHERE user_id = %s
        """, [session['user_id']])
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== FAVORIT ASET API ENDPOINTS =====

@main.route('/api/favorit-aset')
def api_favorit_aset():
    """
    API endpoint untuk mendapatkan aset favorit user
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Get filter parameters
        jenis = request.args.get('jenis', '')
        kecamatan = request.args.get('kecamatan', '')
        
        cur = mysql.connection.cursor()
        
        # Build query with joins to get aset details
        query = """
            SELECT f.id, f.user_id, f.aset_id, f.catatan, f.created_at,
                   a.jenis, a.alamat, a.kecamatan, a.kelurahan, a.luas_tanah, 
                   a.luas_bangunan, a.harga_sewa, a.harga_prediksi, a.status
            FROM favorit_aset f
            JOIN aset_sewa a ON f.aset_id = a.id
            WHERE f.user_id = %s
        """
        params = [session['user_id']]
        
        if jenis:
            query += " AND a.jenis = %s"
            params.append(jenis)
            
        if kecamatan:
            query += " AND a.kecamatan = %s"
            params.append(kecamatan)
            
        query += " ORDER BY f.created_at DESC"
        
        cur.execute(query, params)
        favorit_data = cur.fetchall()
        cur.close()

        favorit_list = []
        for item in favorit_data:
            favorit_list.append({
                'id': item[0],
                'user_id': item[1],
                'aset_id': item[2],
                'catatan': item[3],
                'created_at': item[4].strftime('%Y-%m-%d %H:%M:%S') if item[4] else None,
                'jenis': item[5],
                'alamat': item[6],
                'kecamatan': item[7],
                'kelurahan': item[8],
                'luas_tanah': float(item[9]) if item[9] else 0,
                'luas_bangunan': float(item[10]) if item[10] else 0,
                'harga_sewa': float(item[11]) if item[11] else 0,
                'harga_prediksi': float(item[12]) if item[12] else 0,
                'status': item[13]
            })
        
        return jsonify({
            'success': True,
            'data': favorit_list,
            'total': len(favorit_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/favorit-toggle', methods=['POST'])
def api_favorit_toggle():
    """
    API endpoint untuk menambah/menghapus aset dari favorit
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        aset_id = data.get('aset_id')
        action = data.get('action', 'add')  # add or remove
        catatan = data.get('catatan', '')
        
        if not aset_id:
            return jsonify({'success': False, 'error': 'aset_id required'}), 400
        
        cur = mysql.connection.cursor()
        
        if action == 'add':
            # Add to favorites
            try:
                cur.execute("""
                    INSERT INTO favorit_aset (user_id, aset_id, catatan)
                    VALUES (%s, %s, %s)
                """, (session['user_id'], aset_id, catatan))
                mysql.connection.commit()
                message = 'Aset berhasil ditambahkan ke favorit'
            except mysql.connector.IntegrityError:
                # Already exists
                cur.close()
                return jsonify({'success': False, 'error': 'Aset sudah ada di favorit'}), 400
                
        elif action == 'remove':
            # Remove from favorites
            cur.execute("""
                DELETE FROM favorit_aset 
                WHERE user_id = %s AND aset_id = %s
            """, (session['user_id'], aset_id))
            mysql.connection.commit()
            message = 'Aset berhasil dihapus dari favorit'
        
        cur.close()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/favorit-note/<int:favorit_id>', methods=['PUT'])
def api_favorit_update_note(favorit_id):
    """
    API endpoint untuk mengupdate catatan favorit
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        catatan = data.get('catatan', '')
        
        cur = mysql.connection.cursor()
        
        # Update catatan hanya jika favorit milik user yang login
        cur.execute("""
            UPDATE favorit_aset 
            SET catatan = %s 
            WHERE id = %s AND user_id = %s
        """, (catatan, favorit_id, session['user_id']))
        
        if cur.rowcount == 0:
            cur.close()
            return jsonify({'success': False, 'error': 'Favorit tidak ditemukan'}), 404
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'success': True,
            'message': 'Catatan berhasil diperbarui'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/favorit-clear-all', methods=['DELETE'])
def api_favorit_clear_all():
    """
    API endpoint untuk menghapus semua favorit user
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        cur = mysql.connection.cursor()
        
        # Delete all favorites for the user
        cur.execute("""
            DELETE FROM favorit_aset 
            WHERE user_id = %s
        """, [session['user_id']])
        
        deleted_count = cur.rowcount
        mysql.connection.commit()
        cur.close()
        
        return jsonify({
            'success': True,
            'message': f'{deleted_count} favorit berhasil dihapus'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/favorit-status')
def api_favorit_status():
    """
    API endpoint untuk mendapatkan status favorit (IDs yang difavoritkan)
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        cur = mysql.connection.cursor()
        
        # Get all favorited aset IDs for the user
        cur.execute("""
            SELECT aset_id FROM favorit_aset 
            WHERE user_id = %s
        """, [session['user_id']])
        
        favorited_ids = [row[0] for row in cur.fetchall()]
        cur.close()
        
        return jsonify({
            'success': True,
            'favorited_ids': favorited_ids
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/favorit-count')
def api_favorit_count():
    """
    API endpoint untuk mendapatkan jumlah favorit user
    """
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        cur = mysql.connection.cursor()
        
        # Count favorites for the user
        cur.execute("""
            SELECT COUNT(*) FROM favorit_aset 
            WHERE user_id = %s
        """, [session['user_id']])
        
        count = cur.fetchone()[0]
        cur.close()
        
        return jsonify({
            'success': True,
            'count': count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
