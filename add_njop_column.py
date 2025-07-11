from app import create_app
app = create_app()
from app import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    try:
        # Check if the column exists
        cur.execute("SHOW COLUMNS FROM prediksi_properti_bangunan_tanah")
        columns = [column[0] for column in cur.fetchall()]
        print("Current columns in prediksi_properti_bangunan_tanah:")
        print(columns)
        
        # Add njop_per_m2 if it doesn't exist
        if "njop_per_m2" not in columns:
            print("\nAdding njop_per_m2 column...")
            cur.execute("ALTER TABLE prediksi_properti_bangunan_tanah ADD COLUMN njop_per_m2 DECIMAL(18,2) AFTER tipe_iklan")
            mysql.connection.commit()
            print("✅ njop_per_m2 column added successfully")
            
            # Verify the column was added
            cur.execute("SHOW COLUMNS FROM prediksi_properti_bangunan_tanah")
            updated_columns = [column[0] for column in cur.fetchall()]
            if "njop_per_m2" in updated_columns:
                print("✅ Verified column was added successfully")
            else:
                print("❌ Column was not added correctly")
        else:
            print("\nnjop_per_m2 column already exists")
        
        # Check for any potential missing columns related to property value calculations
        missing_columns = []
        expected_columns = [
            "njop_tanah_per_m2",
            "harga_per_m2_tanah"
        ]
        
        for col in expected_columns:
            if col not in columns:
                missing_columns.append(col)
                
        # Add any other missing columns
        for col in missing_columns:
            print(f"\nAdding {col} column...")
            cur.execute(f"ALTER TABLE prediksi_properti_bangunan_tanah ADD COLUMN {col} DECIMAL(18,2)")
            mysql.connection.commit()
            print(f"✅ {col} column added successfully")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    
    cur.close()
