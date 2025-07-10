# ARCHIVE DIRECTORY - PROJECT KP

## Purpose
Folder ini berisi file-file lama, backup, dan script yang sudah tidak digunakan dalam aplikasi utama tetapi disimpan untuk referensi historis dan troubleshooting.

## Contents Overview

### 📁 cleanup_scripts_final/
Script-script yang digunakan untuk membersihkan data dan memperbaiki masalah:
- `analyze_building_issues.py` - Analisis masalah data bangunan
- `check_*.py` - Script pengecekan database dan model
- `cleanup_*.py` - Script pembersihan data
- `final_*.py` - Script final verification
- `fix_*.py` - Script perbaikan data
- `test_*.py` - Script testing
- `verify_*.py` - Script verifikasi

### 📁 documentation/
Dokumentasi lama dari proses development:
- `CLEANUP_DOCUMENTATION.md` - Dokumentasi proses cleanup
- `BUILDING_DATA_SAFETY_REPORT.md` - Laporan keamanan data
- `PROJECT_CLEANUP_SUMMARY.md` - Summary cleanup project

### 📄 Template Backups
- `total_properti_old.html` - Template lama halaman total properti sebelum rombak ulang

### 📄 Database Scripts
- `create_prediction_tables.py` - Script pembuatan tabel prediksi
- `setup_database.py` - Script setup database awal

### 📄 Test & Debug Files
- `test_api.html` - Test page untuk API
- `test_api_direct.py` - Test script API langsung
- `test_database_connection.py` - Test koneksi database
- `debug_api.py` - Debug script untuk API

### 📄 Documentation Files
- Various `*_FIX.md` files - Dokumentasi perbaikan dan troubleshooting

## Important Notes

⚠️ **Jangan hapus folder ini!** File-file ini diperlukan untuk:
1. Reference jika ada masalah di masa depan
2. Rollback jika diperlukan
3. Historical tracking perubahan
4. Debugging dan troubleshooting

## Project Status
Aplikasi utama sudah bersih dan semua fitur berfungsi optimal. File-file di sini adalah backup dan historical record.
- `final_test_xgboost.py` - Script untuk validasi final XGBoost
- `update_models.py` - Script untuk update model setelah retraining
- `verify_cleanup.py` - Script untuk verifikasi cleanup data

### `old_models/`
Backup model lama dan folder backup:
- `backup_old_models/` - Backup model sebelum retraining
- `backup/` - Folder backup dari ml_model

### `temp_files/`
File temporary dan cache:
- `__pycache__/` - Python cache dari root directory
- `app_pycache/` - Python cache dari app directory
- `xgboost_feature_names.txt` - File temporary untuk debugging features

### Files dari Cleanup Sebelumnya
- `app.db` - Database lama
- `catboost_info/` - Info training CatBoost
- `create_prediction_tables.py` - Script pembuatan tabel prediksi
- `Dataset_Bangunan_Surabaya.csv` - Dataset lama
- `setup_database.py` - Script setup database

## Status Archive

**Tanggal Archive**: 2025-07-08
**Alasan**: Membersihkan struktur proyek setelah selesai cleanup data dan retraining model
**Status**: File-file ini tidak diperlukan lagi untuk operasional sistem

## Catatan

Semua file dalam archive ini sudah tidak digunakan dalam sistem aktif, tetapi disimpan untuk:
1. Referensi historis
2. Audit trail proses cleanup
3. Backup untuk keamanan
4. Dokumentasi proses pengembangan

**Jangan hapus folder ini** kecuali sudah yakin tidak diperlukan untuk audit atau referensi.
