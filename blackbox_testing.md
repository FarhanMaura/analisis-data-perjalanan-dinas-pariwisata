# Black Box Testing - Sistem Manajemen Data Pariwisata Palembang

## 1. Testing Upload Data CSV

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 1.1 | Upload file CSV valid dengan data Palembang | User memilih file CSV yang berisi data Palembang dan input tahun yang valid | File: `tourism_2023.csv` (berisi data Palembang)<br>Tahun: `2023` | ✅ Flash message sukses: "File berhasil diupload: Data berhasil diproses. Total pengunjung: [jumlah]"<br>✅ Data tersimpan di database<br>✅ File info tersimpan di uploaded_files | ⬜ |
| 1.2 | Upload file CSV tanpa memilih file | User klik upload tanpa memilih file | File: (kosong)<br>Tahun: `2023` | ❌ Flash message error: "Tidak ada file yang dipilih" | ⬜ |
| 1.3 | Upload file CSV tanpa input tahun | User memilih file CSV tapi tidak input tahun | File: `tourism_2023.csv`<br>Tahun: (kosong) | ❌ Flash message error: "Tahun harus diisi" | ⬜ |
| 1.4 | Upload file non-CSV | User memilih file dengan format selain CSV | File: `document.pdf`<br>Tahun: `2023` | ❌ Flash message error: "File harus berformat CSV" | ⬜ |
| 1.5 | Upload file CSV tanpa data Palembang | User memilih file CSV yang tidak berisi data Palembang | File: `other_city.csv` (tidak ada data Palembang)<br>Tahun: `2023` | ❌ Flash message error: "Data Palembang tidak ditemukan dalam file" | ⬜ |
| 1.6 | Upload file CSV dengan tahun invalid (< 2000) | User input tahun di bawah 2000 | File: `tourism_2023.csv`<br>Tahun: `1999` | ❌ Flash message error: "Tahun harus antara 2000 dan tahun depan" | ⬜ |
| 1.7 | Upload file CSV dengan tahun invalid (> tahun depan) | User input tahun melebihi tahun depan | File: `tourism_2023.csv`<br>Tahun: `2030` | ❌ Flash message error: "Tahun harus antara 2000 dan tahun depan" | ⬜ |
| 1.8 | Upload file CSV dengan tahun non-numerik | User input tahun dengan karakter non-angka | File: `tourism_2023.csv`<br>Tahun: `abc` | ❌ Flash message error: "Tahun harus berupa angka" | ⬜ |
| 1.9 | Upload file CSV corrupt/tidak bisa dibaca | User memilih file CSV yang corrupt | File: `corrupt.csv` (file rusak)<br>Tahun: `2023` | ❌ Flash message error: "File tidak bisa dibaca: [error detail]" | ⬜ |
| 1.10 | Upload file CSV yang sama (update data tahun yang sama) | User upload file CSV untuk tahun yang sudah ada di database | File: `tourism_2023_new.csv`<br>Tahun: `2023` | ✅ Data tahun lama dihapus dan diganti dengan data baru<br>✅ Flash message sukses | ⬜ |

---

## 2. Testing Upload Data PDF

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 2.1 | Upload file PDF valid dengan data Palembang | User memilih file PDF yang berisi data Palembang dan input tahun | File: `tourism_2023.pdf` (berisi data Palembang)<br>Tahun: `2023` | ✅ Flash message sukses: "PDF berhasil diproses: [message]"<br>✅ Data tersimpan di database | ⬜ |
| 2.2 | Upload file PDF tanpa memilih file | User klik upload tanpa memilih file | File: (kosong)<br>Tahun: `2023` | ❌ Flash message error: "Tidak ada file PDF yang dipilih" | ⬜ |
| 2.3 | Upload file non-PDF | User memilih file dengan format selain PDF | File: `document.csv`<br>Tahun: `2023` | ❌ Flash message error: "File harus berformat PDF" | ⬜ |
| 2.4 | Upload file PDF tanpa input tahun | User memilih file PDF tapi tidak input tahun | File: `tourism_2023.pdf`<br>Tahun: (kosong) | ✅ Sistem menggunakan tahun saat ini sebagai default<br>✅ Data berhasil diproses | ⬜ |
| 2.5 | Upload file PDF dengan tahun invalid | User input tahun invalid | File: `tourism_2023.pdf`<br>Tahun: `1999` | ❌ Flash message error: "Tahun harus antara 2000 dan tahun depan" | ⬜ |
| 2.6 | Upload file PDF corrupt/tidak bisa dibaca | User memilih file PDF yang corrupt | File: `corrupt.pdf` (file rusak)<br>Tahun: `2023` | ❌ Flash message error: "Error processing PDF: [error detail]" | ⬜ |

