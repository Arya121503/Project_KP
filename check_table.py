from app import create_app
app = create_app()
from app import mysql
with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute('DESCRIBE pengajuan_sewa')
    results = cur.fetchall()
    print('Columns in pengajuan_sewa:')
    for row in results: print(row)
    cur.close()
