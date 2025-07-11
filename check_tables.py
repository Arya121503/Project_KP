from app import create_app
app = create_app()
from app import mysql
with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute('SHOW TABLES')
    results = cur.fetchall()
    print('Tables in database:')
    for row in results:
        print(row[0])
        
    # Check prediksi_properti_tanah table
    try:
        cur.execute('DESCRIBE prediksi_properti_tanah')
        results = cur.fetchall()
        print('\nColumns in prediksi_properti_tanah:')
        for row in results:
            print(row[0])
    except Exception as e:
        print(f'Error: {e}')
        
    # Check prediksi_properti_bangunan_tanah table
    try:
        cur.execute('DESCRIBE prediksi_properti_bangunan_tanah')
        results = cur.fetchall()
        print('\nColumns in prediksi_properti_bangunan_tanah:')
        for row in results:
            print(row[0])
    except Exception as e:
        print(f'Error: {e}')
        
    cur.close()