---

## 3. Testing Dashboard Analisis

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 3.1 | Akses dashboard dengan data tersedia | User mengakses halaman dashboard saat database memiliki data | Akses `/dashboard` | ✅ Menampilkan chart bulanan<br>✅ Menampilkan chart tahunan<br>✅ Menampilkan suggestions dari ML<br>✅ Menampilkan statistik database | ⬜ |
| 3.2 | Akses dashboard tanpa data | User mengakses halaman dashboard saat database kosong | Akses `/dashboard` | ✅ Menampilkan pesan "Belum ada data untuk dianalisis"<br>✅ Chart kosong<br>✅ Suggestions: "Belum ada data untuk dianalisis" | ⬜ |
| 3.3 | Lihat chart bulanan | User melihat chart rata-rata bulanan | Akses `/dashboard` | ✅ Chart menampilkan 12 bulan (Jan-Dec)<br>✅ Warna berbeda untuk High/Medium/Low season<br>✅ Nilai rata-rata ditampilkan di atas bar | ⬜ |
| 3.4 | Lihat chart tahunan | User melihat chart trend tahunan | Akses `/dashboard` | ✅ Chart menampilkan semua tahun yang ada di database<br>✅ Line chart dengan marker<br>✅ Total pengunjung per tahun ditampilkan | ⬜ |
| 3.5 | Lihat suggestions ML | User melihat rekomendasi dari analisis ML | Akses `/dashboard` | ✅ Menampilkan maksimal 3 suggestions<br>✅ Suggestions relevan dengan data | ⬜ |
| 3.6 | Lihat statistik database | User melihat info database di sidebar | Akses `/dashboard` | ✅ Menampilkan total tahun data<br>✅ Menampilkan total records<br>✅ Menampilkan total file uploaded | ⬜ |

---

## 4. Testing Export Excel

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 4.1 | Export data ke Excel dengan data tersedia | User klik tombol "Export to Excel" di dashboard | Klik button export | ✅ File Excel (.xlsx) ter-download<br>✅ File berisi 4 sheet: Data Mentah, Analisis ML, Visualisasi, Statistik<br>✅ Chart embedded di sheet Visualisasi | ⬜ |
| 4.2 | Export data ke Excel tanpa data | User klik export saat database kosong | Klik button export | ✅ File Excel tetap ter-download<br>✅ Sheet kosong dengan header saja | ⬜ |
| 4.3 | Validasi sheet "Data Mentah" | User membuka sheet Data Mentah di Excel | Buka file Excel | ✅ Header: Tahun, Bulan, Jumlah Pengunjung<br>✅ Data terurut berdasarkan tahun dan bulan<br>✅ Format kolom sesuai (number untuk tahun dan value) | ⬜ |
| 4.4 | Validasi sheet "Analisis ML" | User membuka sheet Analisis ML di Excel | Buka file Excel | ✅ Menampilkan suggestions<br>✅ Menampilkan pola yang teridentifikasi<br>✅ Menampilkan clustering metrics (Silhouette Score) | ⬜ |
| 4.5 | Validasi sheet "Visualisasi" | User membuka sheet Visualisasi di Excel | Buka file Excel | ✅ Chart bulanan embedded sebagai gambar<br>✅ Chart tahunan embedded sebagai gambar<br>✅ Chart seasonal pie embedded sebagai gambar<br>✅ Chart comparison embedded (jika ada >= 2 tahun) | ⬜ |
| 4.6 | Validasi sheet "Statistik" | User membuka sheet Statistik di Excel | Buka file Excel | ✅ Statistik dasar (total tahun, total records, dll)<br>✅ Summary analisis ML<br>✅ Kualitas data | ⬜ |

