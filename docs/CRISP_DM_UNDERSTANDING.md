# Dokumentasi Metodologi CRISP-DM: Phase 1 & Phase 2
**Proyek:** Analisis Spasial Pertanahan Nasional dan Tata Ruang Tingkat Desa  
**Dataset:** `data/desa.xlsx` (79.842 desa/kelurahan, 34 provinsi, 508 kabupaten/kota)  
**Referensi Kode:** `master.ipynb`  

---

## 1. PHASE 1: BUSINESS UNDERSTANDING (Pemahaman Bisnis & Kebijakan)

### 1.1 Latar Belakang & Konteks Kebijakan
Kementerian Agraria dan Tata Ruang / Badan Pertanahan Nasional (ATR/BPN) bersama pemangku kepentingan terkait (Bappenas, Kemendesa, dan Pemerintah Daerah) memiliki mandat strategis nasional:
1. **Pendaftaran Tanah Sistematis Lengkap (PTSL):** Mendaftarkan dan memetakan seluruh bidang tanah di Indonesia menuju deklarasi *"Desa Lengkap"* dan *"Kabupaten/Kota Lengkap"*.
2. **Kebijakan Satu Peta (One Map Policy) & Sinkronisasi Tata Ruang:** Menyelaraskan status hak kepemilikan tanah dengan instrumen tata ruang, khususnya Rencana Detail Tata Ruang (RDTR) untuk perizinan berusaha otomatis (OSS / KKPR).
3. **Mitigasi Bencana & Perlindungan Aset:** Memahami kerentanan aset masyarakat terhadap bahaya hidrometeorologi (banjir) berdasarkan status legalitas hak atas tanah.

### 1.2 Masalah Kebijakan (Problem Statement)
Meskipun program pendaftaran tanah telah berjalan masif sejak 2017:
* **Disparitas Spasial yang Tinggi:** Sebagian desa/kelurahan (terutama di perkotaan dan Jawa) telah mendekati status lengkap, sementara ribuan desa pedesaan di luar Jawa masih didominasi bidang tanah belum terdaftar (`kosong`).
* **Inkonsistensi Spasial & Kualitas Data:** Batas kartometrik desa yang belum definitif menyebabkan ketidakselarasan luas administrasi desa dengan akumulasi bidang tanah terpetakan.
* **Belum Adanya Tipologi Objektif:** Alokasi target pendaftaran tanah tahunan sering kali masih bersifat agregat tanpa segmentasi berbasis tipologi kematangan pertanahan dan tingkat kerentanan wilayah.

### 1.3 Tujuan Bisnis / Kebijakan (Business Objectives)
1. **Segmentasi Kematangan Kadastral:** Memetakan dan mengelompokkan 79.842 desa/kelurahan di Indonesia ke dalam profil kematangan pendaftaran tanah yang dapat diinterpretasi.
2. **Prioritisasi Intervensi Kebijakan:** Memberikan rekomendasi berbasis bukti (*evidence-based policy*) bagi kantor pertanahan (Kantah) untuk memprioritaskan alokasi PTSL dan sertipikasi aset.
3. **Deteksi Dini Integritas Data Spasial:** Mengidentifikasi kantong-kantong anomali luasan persil tanah guna memandu kegiatan audit lapangan (*ground-truthing*) dan perbaikan batas peta digital.

### 1.4 Penilaian Situasi (Assessment of Situation)
* **Ketersediaan Sumber Daya:** Tersedia data agregat tingkat desa terlengkap se-Indonesia (`desa.xlsx`) hasil olahan sistem GIS pertanahan per Oktober 2026.
* **Batasan & Risiko Data:** Data tidak menyediakan geometri poligon mentah (hanya agregat tabel per desa), sehingga analisis spasial lanjutan mengandalkan hierarki kode wilayah administrasi (8 digit).
* **Kebutuhan Domain:** Analisis harus membedakan secara tegas antara persil hak privat masyarakat (Hak Milik), hak usaha komersial skala besar (HGU/HGB), aset publik/pemerintah (Hak Pakai/Hak Pengelolaan), hak keagamaan (Wakaf), dan bidang belum berstatus (`kosong`).

