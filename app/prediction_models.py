"""
Model untuk tabel prediksi properti
"""

from app import mysql

class PrediksiPropertiTanah:
    def __init__(self, id=None, kecamatan=None, kelurahan=None, luas_tanah_m2=None, 
                 njop_tanah_per_m2=None, zona_nilai_tanah=None, kelas_tanah=None,
                 jenis_sertifikat=None, harga_prediksi_tanah=None, harga_per_m2_tanah=None,
                 model_predictor=None, confidence_score=None):
        self.id = id
        self.kecamatan = kecamatan
        self.kelurahan = kelurahan
        self.luas_tanah_m2 = luas_tanah_m2
        self.njop_tanah_per_m2 = njop_tanah_per_m2
        self.zona_nilai_tanah = zona_nilai_tanah
        self.kelas_tanah = kelas_tanah
        self.jenis_sertifikat = jenis_sertifikat
        self.harga_prediksi_tanah = harga_prediksi_tanah
        self.harga_per_m2_tanah = harga_per_m2_tanah
        self.model_predictor = model_predictor
        self.confidence_score = confidence_score

    @staticmethod
    def get_all(limit=100, offset=0):
        """Ambil semua data prediksi tanah dengan pagination"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, kecamatan, kelurahan, luas_tanah_m2, njop_tanah_per_m2, 
                       zona_nilai_tanah, kelas_tanah, jenis_sertifikat, 
                       harga_prediksi_tanah, harga_per_m2_tanah, model_predictor, 
                       confidence_score, created_at
                FROM prediksi_properti_tanah 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting prediksi tanah: {e}")
            return []

    @staticmethod
    def search_by_kecamatan(kecamatan, limit=50):
        """Cari prediksi berdasarkan kecamatan"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, kecamatan, kelurahan, luas_tanah_m2, njop_tanah_per_m2, 
                       zona_nilai_tanah, kelas_tanah, jenis_sertifikat, 
                       harga_prediksi_tanah, harga_per_m2_tanah, model_predictor, 
                       confidence_score, created_at
                FROM prediksi_properti_tanah 
                WHERE kecamatan LIKE %s
                ORDER BY harga_prediksi_tanah DESC 
                LIMIT %s
            """, (f'%{kecamatan}%', limit))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error searching prediksi tanah: {e}")
            return []

    @staticmethod
    def get_statistics():
        """Ambil statistik prediksi tanah (excluding Prajuritkulon)"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    AVG(harga_prediksi_tanah) as avg_price,
                    MIN(harga_prediksi_tanah) as min_price,
                    MAX(harga_prediksi_tanah) as max_price,
                    AVG(harga_per_m2_tanah) as avg_price_per_m2,
                    COUNT(DISTINCT kecamatan) as total_kecamatan
                FROM prediksi_properti_tanah
                WHERE kecamatan NOT LIKE '%prajurit%'
            """)
            result = cur.fetchone()
            cur.close()
            return result
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return None

    @staticmethod
    def get_location_analysis():
        """Ambil analisis per lokasi untuk data tanah (excluding Prajuritkulon)"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    kecamatan,
                    COUNT(*) as total_properties,
                    AVG(harga_prediksi_tanah) as avg_price,
                    MIN(harga_prediksi_tanah) as min_price,
                    MAX(harga_prediksi_tanah) as max_price,
                    SUM(harga_prediksi_tanah) as total_value,
                    AVG(luas_tanah_m2) as avg_land_area,
                    COUNT(DISTINCT jenis_sertifikat) as certificate_types
                FROM prediksi_properti_tanah 
                WHERE kecamatan NOT LIKE '%prajurit%'
                GROUP BY kecamatan
                ORDER BY avg_price DESC
            """)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting location analysis: {e}")
            return []

    @staticmethod
    def get_certificate_distribution():
        """Ambil distribusi sertifikat (excluding Prajuritkulon)"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    jenis_sertifikat,
                    COUNT(*) as count,
                    AVG(harga_prediksi_tanah) as avg_price,
                    MIN(harga_prediksi_tanah) as min_price,
                    MAX(harga_prediksi_tanah) as max_price
                FROM prediksi_properti_tanah 
                WHERE jenis_sertifikat IS NOT NULL AND jenis_sertifikat != ''
                AND kecamatan NOT LIKE '%prajurit%'
                GROUP BY jenis_sertifikat
                ORDER BY count DESC
            """)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting certificate distribution: {e}")
            return []

    @staticmethod
    def get_all_with_real_prices(limit=100, offset=0):
        """Ambil semua data prediksi tanah dengan harga real (jika ada) dengan pagination"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT p.id, p.kecamatan, p.kelurahan, p.luas_tanah_m2, p.njop_tanah_per_m2, 
                       p.zona_nilai_tanah, p.kelas_tanah, p.jenis_sertifikat, 
                       p.harga_prediksi_tanah as harga_display, 
                       p.harga_prediksi_tanah, p.harga_per_m2_tanah, p.model_predictor, 
                       p.confidence_score, p.created_at,
                       FALSE as has_real_price
                FROM prediksi_properti_tanah p
                ORDER BY p.created_at DESC 
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting prediksi tanah with real prices: {e}")
            return []

