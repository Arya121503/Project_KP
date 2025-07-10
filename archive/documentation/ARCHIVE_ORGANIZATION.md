# Archive Organization

This archive contains all files that are no longer actively used in the main application but are kept for historical reference and potential future use.

## Directory Structure

### `cleanup_scripts_final/`
Contains all cleanup and testing scripts that were used during development but are no longer needed for production:

- `add_tenggilis_mejoyo.py` - Script untuk menambahkan data Tenggilis Mejoyo
- `analyze_building_issues.py` - Analisis masalah data bangunan
- `check_building_data.py` - Script pemeriksaan data bangunan
- `check_database.py` - Script pemeriksaan database
- `check_kecamatan.py` - Script pemeriksaan data kecamatan
- `check_models.py` - Script pemeriksaan model ML
- `cleanup_prajuritkulon.py` - Script cleanup data Prajuritkulon
- `final_test_xgboost.py` - Testing XGBoost model
- `final_verification.py` - Verifikasi final data
- `fix_building_data.py` - Script perbaikan data bangunan
- `test_xgboost_retrain.py` - Testing retrain XGBoost
- `update_models.py` - Script update model
- `verify_cleanup.py` - Verifikasi cleanup
- `test_pagination.html` - File test pagination (empty)
- `Makefile` - Makefile (empty)

### `documentation/`
Contains project documentation files:

- `BUILDING_DATA_SAFETY_REPORT.md` - Laporan keamanan data bangunan
- `CLEANUP_DOCUMENTATION.md` - Dokumentasi cleanup
- `PROJECT_CLEANUP_SUMMARY.md` - Ringkasan cleanup project

### `scripts_cleanup/` (existing)
Contains older cleanup scripts from previous cleanup phases.

### `old_models/` (existing)
Contains backup of old machine learning models.

### `temp_files/` (existing)
Contains temporary files used during development.

## Files Still in Active Use

The following files remain in the main directory as they are actively used:

- `run.py` - Main application runner
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies
- `README.md` - Main project documentation
- `CHANGELOG.md` - Project changelog
- `app/` - Main application directory
- `data/` - Data files directory
- `docs/` - Active documentation
- `instance/` - Instance configuration
- `ml_model/` - Active ML models
- `notebooks/` - Jupyter notebooks

## Cleanup Date
Files archived on: July 8, 2025

## Notes
- All archived files have been tested and confirmed to be no longer needed for production
- Files can be restored if needed for future reference
- __pycache__ directories have been removed to clean up compiled Python files
