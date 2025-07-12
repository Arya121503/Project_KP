-- SQL untuk membuat tabel prediksi sewa bulanan
CREATE TABLE IF NOT EXISTS prediksi_sewa_bulanan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kecamatan VARCHAR(100) NOT NULL,
    kelurahan VARCHAR(100),
    luas_tanah_m2 INT,
    luas_bangunan_m2 INT,
    kamar_tidur INT,
    kamar_mandi INT,
    jumlah_lantai INT,
    tahun_dibangun INT,
    daya_listrik INT,
    sertifikat VARCHAR(100),
    kondisi_properti VARCHAR(100),
    tingkat_keamanan VARCHAR(50),
    aksesibilitas VARCHAR(50),
    tipe_iklan VARCHAR(50),
    NJOP_Rp_per_m2 DECIMAL(15,2),
    harga_sewa_rf DECIMAL(15,2),
    harga_sewa_xgb DECIMAL(15,2),
    harga_sewa_catboost DECIMAL(15,2),
    harga_sewa_ensemble DECIMAL(15,2),
    confidence_score DECIMAL(5,4),
    model_predictor VARCHAR(50) DEFAULT 'ensemble',
    property_type VARCHAR(20) DEFAULT 'bangunan',
    status_kirim_user ENUM('pending', 'sent') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_kecamatan (kecamatan),
    INDEX idx_status (status_kirim_user),
    INDEX idx_property_type (property_type),
    INDEX idx_created_at (created_at)
);

-- Tambahkan kolom untuk menyimpan informasi tambahan jika diperlukan
ALTER TABLE prediksi_sewa_bulanan 
ADD COLUMN IF NOT EXISTS alamat TEXT,
ADD COLUMN IF NOT EXISTS deskripsi TEXT,
ADD COLUMN IF NOT EXISTS foto_url VARCHAR(255);

-- Update existing records if any
UPDATE prediksi_sewa_bulanan 
SET alamat = CONCAT(kecamatan, ', Surabaya') 
WHERE alamat IS NULL OR alamat = '';