### 1.5 Tujuan Data Mining (Data Mining Goals)
Secara teknis analitis, tujuan ini diturunkan menjadi:
1. **Unsupervised Clustering / Typology Profiling:**
   * Mereduksi dimensi multivariat hak tanah dan tata ruang.
   * Mengelompokkan desa ke dalam 4–5 klaster kematangan pertanahan dan paparan risiko lingkungan (menggunakan K-Means, Gaussian Mixture Models, atau HDBSCAN).
2. **Spatial Anomaly Detection:**
   * Membangun model deteksi anomali tanpa pengawasan (Isolation Forest / Local Outlier Factor) untuk mendeteksi desa dengan rasio persil-luas yang menyimpang secara ekstrem.
3. **Analisis Asosiasi & Komparasi Antar-Wilayah:**
   * Menganalisis korelasi antara penetrasi RDTR, paparan banjir, dan tingkat sertipikasi tanah.

### 1.6 Kriteria Keberhasilan (Project Success Criteria)
* **Kriteria Keberhasilan Bisnis/Kebijakan:**
  * Dihasilkannya indeks prioritas desa (*Desa Lengkap Readiness Index*) dan daftar prioritas audit anomali data per kabupaten/kota.
* **Kriteria Keberhasilan Data Mining:**
  * Model klaster menghasilkan metrik pemisahan yang teruji (*Silhouette Score* memadai, klaster stabil, dan memiliki interpretasi bisnis yang jelas).
  * Fitur-fitur yang digunakan terbebas dari multikolinearitas eksak (*size-neutral ratios*).

---

## 2. PHASE 2: DATA UNDERSTANDING (Pemahaman Data)

### 2.1 Pengumpulan Data Awal (Data Collection)
* **Nama File:** `data/desa.xlsx`
* **Format:** Microsoft Excel Spreadsheet (.xlsx)
* **Dimensi:** 79.842 baris × 33 kolom.
* **Unit Analisis:** 1 baris mewakili 1 unit wilayah administratif setingkat desa / kelurahan di Indonesia.
* **Waktu Snapshot:** Dihitung dan diekstraksi pada Oktober 2026 (`dihitung_pada`).

### 2.2 Deskripsi Data & Kamus Data (Data Description)
Variabel terbagi ke dalam 4 kelompok dimensi logis:

#### A. Identitas Administratif & Hierarki Spasial
| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `kode` | String (8-digit) | Kode wilayah Kemendagri/BPS (PPKKCCDD: Propinsi, Kab/Kota, Kecamatan, Desa). |
| `nama` | String | Nama desa/kelurahan (terdapat variasi kapitalisasi: Title vs UPPER). |
| `tipe` | String | Klasifikasi wilayah administrasi: `Desa` (pedesaan) vs `Kelurahan` (perkotaan). |
| `kecamatan` | String | Nama kecamatan induk. |
| `kabupaten` | String | Nama kabupaten atau kota. |
| `provinsi` | String | Nama provinsi (34 provinsi di Indonesia). |

#### B. Dimensi Fisik, Tata Ruang, & Risiko Lingkungan
| Kolom | Tipe Data | Satuan | Deskripsi |
| :--- | :--- | :--- | :--- |
| `luas_desa` | Float | $m^2$ | Luas administratif desa berdasarkan batas spasial yang digunakan BPN. |
| `rdtr_luas` | Float | $m^2$ | Luas wilayah desa yang telah dicakup dokumen Rencana Detail Tata Ruang. |
| `banjir_rendah` | Float | $m^2$ | Luas area desa dengan kerawanan banjir tingkat rendah. |
| `banjir_sedang` | Float | $m^2$ | Luas area desa dengan kerawanan banjir tingkat sedang. |
| `banjir_tinggi` | Float | $m^2$ | Luas area desa dengan kerawanan banjir tingkat tinggi. |

