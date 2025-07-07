# 🚀 Quick Start Guide - Telkom Property Prediction System

## Langkah-langkah Setup dan Menjalankan Aplikasi

### Prasyarat
1. **Python 3.8+** - Download dari [python.org](https://python.org)
2. **MySQL Server** - Bisa menggunakan XAMPP, MySQL Workbench, atau Docker
3. **Git** (opsional) - Untuk clone repository

### Opsi 1: Quick Start (Termudah) 🎯

1. **Jalankan script otomatis:**
   ```cmd
   double-click start.bat
   ```
   atau
   ```cmd
   start.bat
   ```

### Opsi 2: Manual Setup 🔧

1. **Setup MySQL Server**
   - **XAMPP**: Buka XAMPP Control Panel → Start Apache & MySQL
   - **MySQL Service**: Buka Command Prompt as Administrator → `net start mysql`
   - **Docker**: `docker run --name mysql -p 3307:3306 -e MYSQL_ROOT_PASSWORD=Arya151203F. -d mysql:8.0`

2. **Buat Virtual Environment**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Setup Database**
   ```cmd
   python setup_database.py
   ```

5. **Jalankan Aplikasi**
   ```cmd
   python run.py
   ```
   atau
   ```cmd
   python launcher.py
   ```

### Akses Aplikasi 🌐

- **URL**: http://localhost:5000
- **Admin Login**:
  - Email: `admin@telkom.co.id`
  - Password: `admin123`

### Troubleshooting ⚡

#### Error: MySQL Connection Failed
```
❌ MySQL server tidak berjalan atau tidak dapat diakses
```
**Solusi**:
1. Pastikan MySQL server berjalan di port 3307
2. Check file `config.py` untuk konfigurasi database
3. Update password MySQL di file `.env` jika berbeda

#### Error: Module Not Found
```
❌ Package yang belum terinstall: flask, pandas, etc.
```
**Solusi**:
```cmd
pip install -r requirements.txt
```

#### Error: Database/Table Not Found
```
❌ Tabel database yang belum ada: users, prediksi_properti_tanah
```
**Solusi**:
```cmd
python setup_database.py
```

#### Error: Model ML Not Found
```
⚠️ Model ML yang tidak ditemukan: catboost_model.pkl
```
**Solusi**: Aplikasi tetap bisa berjalan, tapi fitur prediksi tidak akan bekerja. Model bisa ditraining ulang melalui notebook di folder `notebooks/`.

### Struktur Proyek 📁

```
Project_KP/
├── run.py              # Entry point utama
├── launcher.py         # Setup checker & launcher
├── setup_database.py   # Database setup script
├── start.bat          # Quick start script (Windows)
├── config.py          # Konfigurasi aplikasi
├── requirements.txt   # Python dependencies
├── .env              # Environment variables
├── app/              # Main application
├── ml_model/         # Trained ML models
├── data/            # Datasets
└── templates/       # HTML templates
```

### Konfigurasi Database 🗄️

Edit file `config.py` atau `.env` untuk mengubah konfigurasi:

```python
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3307
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'Arya151203F.'
MYSQL_DB = 'db_kp'
```

### Fitur Utama 🎉

1. **Dashboard Admin**: Manajemen data, visualisasi, export
2. **Dashboard User**: Prediksi harga properti
3. **Machine Learning**: CatBoost, XGBoost, Random Forest
4. **Database**: MySQL untuk penyimpanan data
5. **Web Interface**: Bootstrap, Chart.js, responsive design

### Support 💬

Jika ada masalah, cek:
1. Apakah MySQL server berjalan?
2. Apakah semua dependencies terinstall?
3. Apakah database sudah disetup?
4. Apakah port 5000 tersedia?

**Happy Coding!** 🚀
