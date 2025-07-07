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
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validasi input
        if not current_password or not new_password or not confirm_password:
            flash('Semua field wajib diisi.', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Password baru dan konfirmasi password tidak cocok.', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 8:
            flash('Password baru minimal 8 karakter.', 'error')
            return render_template('change_password.html')
        
        try:
            cur = mysql.connection.cursor()
            
            # Ambil password lama dari database
            cur.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
            user_data = cur.fetchone()
            
            if not user_data:
                flash('User tidak ditemukan.', 'error')
                cur.close()
                return render_template('change_password.html')
            
            # Verifikasi password lama
            if not check_password_hash(user_data[0], current_password):
                flash('Password saat ini salah.', 'error')
                cur.close()
                return render_template('change_password.html')
            
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
            flash(f'Terjadi kesalahan: {str(e)}', 'error')
            return render_template('change_password.html')
    
    return render_template('change_password.html')
