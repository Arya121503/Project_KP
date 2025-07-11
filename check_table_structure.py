from app import create_app
app = create_app()
from app import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    try:
        # Check the table structure
        cur.execute("DESCRIBE prediksi_properti_bangunan_tanah")
        columns = cur.fetchall()
        print("Columns in prediksi_properti_bangunan_tanah:")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        cur.close()
