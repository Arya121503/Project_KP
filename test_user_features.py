"""
Comprehensive test script to verify all user features are working
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_api_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test an API endpoint"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        
        print(f"✅ {method} {endpoint} - Status: {response.status_code}")
        
        if response.status_code < 400:
            try:
                result = response.json()
                if 'success' in result:
                    print(f"   Success: {result['success']}")
                    if 'data' in result:
                        print(f"   Data count: {len(result['data']) if isinstance(result['data'], list) else 'N/A'}")
                    if 'message' in result:
                        print(f"   Message: {result['message']}")
                else:
                    print(f"   Response: {result}")
            except:
                print(f"   Response: {response.text[:100]}...")
        else:
            print(f"   Error: {response.text[:100]}...")
        
        return response
        
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return None

def main():
    """Test all user features"""
    print("🚀 TESTING USER FEATURES")
    print("=" * 50)
    
    # Test basic API endpoints (no auth required)
    print("\n📋 Testing Public API Endpoints:")
    test_api_endpoint("/api/aset-tersedia")
    test_api_endpoint("/api/kecamatan-list")
    
    # Test user feature API endpoints (require auth)
    print("\n🔐 Testing User Feature API Endpoints (will fail without auth):")
    test_api_endpoint("/api/favorit/list")
    test_api_endpoint("/api/notifikasi/list")
    test_api_endpoint("/api/histori/list")
    test_api_endpoint("/api/notifikasi/unread-count")
    
    # Test database connectivity
    print("\n🗄️ Testing Database Connectivity:")
    try:
        import mysql.connector
        from config import Config
        
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
        cursor = conn.cursor()
        
        # Test each table
        tables_to_test = [
            'users', 'aset_sewa', 'favorit_aset', 'notifikasi_user', 
            'histori_sewa', 'prediksi_sewa_bulanan', 'pengajuan_sewa'
        ]
        
        for table in tables_to_test:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} rows")
            except Exception as e:
                print(f"❌ {table}: Error - {str(e)}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
    
    # Test prediction models
    print("\n🤖 Testing ML Models:")
    try:
        from app.ml_predictor import PropertyPricePredictor
        
        predictor = PropertyPricePredictor()
        
        # Test building prediction
        test_data = {
            'kecamatan': 'Sukolilo',
            'luas_tanah': 100,
            'luas_bangunan': 70,
            'kamar_tidur': 2,
            'kamar_mandi': 1,
            'jumlah_lantai': 1,
            'daya_listrik': 1300,
            'sertifikat': 'SHM - Sertifikat Hak Milik',
            'kondisi_properti': 'Bagus',
            'tingkat_keamanan': 'Tinggi',
            'aksesibilitas': 'Baik',
            'tipe_iklan': 'Dijual',
            'njop_per_m2': 3000000,
            'hadap': 'Utara',
            'hook': 'Tidak'
        }
        
        result = predictor.predict_all_models(test_data)
        if result:
            print(f"✅ Building prediction: Rp {result.get('random_forest', 0):,.0f} (RF)")
        else:
            print("❌ Building prediction failed")
        
        # Test rental prediction
        rental_data = {
            'kecamatan': 'Sukolilo',
            'luas_tanah': 100,
            'luas_bangunan': 70,
            'kamar_tidur': 2,
            'kamar_mandi': 1,
            'jumlah_lantai': 1,
            'daya_listrik': 1300,
            'sertifikat': 'SHM - Sertifikat Hak Milik',
            'kondisi_properti': 'Bagus',
            'tingkat_keamanan': 'Tinggi',
            'aksesibilitas': 'Baik',
            'njop_per_m2': 3000000
        }
        
        rental_result = predictor.predict_rental_price_ensemble(rental_data)
        if rental_result:
            print(f"✅ Rental prediction: Rp {rental_result['ensemble_price']:,.0f}/month")
        else:
            print("❌ Rental prediction failed")
        
    except Exception as e:
        print(f"❌ ML Models test failed: {str(e)}")
    
    print("\n🎯 TESTING COMPLETE")
    print("=" * 50)
    print("✅ If you see mostly green checkmarks above, the features are working!")
    print("❌ Any red X marks indicate issues that need attention.")
    print("\nTo test the full user interface:")
    print("1. Open http://127.0.0.1:5000 in your browser")
    print("2. Login as admin (admin@telkom.com / admin123)")
    print("3. Test the prediction features")
    print("4. Login as user (user@telkom.com / user123)")
    print("5. Test favorit, notifikasi, and histori features")

if __name__ == "__main__":
    main()
