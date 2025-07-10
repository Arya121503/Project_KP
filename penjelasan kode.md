# Penjelasan Harga Rata-Rata (Prediksi) vs. Harga Rata-Rata (Real)

Dokumen ini menjelaskan perbedaan antara metrik "Harga Rata-rata (Prediksi)" dan "Harga Rata-rata (Real)" yang ditampilkan pada dasbor admin.

**Secara singkat:** Harga **Prediksi** adalah estimasi otomatis oleh sistem (Machine Learning), sedangkan harga **Real** adalah nilai final yang ditetapkan secara manual oleh Admin.

---

### Harga Rata-rata (Prediksi)

-   **Sumber:** Dihasilkan secara otomatis oleh model *machine learning* (ML) yang telah dilatih (misalnya, Random Forest, XGBoost, dll.).
-   **Proses:** Ketika data aset baru (baik tanah maupun bangunan) dimasukkan ke dalam sistem, model ML akan menganalisis fitur-fitur properti tersebut (seperti lokasi, luas tanah, luas bangunan, jumlah kamar, dll.) untuk menghitung estimasi harganya.
-   **Tujuan:** Memberikan **nilai taksiran awal** yang cepat dan objektif berdasarkan data historis. Ini berfungsi sebagai acuan atau titik awal bagi admin dalam proses evaluasi aset.
-   **Sifat:** Merupakan **estimasi** dan bukan harga resmi yang akan dipublikasikan. Akurasinya bergantung pada kualitas model dan data.

### Harga Rata-rata (Real)

-   **Sumber:** Ditetapkan atau dimasukkan secara **manual oleh Admin** melalui fitur "Manajemen Harga Real Aset".
-   **Proses:** Setelah model ML memberikan harga prediksi, admin akan melakukan verifikasi. Admin dapat menyetujui harga prediksi tersebut atau mengubahnya berdasarkan pertimbangan lain yang mungkin tidak tercakup oleh model, seperti:
    -   Kondisi pasar terkini.
    -   Hasil negosiasi dengan pihak terkait.
    -   Faktor unik atau kondisi spesifik dari properti.
    -   Kebijakan internal perusahaan.
-   **Tujuan:** Menjadi **harga resmi dan final** dari aset tersebut. Harga inilah yang akan digunakan untuk transaksi, penawaran sewa, laporan keuangan, dan keperluan resmi lainnya.
-   **Sifat:** Merupakan **nilai yang sudah diverifikasi** dan dianggap sebagai harga yang valid dan akurat oleh pengelola sistem.

### Alur Kerja

Alur data harga di dalam sistem adalah sebagai berikut:

1.  **Data Aset Masuk** ->
2.  **Harga Prediksi Dihasilkan (Otomatis oleh ML)** ->
3.  **Admin Melakukan Verifikasi & Penetapan Harga Real (Manual)**

Dasbor menampilkan rata-rata dari kedua jenis harga ini untuk memberikan gambaran perbandingan antara estimasi awal oleh sistem dan nilai final yang berlaku di lapangan.