---

## 5. Testing Hapus Data

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 5.1 | Hapus semua data | User klik tombol "Hapus Semua Data" dan konfirmasi | Klik button hapus → Konfirmasi | ✅ Semua data di tabel `tourism_data` terhapus<br>✅ Semua data di tabel `uploaded_files` terhapus<br>✅ Semua file di folder `uploads` terhapus<br>✅ Flash message: "Semua data berhasil dihapus" | ⬜ |
| 5.2 | Hapus data saat database kosong | User klik hapus saat tidak ada data | Klik button hapus | ✅ Flash message sukses (tidak error)<br>✅ Sistem tetap berjalan normal | ⬜ |
| 5.3 | Validasi setelah hapus data | User akses dashboard setelah hapus data | Akses `/dashboard` setelah hapus | ✅ Dashboard menampilkan "Belum ada data"<br>✅ Chart kosong<br>✅ Statistik database menunjukkan 0 | ⬜ |

---

## 6. Testing Navigasi & UI

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 6.1 | Akses homepage | User mengakses root URL | Akses `/` | ✅ Menampilkan homepage dengan informasi sistem<br>✅ Button "Mulai Upload Data" dan "Lihat Dashboard" berfungsi | ⬜ |
| 6.2 | Navigasi dari homepage ke upload | User klik "Mulai Upload Data" | Klik button | ✅ Redirect ke halaman `/upload`<br>✅ Form upload ditampilkan | ⬜ |
| 6.3 | Navigasi dari homepage ke dashboard | User klik "Lihat Dashboard" | Klik button | ✅ Redirect ke halaman `/dashboard`<br>✅ Dashboard ditampilkan | ⬜ |
| 6.4 | Navigasi antar halaman via navbar | User klik menu di navigation bar | Klik menu navbar | ✅ Navigasi ke halaman yang sesuai<br>✅ Active state pada menu yang sedang dibuka | ⬜ |
| 6.5 | Akses halaman 404 | User mengakses URL yang tidak ada | Akses `/invalid-url` | ✅ Menampilkan halaman 404<br>✅ Link kembali ke homepage | ⬜ |
| 6.6 | Responsive design - Mobile | User akses website dari mobile device | Akses dari smartphone | ✅ Layout responsive<br>✅ Chart dapat dilihat dengan baik<br>✅ Button dan form mudah diakses | ⬜ |
| 6.7 | Responsive design - Tablet | User akses website dari tablet | Akses dari tablet | ✅ Layout responsive<br>✅ Semua fitur dapat diakses | ⬜ |

---

## 7. Testing API Endpoints

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 7.1 | API Chart Data | Request data chart via API | GET `/api/chart-data` | ✅ Response JSON dengan format:<br>`{monthly_labels: [], monthly_values: [], yearly_labels: [], yearly_values: []}` | ⬜ |
| 7.2 | API Advanced Chart Data | Request advanced chart data | GET `/api/advanced-chart-data` | ✅ Response JSON dengan data chart advanced<br>✅ Status code 200 | ⬜ |
| 7.3 | API Analysis Data | Request ML analysis data | GET `/api/analysis-data` | ✅ Response JSON dengan suggestions dan patterns<br>✅ Status code 200 | ⬜ |
| 7.4 | API Database Stats | Request database statistics | GET `/api/db-stats` | ✅ Response JSON dengan total_years, total_records, dll<br>✅ Status code 200 | ⬜ |
| 7.5 | API Error Handling | Request API saat terjadi error | GET `/api/analysis-data` (saat error) | ✅ Response JSON dengan key `error`<br>✅ Status code sesuai (500 untuk server error) | ⬜ |

---

