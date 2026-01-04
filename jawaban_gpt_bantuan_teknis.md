# Jawaban Teknis untuk Penulisan Laporan (Input untuk ChatGPT)

Berikut adalah detail teknis dari website `websitebgojik` yang dianalisis langsung dari *source code* untuk menjawab pertanyaan ChatGPT.

### 1. Fungsi Utama, Tujuan, dan Masalah
*   **Fungsi Utama**: Platform pengolahan data pariwisata berbasis web yang mengubah data mentah (CSV/PDF) menjadi visualisasi grafik dan memberikan analisis strategi pemasaran otomatis menggunakan *Machine Learning*.
*   **Tujuan Pembuatan**: Menggantikan proses rekapitulasi data manual, mempercepat analisis tren kunjungan tahunan, dan menyediakan rekomendasi strategi pariwisata berbasis data (*data-driven*) untuk Dinas Pariwisata.
*   **Masalah yang Diselesaikan**: Kesulitan dalam memantau tren kunjungan dari tumpukan laporan file mentah, kurangnya visualisasi data yang mudah dipahami, dan ketiadaan sistem pendukung keputusan untuk menentukan strategi saat *Low* atau *High Season*.

### 2. Arsitektur Sistem
*   **Pola Desain**: Menerapkan pola **MVC (Model-View-Controller)** sederhana.
    *   **Model**: Database SQLite (`tourism.db`) dan logika manipulasi data (via `pandas` & `sqlite3`).
    *   **View**: Folder `templates/` berisi file HTML dengan Jinja2 template untuk antarmuka pengguna.
    *   **Controller**: File `app.py` yang mengatur *routing* URL, validasi input, dan memanggil fungsi analisis.
*   **Alur Komunikasi (Diagram Teks)**:
    `User (Browser)` -> `Request (Upload/View)` -> `Controller (Flask)` -> `Processing (Pandas/ML)` <-> `Model (Database)` -> `Controller` -> `Response (Render Template)` -> `User`.

### 3. Fitur dan Modul Utama
*Berdasarkan kode program saat ini, modul yang tersedia adalah:*

1.  **Modul Manajemen Data (Input)**
    *   *Fungsi*: Menangani upload file data kunjungan. Mendukung format CSV dan PDF (ekstraksi tabel otomatis). Melakukan validasi tahun dan format file.
2.  **Modul Dashboard & Visualisasi**
    *   *Fungsi*: Menampilkan ringkasan statistik (Total, Rata-rata) dan grafik visual (Bar Chart bulanan, Line Chart trend tahunan, Pie Chart musim) yang digenerasi menggunakan library `Matplotlib`.
3.  **Modul Analisis Cerdas (Machine Learning)**
    *   *Fungsi*: Menggunakan algoritma *K-Means Clustering* untuk mengelompokkan pola kunjungan bulan ke dalam kategori "High", "Medium", dan "Low Season". Memberikan rekomendasi teks otomatis berdasarkan hasil clustering tersebut.
4.  **Modul Laporan (Export)**
    *   *Fungsi*: Mengunduh hasil analisis lengkap ke dalam format Microsoft Excel (`.xlsx`), mencakup data mentah, hasil analisis ML, dan gambar grafik.
5.  **Modul Utilitas System**
    *   *Fungsi*: Fitur "Reset Data" untuk menghapus seluruh database dan memulai dari awal.

*Catatan Penting untuk Laporan: Tidak ditemukan "Modul Login" atau "Modul Admin" khusus. Sistem ini bersifat terbuka (single-access) di mana setiap pengguna yang membuka website memiliki akses penuh untuk mengelola data.*

### 4. Analisis Struktur Database
*   **Database**: SQLite (`tourism.db`).
*   **Relasi**: 1-to-Many (Implisit). Satu file upload bisa berisi banyak baris data bulanan.

**Tabel 1: `tourism_data` (Menyimpan data kunjungan per bulan)**
*   `id` (INTEGER, Primary Key, Auto Increment)
*   `year` (INTEGER) - Atribut Utama
*   `month` (TEXT) - Atribut Utama
*   `value` (INTEGER) - Jumlah Pengunjung
*   `created_at` (TIMESTAMP)

**Tabel 2: `uploaded_files` (Audit trail file yang diupload)**
*   `id` (INTEGER, Primary Key, Auto Increment)
*   `filename` (TEXT)
*   `year` (INTEGER)
*   `upload_date` (TIMESTAMP)

**ERD Teks Ringkas**:
`[uploaded_files] --(1:N)--> [tourism_data]`
*(Artinya: Data berasal dari file yang diupload, namun di SQLite tidak diset Foreign Key constraint secara fisik, hanya logika aplikasi).*

### 5. Alur Proses Utama
*   **Alur Input Data**: User mengakses menu Upload -> Pilih File (CSV/PDF) -> Input Tahun -> Sistem Membaca & Memvalidasi File -> Sistem Menyimpan ke Database -> Tampil Pesan Sukses.
*   **Alur Dashboard/Output**: User mengakses Dashboard -> Sistem menarik seluruh data dari DB -> Sistem melakukan *Clustering* & Generate Grafik -> Halaman Dashboard tampil dengan statistik dan saran strategi.
*   **Alur Export**: User klik tombol "Export Excel" -> Sistem men-generate file Excel berisi 4 sheet (Data Mentah, Analisis ML, Chart, Statistik) -> File terunduh otomatis.

### 6. Implementasi Program
*   **Bahasa Pemrograman**: Python 3.9+
*   **Framework Web**: Flask (Microframework yang ringan dan fleksibel).
*   **Database**: SQLite 3 (File-based database, tidak butuh server terpisah).
*   **Library Data Science**:
    *   `Pandas` (Manipulasi data tabel)
    *   `Scikit-Learn` (Algoritma K-Means Clustering untuk ML)
    *   `Matplotlib` (Pembuatan grafik 2D statis)
    *   `pdfplumber` (Ekstraksi teks/tabel dari file PDF)
    *   `OpenPyXL` (Pembuatan file Excel)
*   **Frontend**: HTML5, Bootstrap 5 (CSS Framework), JavaScript.

### 7. Kelebihan dan Keterbatasan (Analisis Nyata)
**Kelebihan**:
1.  **Analisis Otomatis**: Memiliki fitur *Machine Learning* sederhana (Clustering) yang memberikan nilai tambah dibanding aplikasi pencatatan biasa.
2.  **Fleksibilitas Input**: Bisa membaca langsung dari PDF, sangat membantu jika sumber data asli berupa laporan dokumen PDF.
3.  **Visualisasi Komprehensif**: Menyediakan grafik lengkap (Tren, Musiman, Perbandingan) yang siap pakai untuk laporan.

**Keterbatasan**:
1.  **Keamanan (Security)**: **Tidak ada fitur Login/Autentikasi**. Siapapun yang bisa mengakses URL bisa menghapus seluruh data (Fitur Delete Data terbuka untuk umum). Ini adalah poin kritis.
2.  **Interaktivitas Grafik**: Grafik dirender sebagai gambar statis (PNG) dari server, bukan grafik interaktif (seperti JS Chart) yang bisa di-hover/zoom.
3.  **Validasi PDF**: Ekstraksi PDF sangat bergantung pada format tabel yang baku. Jika format laporan PDF dinas berubah layout-nya, fitur upload PDF mungkin gagal membaca.