#### C. Struktur Hak Atas Tanah (Cadastral Rights)
Terdapat 8 jenis hak tanah. Setiap hak memiliki 2 atribut: cacah bidang (`_jumlah`) dan luasan bidang (`_luas` dalam $m^2$):
1. `hak_milik` (`_jumlah`, `_luas`): Hak turun-temurun, terkuat, dan terpenuh (kepemilikan perorangan/warga).
2. `hgb` (`_jumlah`, `_luas`): Hak Guna Bangunan (komersial, perumahan developer, industri).
3. `hgu` (`_jumlah`, `_luas`): Hak Guna Usaha (perkebunan skala besar/pertanian industri).
4. `hak_pakai` (`_jumlah`, `_luas`): Hak atas tanah instansi pemerintah atau peruntukan khusus.
5. `hak_pengelolaan` (`_jumlah`, `_luas`): Hak Pengelolaan (HPL milik pemerintah pusat/BUMN/Pemda).
6. `hak_wakaf` (`_jumlah`, `_luas`): Tanah wakaf untuk keperluan ibadah dan sosial.
7. `kosong` (`_jumlah`, `_luas`): Bidang tanah terpetakan yang belum berstatus hak / belum bersertipikat resmi.
8. `lainnya` (`_jumlah`, `_luas`): Hak-hak lain yang tidak termasuk klasifikasi di atas.
9. `jumlah_persil` & `luas_persil`: Total akumulasi seluruh bidang tanah di desa tersebut.

#### D. Dimensi Kronologis / Temporal
| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `tahun_min` | Float | Tahun terbit sertipikat/pendaftaran tanah paling awal di desa tersebut. |
| `tahun_median` | Float | Tahun tengah pendaftaran tanah (titik berat masa registrasi masif). |
| `tahun_max` | Float | Tahun pendaftaran tanah paling mutakhir di desa tersebut. |
| `dihitung_pada` | Datetime | Waktu komputasi agregasi spasial dilakukan. |

---

### 2.3 Eksplorasi Data & Temuan Struktural (Exploratory Data Insights)
Berdasarkan pengujian relasi struktural pada tahap *Step 1*:

1. **Identitas Matematika Sempurna:**
   $$\sum_{r=1}^{8} \text{hak}_r\text{\_jumlah} = \text{jumlah\_persil} \quad (\text{100\% konsisten})$$
   $$\sum_{r=1}^{8} \text{hak}_r\text{\_luas} = \text{luas\_persil} \quad (\text{100\% konsisten})$$
   *Implikasi:* `jumlah_persil` dan `luas_persil` adalah variabel komposit/turunan langsung. Jangan menyertakan total ini bersamaan dengan komponen hak tanpa normalisasi untuk menghindari multikolinearitas.

2. **Kopel Nol Bidang & Luas (Zero-Coupling):**
   * Untuk seluruh hak tanah resmi, jika `_jumlah == 0` maka `_luas == 0` secara mutlak (hanya 6 kasus perkecualian pada tanah kosong).

3. **Inklusi Area Tata Ruang & Bencana:**
   * $\text{rdtr\_luas} \le \text{luas\_desa}$ dan $\sum \text{banjir\_*} \le \text{luas\_desa}$ berlaku tanpa pelanggaran (dengan batas toleransi pembulatan $0,01\%$). Kedua atribut ini aman dikonversi menjadi proporsi/rasio terhadap `luas_desa`.

---

### 2.4 Verifikasi Kualitas Data & Isu-Isu Kritis (Data Quality Verification)

#### 1. Pelanggaran Luas Persil vs Luas Desa (Anomali Spasial Utama)
* **Temuan:** Terdapat **11.009 desa (13,8%)** yang memiliki:
  $$\text{luas\_persil} > \text{luas\_desa}$$
* **Penyebab Domain:**
  - Batas administrasi desa masih indikatif (belum penetapan batas kartometrik permanen oleh Kemendagri).
  - Persil tanah HGU/perkebunan luas melintasi batas administrasi lebih dari satu desa (*cross-boundary parcels*).
  - Tumpang tindih peta digital (*overlapping digital land parcels*).