class PrediksiPropertiBangunanTanah:
    def __init__(self, id=None, kecamatan=None, luas_tanah_m2=None, luas_bangunan_m2=None,
                 jumlah_kamar_tidur=None, jumlah_kamar_mandi=None, jumlah_lantai=None,
                 tahun_dibangun=None, daya_listrik=None, sertifikat=None, kondisi_properti=None,
                 tingkat_keamanan=None, aksesibilitas=None, tipe_iklan=None, njop_per_m2=None,
                 rasio_bangunan_tanah=None, umur_bangunan=None, harga_prediksi_total=None,
                 harga_prediksi_tanah=None, harga_prediksi_bangunan=None, harga_per_m2_bangunan=None,
                 model_predictor=None, confidence_score=None):
        self.id = id
        self.kecamatan = kecamatan
        self.luas_tanah_m2 = luas_tanah_m2
        self.luas_bangunan_m2 = luas_bangunan_m2
        self.jumlah_kamar_tidur = jumlah_kamar_tidur
        self.jumlah_kamar_mandi = jumlah_kamar_mandi
        self.jumlah_lantai = jumlah_lantai
        self.tahun_dibangun = tahun_dibangun
        self.daya_listrik = daya_listrik
        self.sertifikat = sertifikat
        self.kondisi_properti = kondisi_properti
        self.tingkat_keamanan = tingkat_keamanan
        self.aksesibilitas = aksesibilitas
        self.tipe_iklan = tipe_iklan
        self.njop_per_m2 = njop_per_m2
        self.rasio_bangunan_tanah = rasio_bangunan_tanah
        self.umur_bangunan = umur_bangunan
        self.harga_prediksi_total = harga_prediksi_total
        self.harga_prediksi_tanah = harga_prediksi_tanah
        self.harga_prediksi_bangunan = harga_prediksi_bangunan
        self.harga_per_m2_bangunan = harga_per_m2_bangunan
        self.model_predictor = model_predictor
        self.confidence_score = confidence_score

    @staticmethod
    def get_all(limit=100, offset=0):
        """Ambil semua data prediksi bangunan+tanah dengan pagination"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, kecamatan, luas_tanah_m2, luas_bangunan_m2, jumlah_kamar_tidur,
                       jumlah_kamar_mandi, jumlah_lantai, tahun_dibangun, daya_listrik,
                       sertifikat, kondisi_properti, tingkat_keamanan, aksesibilitas,
                       tipe_iklan, njop_per_m2, rasio_bangunan_tanah, umur_bangunan,
                       harga_prediksi_total, harga_prediksi_tanah, harga_prediksi_bangunan,
                       harga_per_m2_bangunan, model_predictor, confidence_score, created_at
                FROM prediksi_properti_bangunan_tanah 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting prediksi bangunan tanah: {e}")
            return []

    @staticmethod
    def search_by_criteria(kecamatan=None, min_luas_bangunan=None, max_luas_bangunan=None,
                          kamar_tidur=None, min_harga=None, max_harga=None, limit=50):
        """Cari prediksi berdasarkan kriteria tertentu"""
        try:
            cur = mysql.connection.cursor()
            
            where_conditions = []
            params = []
            
            if kecamatan:
                where_conditions.append("kecamatan LIKE %s")
                params.append(f'%{kecamatan}%')
            
            if min_luas_bangunan:
                where_conditions.append("luas_bangunan_m2 >= %s")
                params.append(min_luas_bangunan)
            
            if max_luas_bangunan:
                where_conditions.append("luas_bangunan_m2 <= %s")
                params.append(max_luas_bangunan)
            
            if kamar_tidur:
                where_conditions.append("jumlah_kamar_tidur = %s")
                params.append(kamar_tidur)
            
            if min_harga:
                where_conditions.append("harga_prediksi_total >= %s")
                params.append(min_harga)
            
            if max_harga:
                where_conditions.append("harga_prediksi_total <= %s")
                params.append(max_harga)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            query = f"""
                SELECT id, kecamatan, luas_tanah_m2, luas_bangunan_m2, jumlah_kamar_tidur,
                       jumlah_kamar_mandi, jumlah_lantai, tahun_dibangun, daya_listrik,
                       sertifikat, kondisi_properti, tingkat_keamanan, aksesibilitas,
                       tipe_iklan, njop_per_m2, rasio_bangunan_tanah, umur_bangunan,
                       harga_prediksi_total, harga_prediksi_tanah, harga_prediksi_bangunan,
                       harga_per_m2_bangunan, model_predictor, confidence_score, created_at
                FROM prediksi_properti_bangunan_tanah 
                {where_clause}
                ORDER BY harga_prediksi_total DESC 
                LIMIT %s
            """
            
            params.append(limit)
            cur.execute(query, params)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error searching prediksi bangunan tanah: {e}")
            return []

    @staticmethod
    def get_statistics():
        """Ambil statistik prediksi bangunan+tanah (excluding Prajuritkulon)"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    AVG(harga_prediksi_total) as avg_total_price,
                    MIN(harga_prediksi_total) as min_total_price,
                    MAX(harga_prediksi_total) as max_total_price,
                    AVG(harga_per_m2_bangunan) as avg_price_per_m2,
                    AVG(luas_bangunan_m2) as avg_building_size,
                    AVG(luas_tanah_m2) as avg_land_size,
                    COUNT(DISTINCT kecamatan) as total_kecamatan
                FROM prediksi_properti_bangunan_tanah
                WHERE kecamatan NOT LIKE '%prajurit%'
            """)
            result = cur.fetchone()
            cur.close()
            return result
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return None

    @staticmethod
    def get_by_kecamatan_stats():
        """Ambil statistik berdasarkan kecamatan"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    kecamatan,
                    COUNT(*) as total_properties,
                    AVG(harga_prediksi_total) as avg_price,
                    MIN(harga_prediksi_total) as min_price,
                    MAX(harga_prediksi_total) as max_price,
                    AVG(harga_per_m2_bangunan) as avg_price_per_m2
                FROM prediksi_properti_bangunan_tanah
                GROUP BY kecamatan
                ORDER BY avg_price DESC
            """)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting kecamatan statistics: {e}")
            return []

    @staticmethod
    def get_location_analysis():
        """Ambil analisis per lokasi untuk data bangunan (excluding Prajuritkulon)"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    kecamatan,
                    COUNT(*) as total_properties,
                    AVG(harga_prediksi_total) as avg_price,
                    MIN(harga_prediksi_total) as min_price,
                    MAX(harga_prediksi_total) as max_price,
                    SUM(harga_prediksi_total) as total_value,
                    AVG(luas_bangunan_m2) as avg_building_area,
                    AVG(luas_tanah_m2) as avg_land_area,
                    COUNT(DISTINCT sertifikat) as certificate_types
                FROM prediksi_properti_bangunan_tanah 
                WHERE kecamatan NOT LIKE '%prajurit%'
                GROUP BY kecamatan
                ORDER BY avg_price DESC
            """)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting location analysis: {e}")
            return []

    @staticmethod
    def get_certificate_distribution():
        """Ambil distribusi sertifikat untuk bangunan (excluding Prajuritkulon)"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    sertifikat,
                    COUNT(*) as count,
                    AVG(harga_prediksi_total) as avg_price,
                    MIN(harga_prediksi_total) as min_price,
                    MAX(harga_prediksi_total) as max_price
                FROM prediksi_properti_bangunan_tanah 
                WHERE sertifikat IS NOT NULL AND sertifikat != ''
                AND kecamatan NOT LIKE '%prajurit%'
                GROUP BY sertifikat
                ORDER BY count DESC
            """)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting certificate distribution: {e}")
            return []

    @staticmethod
    def get_building_condition_analysis():
        """Ambil analisis kondisi bangunan (excluding Prajuritkulon)"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT 
                    kondisi_properti,
                    COUNT(*) as count,
                    AVG(harga_prediksi_total) as avg_price,
                    AVG(harga_per_m2_bangunan) as avg_price_per_m2
                FROM prediksi_properti_bangunan_tanah 
                WHERE kondisi_properti IS NOT NULL AND kondisi_properti != ''
                AND kecamatan NOT LIKE '%prajurit%'
                GROUP BY kondisi_properti
                ORDER BY avg_price DESC
            """)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting building condition analysis: {e}")
            return []

    @staticmethod
    def get_all_with_real_prices(limit=100, offset=0):
        """Ambil semua data prediksi bangunan+tanah dengan harga real (jika ada) dengan pagination"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT p.id, p.kecamatan, p.luas_tanah_m2, p.luas_bangunan_m2, p.jumlah_kamar_tidur,
                       p.jumlah_kamar_mandi, p.jumlah_lantai, p.tahun_dibangun, p.daya_listrik,
                       p.sertifikat, p.kondisi_properti, p.tingkat_keamanan, p.aksesibilitas,
                       p.tipe_iklan, p.njop_per_m2, p.rasio_bangunan_tanah, p.umur_bangunan,
                       p.harga_prediksi_total as harga_display,
                       p.harga_prediksi_total, p.harga_prediksi_tanah, p.harga_prediksi_bangunan,
                       p.harga_per_m2_bangunan, p.model_predictor, p.confidence_score, p.created_at,
                       FALSE as has_real_price
                FROM prediksi_properti_bangunan_tanah p
                ORDER BY p.created_at DESC 
                LIMIT %s OFFSET %s
            """, (limit, offset))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"Error getting prediksi bangunan tanah with real prices: {e}")
            return []
