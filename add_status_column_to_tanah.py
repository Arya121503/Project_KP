#!/usr/bin/env python3
"""
Migration script untuk menambahkan kolom status_kirim_user ke tabel prediksi_properti_tanah
"""

from app import create_app, mysql

def add_status_column_to_tanah():
    """Add status_kirim_user column to prediksi_properti_tanah table"""
    app = create_app()
    
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Check if column already exists
            cur.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'prediksi_properti_tanah' 
                AND column_name = 'status_kirim_user'
            """)
            
            if cur.fetchone()[0] == 0:
                # Add the column
                cur.execute("""
                    ALTER TABLE prediksi_properti_tanah 
                    ADD COLUMN status_kirim_user ENUM('pending', 'sent') DEFAULT 'pending'
                """)
                mysql.connection.commit()
                print("✅ Added status_kirim_user column to prediksi_properti_tanah table")
            else:
                print("ℹ️  Column status_kirim_user already exists in prediksi_properti_tanah table")
            
            cur.close()
            
        except Exception as e:
            print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_status_column_to_tanah()