* **Strategi Penanganan:** Desa-desa ini tidak boleh langsung dibuang (karena berjumlah 13,8%), melainkan diberikan *flagging* khusus (`anomali_luas_flag = 1`) dan dijadikan target audit kualitas data spasial.

#### 2. Pola Nilai Hilang (Missing Values Pattern)
* **Temuan:** Kolom tahun (`tahun_min`, `tahun_median`, `tahun_max`) memiliki missing value pada **2.670 baris (3,3%)**.
* **Karakteristik:** Missing ini bersifat *Missing Not at Random (MNAR)*. Terbukti bahwa ketika kolom tahun bernilai null, desa tersebut **tidak memiliki satu pun bidang tanah yang berstatus hak** ($\text{jumlah\_persil} - \text{kosong\_jumlah} = 0$).
* **Strategi Penanganan:** Tidak boleh diisi sembarangan (*impute mean/median*). Desa tanpa tahun pendaftaran dikelompokkan ke dalam kategori *"Belum Terintervensi Pendaftaran"* atau diberikan nilai indikator terpisah.

#### 3. Variasi Skala Desa (Scale Invariance Requirement)
* Luas desa di Indonesia memiliki rentang dari ribuan meter persegi ($< 0,1 \text{ km}^2$) hingga ratusan juta meter persegi ($> 100 \text{ km}^2$).
* Penggunaan nilai absolut luas akan membiaskan algoritma machine learning kepada ukuran fisik desa, bukan struktur pertanahannya. Wajib dilakukan rekayasa fitur netral-ukuran (*size-neutral features*).

#### 4. Kerapuhan Nomenklatur Wilayah
* Nama kabupaten/kota dan kecamatan memiliki variasi kapitalisasi huruf (`UPPERCASE` vs `Title Case`).
* Beberapa kabupaten hasil pemekaran berbagi kode wilayah yang identik (misal: Solok / Solok Selatan, Rokan Hilir / Siak).
* **Solusi:** Wajib menggunakan *composite key* (`prov_code` + `kab_code` + `nama_ternormalisasi`) sebelum agregasi wilayah.

---

## 3. RENCANA MENUJU PHASE 3 (Data Preparation) & PHASE 4 (Modeling)

Dari pemahaman bisnis dan data di atas, peta jalan teknis berikutnya adalah:

### Rekayasa Fitur Wajib (Feature Engineering):
1. **Rasio Penetrasi Sertipikasi:**
   $$\text{rasio\_terdaftar} = \frac{\text{jumlah\_persil} - \text{kosong\_jumlah}}{\text{jumlah\_persil} + 1}$$
2. **Proporsi Dominasi Hak Lahan:**
   $$\text{prop\_hak\_milik} = \frac{\text{hak\_milik\_luas}}{\text{luas\_persil} + 1}$$
   $$\text{prop\_hgb} = \frac{\text{hgb\_luas}}{\text{luas\_persil} + 1}$$
   $$\text{prop\_hgu} = \frac{\text{hgu\_luas}}{\text{luas\_persil} + 1}$$
3. **Kepadatan Kadastral Spasial:**
   $$\text{densitas\_persil} = \frac{\text{jumlah\_persil}}{\text{luas\_desa} / 10.000} \quad (\text{bidang per hektar})$$
4. **Indikator Kesiapan Tata Ruang & Risiko Bencana:**
   $$\text{rasio\_rdtr} = \frac{\text{rdtr\_luas}}{\text{luas\_desa}}$$
   $$\text{rasio\_banjir\_tinggi} = \frac{\text{banjir\_tinggi}}{\text{luas\_desa}}$$
5. **Dinamika Pendaftaran Tanah (PTSL Velocity):**
   $$\text{rentang\_tahun} = \text{tahun\_max} - \text{tahun\_min}$$
   $$\text{momentum\_pendaftaran} = \text{tahun\_max} - \text{tahun\_median}$$
