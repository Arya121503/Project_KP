"""
Script untuk membersihkan database dari data Prajuritkulon yang bukan bagian dari Surabaya
"""

import mysql.connector
from config import Config
import os
import sys

def connect_to_database():
    """Koneksi ke database"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def clean_prajuritkulon_data():
    """Hapus semua data yang mengandung Prajuritkulon dari database"""
    connection = connect_to_database()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Periksa tabel yang mungkin mengandung data Prajuritkulon
        tables_to_check = [
            'asset_tanah',
            'asset_bangunan', 
            'prediksi_properti_tanah',
            'prediksi_properti_bangunan_tanah'
        ]
        
        total_deleted = 0
        
        for table in tables_to_check:
            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if cursor.fetchone():
                # Check for Prajuritkulon data
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE kecamatan LIKE '%prajurit%'")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"Found {count} records containing 'prajurit' in table {table}")
                    
                    # Delete the records
                    cursor.execute(f"DELETE FROM {table} WHERE kecamatan LIKE '%prajurit%'")
                    deleted = cursor.rowcount
                    total_deleted += deleted
                    print(f"Deleted {deleted} records from table {table}")
                else:
                    print(f"No 'prajurit' records found in table {table}")
        
        # Commit changes
        connection.commit()
        print(f"Total records deleted: {total_deleted}")
        
        return True
        
    except Exception as e:
        print(f"Error cleaning database: {e}")
        connection.rollback()
        return False
    finally:
        if connection:
            connection.close()

def reload_clean_data():
    """Reload data dari CSV yang sudah dibersihkan"""
    print("Reloading data from cleaned CSV...")
    
    # Import data processor
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.data_processor import AssetDataProcessor
    
    try:
        # Load data from cleaned CSV
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'dataset_tanah_njop_surabaya_sertifikat.csv')
        processor = AssetDataProcessor(csv_path)
        
        # Verify no Prajuritkulon data exists
        if processor.df is not None:
            prajurit_count = processor.df[processor.df['kecamatan'].str.contains('prajurit', case=False, na=False)].shape[0]
            if prajurit_count > 0:
                print(f"WARNING: Found {prajurit_count} Prajuritkulon records in CSV!")
                return False
            else:
                print("CSV data is clean - no Prajuritkulon records found")
                return True
        else:
            print("Failed to load CSV data")
            return False
            
    except Exception as e:
        print(f"Error reloading data: {e}")
        return False

if __name__ == "__main__":
    print("Starting database cleanup for Prajuritkulon data...")
    
    # Step 1: Clean database
    if clean_prajuritkulon_data():
        print("Database cleanup completed successfully")
        
        # Step 2: Verify CSV data is clean
        if reload_clean_data():
            print("Data verification completed successfully")
            print("All Prajuritkulon data has been removed from the system")
        else:
            print("Data verification failed - please check CSV file")
    else:
        print("Database cleanup failed")
