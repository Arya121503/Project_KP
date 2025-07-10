from app import create_app
app = create_app()
from app import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    try:
        print("Updating newly added columns with default values...")
        
        # Update njop_per_m2 with a reasonable default value
        cur.execute("UPDATE prediksi_properti_bangunan_tanah SET njop_per_m2 = 1000000 WHERE njop_per_m2 IS NULL")
        
        # Update njop_tanah_per_m2 with a reasonable default value
        cur.execute("UPDATE prediksi_properti_bangunan_tanah SET njop_tanah_per_m2 = 1000000 WHERE njop_tanah_per_m2 IS NULL")
        
        # Calculate and update harga_per_m2_tanah based on njop_tanah_per_m2
        cur.execute("UPDATE prediksi_properti_bangunan_tanah SET harga_per_m2_tanah = njop_tanah_per_m2 WHERE harga_per_m2_tanah IS NULL")
        
        mysql.connection.commit()
        print("✅ Columns updated with default values")
        
        # Count rows updated
        cur.execute("SELECT COUNT(*) FROM prediksi_properti_bangunan_tanah WHERE njop_per_m2 IS NOT NULL")
        count = cur.fetchone()[0]
        print(f"Updated {count} records with default values")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    cur.close()
