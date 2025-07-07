-- Script untuk menambahkan kolom profil user
-- Tambahkan kolom jika belum ada

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS company VARCHAR(255),
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Update existing records jika diperlukan
UPDATE users SET 
    phone = COALESCE(phone, ''),
    company = COALESCE(company, ''),
    address = COALESCE(address, '')
WHERE phone IS NULL OR company IS NULL OR address IS NULL;