## 8. Testing Error Handling

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 8.1 | Upload file terlalu besar (> 16MB) | User upload file lebih dari 16MB | File: `large_file.csv` (> 16MB) | ❌ Flash message error: "File terlalu besar. Maksimal 16MB"<br>✅ Redirect ke halaman upload | ⬜ |
| 8.2 | Database connection error | Simulasi error koneksi database | Rename/hapus file `tourism.db` | ❌ Flash message error yang informatif<br>✅ Sistem tidak crash | ⬜ |
| 8.3 | Internal server error (500) | Simulasi internal error | Trigger error di backend | ❌ Flash message: "Terjadi error internal server"<br>✅ Redirect ke homepage | ⬜ |

---

## 9. Testing Data Integrity

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 9.1 | Validasi data tersimpan dengan benar | Upload CSV dan cek database | Upload file CSV valid | ✅ Data di database sesuai dengan data di CSV<br>✅ 12 bulan tersimpan lengkap<br>✅ Tahun tersimpan sesuai input | ⬜ |
| 9.2 | Validasi perhitungan total pengunjung | Cek total pengunjung yang ditampilkan | Upload file CSV | ✅ Total pengunjung = sum dari 12 bulan<br>✅ Angka sesuai dengan perhitungan manual | ⬜ |
| 9.3 | Validasi update data tahun yang sama | Upload 2x untuk tahun yang sama | Upload tahun 2023 → Upload tahun 2023 lagi | ✅ Data tahun 2023 yang lama terhapus<br>✅ Hanya data terbaru yang tersimpan<br>✅ Tidak ada duplikasi | ⬜ |
| 9.4 | Validasi timestamp created_at | Cek timestamp saat data disimpan | Upload file CSV | ✅ Timestamp `created_at` sesuai dengan waktu upload<br>✅ Format timestamp valid | ⬜ |

---

## 10. Testing Performance

| No | Skenario Testing | Test Case | Input | Expected Output | Status |
|----|------------------|-----------|-------|-----------------|--------|
| 10.1 | Load time homepage | Akses homepage dan ukur waktu loading | Akses `/` | ✅ Halaman load dalam < 2 detik | ⬜ |
| 10.2 | Load time dashboard dengan banyak data | Akses dashboard dengan 10+ tahun data | Akses `/dashboard` | ✅ Dashboard load dalam < 5 detik<br>✅ Chart ter-render dengan baik | ⬜ |
| 10.3 | Upload file besar (mendekati 16MB) | Upload file CSV ~15MB | Upload file besar | ✅ File berhasil diupload<br>✅ Proses selesai dalam waktu wajar (< 30 detik) | ⬜ |
| 10.4 | Export Excel dengan banyak data | Export data dengan 10+ tahun | Klik export | ✅ File Excel ter-generate dalam < 10 detik<br>✅ File size wajar | ⬜ |

---

## Summary Testing

**Total Test Cases:** 60+

**Kategori:**
- ✅ **Functional Testing:** Upload CSV, Upload PDF, Dashboard, Export, Delete
- ✅ **UI/UX Testing:** Navigasi, Responsive Design
- ✅ **API Testing:** Endpoint validation
- ✅ **Error Handling:** File validation, Error messages
- ✅ **Data Integrity:** Database validation
- ✅ **Performance Testing:** Load time, File processing

**Status Legend:**
- ⬜ Not Tested
- ✅ Passed
- ❌ Failed
- ⚠️ Partial Pass

---

## Notes untuk Tester

1. **Environment Setup:**
   - Pastikan Python dan dependencies terinstall
   - Database `tourism.db` harus ada
   - Folder `uploads` harus ada dan writable

2. **Test Data:**
   - Siapkan file CSV valid dengan data Palembang
   - Siapkan file CSV tanpa data Palembang
   - Siapkan file PDF untuk testing
   - Siapkan file corrupt untuk negative testing

3. **Browser Testing:**
   - Test di Chrome, Firefox, Safari
   - Test di mobile browser (Chrome Mobile, Safari iOS)

4. **Regression Testing:**
   - Jalankan semua test case setelah setiap update
   - Prioritaskan critical path: Upload → Dashboard → Export
