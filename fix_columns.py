from app import create_app
app = create_app()
from app import mysql
with app.app_context():
    cur = mysql.connection.cursor()
    try:
        # Add the missing column to the prediksi_properti_bangunan_tanah table
        cur.execute('DESCRIBE prediksi_properti_bangunan_tanah')
        columns = [row[0] for row in cur.fetchall()]
        print('Current columns in prediksi_properti_bangunan_tanah:')
        for col in columns:
            print(f'- {col}')
            
        # Check if jumlah_kamar_tidur exists
        if 'jumlah_kamar_tidur' not in columns and 'kamar_tidur' in columns:
            print('\nRenaming kamar_tidur to jumlah_kamar_tidur...')
            cur.execute('ALTER TABLE prediksi_properti_bangunan_tanah CHANGE kamar_tidur jumlah_kamar_tidur INT')
            mysql.connection.commit()
            print(' Column renamed successfully')
        elif 'jumlah_kamar_tidur' not in columns and 'kamar_tidur' not in columns:
            print('\nAdding jumlah_kamar_tidur column...')
            cur.execute('ALTER TABLE prediksi_properti_bangunan_tanah ADD COLUMN jumlah_kamar_tidur INT AFTER luas_bangunan_m2')
            mysql.connection.commit()
            print(' Column added successfully')
        else:
            print('\njumlah_kamar_tidur already exists')
        
        # Check if jumlah_kamar_mandi exists
        if 'jumlah_kamar_mandi' not in columns and 'kamar_mandi' in columns:
            print('\nRenaming kamar_mandi to jumlah_kamar_mandi...')
            cur.execute('ALTER TABLE prediksi_properti_bangunan_tanah CHANGE kamar_mandi jumlah_kamar_mandi INT')
            mysql.connection.commit()
            print(' Column renamed successfully')
        elif 'jumlah_kamar_mandi' not in columns and 'kamar_mandi' not in columns:
            print('\nAdding jumlah_kamar_mandi column...')
            cur.execute('ALTER TABLE prediksi_properti_bangunan_tanah ADD COLUMN jumlah_kamar_mandi INT AFTER jumlah_kamar_tidur')
            mysql.connection.commit()
            print(' Column added successfully')
        else:
            print('\njumlah_kamar_mandi already exists')
        
        print('\nVerifying updated columns...')
        cur.execute('DESCRIBE prediksi_properti_bangunan_tanah')
        updated_columns = [row[0] for row in cur.fetchall()]
        print('Updated columns in prediksi_properti_bangunan_tanah:')
        for col in updated_columns:
            print(f'- {col}')
            
    except Exception as e:
        print(f'Error: {str(e)}')
    
    cur.close()
