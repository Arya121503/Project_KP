from app import create_app
app = create_app()
from app import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    try:
        # Check current columns
        cur.execute("SHOW COLUMNS FROM prediksi_properti_bangunan_tanah")
        columns = [column[0] for column in cur.fetchall()]
        print("Current columns:", columns)
        
        # Add updated_at if it doesn't exist
        if "updated_at" not in columns:
            print("Adding updated_at column...")
            cur.execute("ALTER TABLE prediksi_properti_bangunan_tanah ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            mysql.connection.commit()
            print("updated_at column added successfully")
        else:
            print("updated_at column already exists")
            
        # Check for any other missing columns that might be needed
        missing_columns = []
        expected_columns = [
            "harga_prediksi_tanah",
            "harga_prediksi_bangunan",
            "rasio_bangunan_tanah",
            "umur_bangunan",
            "tahun_dibangun"
        ]
        
        for col in expected_columns:
            if col not in columns:
                missing_columns.append(col)
        
        # Add any missing columns
        for col in missing_columns:
            print(f"Adding {col} column...")
            data_type = "DECIMAL(18,2)" if "harga" in col or "rasio" in col else "INT"
            cur.execute(f"ALTER TABLE prediksi_properti_bangunan_tanah ADD COLUMN {col} {data_type}")
            print(f"{col} column added successfully")
            
        mysql.connection.commit()
            
        # Check updated columns
        cur.execute("SHOW COLUMNS FROM prediksi_properti_bangunan_tanah")
        updated_columns = [column[0] for column in cur.fetchall()]
        print("\nUpdated columns:", updated_columns)
    except Exception as e:
        print(f"Error: {str(e)}")
    cur.close()
