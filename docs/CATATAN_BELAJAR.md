# Catatan Belajar: Proyek Spasial Pertanahan Nasional

> Jurnal belajar santai dari nol — semua drama data, konsep penting, aturan main, dan catatan tiap langkah *modeling* bakal dicatat rapi di sini step-by-step.

---

## Peta Jalan Belajar

- [x] **Step 0:** Kenalan dari Nol — Spill The Tea Proyek & Drama Datanya
- [x] **Step 1:** Cek Ombak — Kenalan sama `X_A_scaled.csv` & Uji *Cluster Tendency*
- [x] **Step 2:** Adu "Mak Comblang" — Eksperimen Algoritma Clustering (K-Means, GMM, HDBSCAN) & Pilih $k$
- [x] **Step 3:** Tes Anti-Goyah — Uji Stabilitas & Sensitivitas (*Seed*, *Bootstrap*, Variant A vs B)
- [x] **Step 4:** Sesi Kepo — Cek Bias Geografis & Bongkar Profil Tiap Geng
- [ ] **Step 5:** Kasih Julukan & Bikin Rekomendasi Kebijakan (Termasuk Grup `place_later`)

---

## Step 0: Kenalan dari Nol — Spill The Tea Proyek & Drama Datanya

### 1. Sebenarnya ini proyek apaan sih?
Jadi ceritanya, Kementerian ATR/BPN (yang ngurus sertifikat tanah dan tata ruang di Indonesia) punya misi gede: ingin mendaftarkan dan memetakan seluruh bidang tanah di Indonesia lewat program **PTSL** (*Pendaftaran Tanah Sistematis Lengkap*) menuju *"Desa Lengkap"* dan *"Kabupaten/Kota Lengkap"*, sekaligus menyelaraskan tata ruang (**RDTR**) dan memahami kerentanan aset terhadap banjir.

Masalahnya, Indonesia itu ada **79.842 desa dan kelurahan** (64.223 Desa + 15.619 Kelurahan di 34 provinsi, *snapshot* data tanggal **17 Oktober 2026**). Nasib tanahnya beda-beda jauh:
- Ada kelurahan di kota yang hampir semua petak tanahnya sudah bersertifikat rapi dan penuh ruko/perumahan.
- Ada desa yang isinya didominasi kebun skala raksasa milik perusahaan.
- Ada juga desa yang petak tanahnya sudah digambar di peta BPN, tapi status haknya masih **"kosong"** alias belum bersertifikat resmi.

Nah, **misi besar proyek ini** simpel:
> **Mengelompokkan puluhan ribu desa itu ke dalam beberapa "geng" (klaster) berdasarkan kemiripan profil kepemilikan tanahnya**, supaya pemerintah tahu desa mana yang sudah matang, mana yang perlu dikebut program sertifikasi gratis (PTSL), dan mana yang perlu perhatian khusus.

---

### 2. Isi datanya (`data/desa.xlsx`) apa aja?
Bayangin ada satu file Excel raksasa: `data/desa.xlsx` (79.842 baris × 33 kolom). **Satu baris = satu desa/kelurahan.** Tiap desa punya 4 kelompok "biodata":

1. **KTP Wilayah:** Nama desa/kelurahan, kecamatan, kabupaten/kota, provinsi, tipe (`Desa` vs `Kelurahan`), plus kode wilayah unik **8 digit** (`kode8`: format `PPKKCCDD` = Provinsi, Kab/Kota, Kecamatan, Desa).
2. **8 Jenis Status Hak Tanah:** Masing-masing punya cacah bidang (`_jumlah`) dan luas dalam $m^2$ (`_luas`):
   - `hak_milik` (SHM): tanah milik perorangan/warga biasa (rumah tinggal, sawah).
   - `hgb` (Hak Guna Bangunan): ruko, pabrik, perumahan developer.
   - `hgu` (Hak Guna Usaha): perkebunan/pertanian skala besar perusahaan (sawit, tebu, dll.).
   - `hak_pakai`: tanah instansi pemerintah / fasilitas umum.
   - `hak_pengelolaan`: lahan kelola negara/BUMN/Pemda (mis. pelabuhan, kawasan industri).
   - `hak_wakaf`: tanah ibadah/sosial (masjid, makam, pesantren).
   - `lainnya`: hak-hak lain di luar kategori di atas.
   - `kosong`: bidang tanah yang sudah tergambar batasnya di peta BPN, tapi **belum punya status hak/sertifikat** (target utama PTSL!).
3. **Tata Ruang & Risiko Banjir:** `rdtr_luas` (luas wilayah yang sudah tercakup Rencana Detail Tata Ruang), serta `banjir_rendah`, `banjir_sedang`, `banjir_tinggi` (luas area rawan banjir tiap tingkat).
4. **Sejarah Sertifikat (Kronologis):** `tahun_min` (sertifikat paling awal), `tahun_median` (tahun tengah masa pendaftaran), dan `tahun_max` (sertifikat paling baru).

---

### 3. "Skandal" & drama data yang sudah terbongkar di pre-processing
Sebelum tahap modeling dimulai, data mentah sudah dibersihkan dan diaudit habis-habisan di `pre_processing/master.ipynb`. Hasil investigasinya ternyata penuh drama:

- **122 "Baris Ngaco" terpaksa dikeluarin (`excluded_rows.csv`):**
  - **2 baris siluman** yang bukan desa beneran (satu bernama `"HGU"`, satu lagi nama dan kecamatannya cuma `"-"`).
  - **46 desa yang luas desanya 0 $m^2$** — hampir setengahnya (22 desa) ngumpul di Bengkulu, jadi semua hitungan rasio tidak terdefinisi.
  - **74 desa yang total luas persilnya > 10× luas desanya sendiri** — terlalu ekstrem untuk dihitung sebagai data normal.
- **1.950 desa "kosong melompong" tanpa persil (`place_later.csv`):**
  - Paling banyak ngumpul di **Papua Barat (344)**, **NTT (296)**, **Sumatera Utara (295)**, dan **Papua (283)**.
  - Karena tidak ada satu pun petak tanah (`jumlah_persil = 0`), proporsi hak tanahnya `0/0` (tidak terdefinisi). **Aturannya:** jangan ditebak/diisi angka palsu, tapi nanti dilaporkan sebagai **kelompok tersendiri** di hasil akhir!
- **10.935 desa (13,7%) *overshoot* (luas persil 1–10× luas desa):**
  - Kok bisa lebih luas dari desanya? Biasanya karena batas peta desa masih indikatif atau ada petak tanah yang tumpang tindih (*overlapping*). Mereka adalah desa beneran yang cenderung padat; kalau dibuang malah bikin median kepadatan persil bergeser **-26,9%**. Jadi mereka **tetap dipertahankan** di *fit set*.
- **Misteri Banjir Nol (21,8% / 17.415 desa):**
  - Seperlima desa punya nilai banjir = 0 di semua kelas. Masalahnya, kita tidak tahu apakah desanya benar-benar bebas banjir (mis. dataran tinggi) atau **belum sempat dipetakan** (polanya sangat kental per kabupaten/provinsi).
  - **Konsekuensi:** Data banjir **dilarang masuk sebagai input clustering** — hanya dipakai saat membaca profil klaster nanti, itu pun dengan catatan kehati-hatian ekstra.
- **Plot Twist Geometri Data (PCA Awal):**
  - Saat diintip pakai PCA pada Variant A (dua komponen utama = ~68% varians), desa-desa ternyata membentuk **awan kontinu dengan beberapa area padat**, bukan geng-geng yang langsung terpisah jauh satu sama lain.
  - Artinya: nanti kita wajib uji *cluster tendency* dan stabilitas dulu sebelum mengklaim klaster yang terbentuk adalah "tipe desa yang terpisah tegas".

---

### 4. Posisi CRISP-DM saat ini
Dalam alur standar **CRISP-DM**:
1. **Phase 1 (Business Understanding):** Selesai (`docs/CRISP_DM_UNDERSTANDING.md`).
2. **Phase 2 (Data Understanding):** Selesai (audit & eksplorasi di `pre_processing/master.ipynb` & `data/clustering_ready/BACKGROUND.md`).
3. **Phase 3 (Data Preparation):** Selesai! Semua matriks siap-pakai sudah diekspor ke `data/clustering_ready/`.
4. **Phase 4 (Modeling):** **Posisi kita sekarang — baru mau mulai!**
5. **Phase 5 (Evaluation) & Phase 6 (Deployment):** Menyusul setelah model & profil klaster matang.

---

### 5. File siap-pakai & aturan main singkat (`data/clustering_ready/`)

Kita **tidak perlu** mengulang bersih-bersih data dari `desa.xlsx`. Cukup pakai file matang di `data/clustering_ready/`:

| File | Ukuran | Gunanya Buat Apa? |
| :--- | :--- | :--- |
| `X_A_scaled.csv` | 77.770 × 8 | **Menu Utama (Default):** profil *land-tenure* saja — akar kuadrat proporsi luas 6 hak (`s_hak_milik`, `s_hgb`, `s_hgu`, `s_hak_pakai`, `s_kosong`, `s_other` [gabungan `hak_pengelolaan`, `hak_wakaf`, `lainnya` < 1%]) + `log_parcel_density` + `log_mean_parcel`. |
| `X_B_scaled.csv` | 77.098 × 10 | **Menu Pembanding (Variant B):** semua kolom Variant A + `log_luas_desa` (ukuran desa) + `log1p_age_median` (usia pendaftaran median). |
| `village_ids.csv` | 79.842 × 7 | Nama wilayah lengkap + `kab_key` (kunci aman untuk agregasi kabupaten/kota). |
| `interpretation_columns.csv` | 79.842 × 33 | **Buku contekan profiling:** proporsi mentah, banjir, RDTR, tahun pendaftaran, flag anomali — **hanya untuk membaca karakter klaster setelah terbentuk**. |
| `place_later.csv` | 2.744 × 20 | Daftar desa di luar *fit set* beserta alasannya (1.950 tanpa persil, 122 tereksklusi di Step 3, dan 672 tanpa tahun pendaftaran yang masih ada di `X_A` tapi tidak di `X_B`). |
| `decision_log.csv` | 14 keputusan | Catatan keputusan desain **D1–D14** beserta alasan dan bukti angkanya. |

**Aturan Wajib yang Harus Dijaga:**
1. **Jangan ulangi pre-processing** dan **jangan rescale ulang** `*_scaled.csv` (blok komposisi sengaja diskalakan bersama ke 5 *degrees of freedom* / ~70,1% varians supaya hak yang langka tidak ikut terinflasi bobotnya).
2. **Selalu baca `kode8` sebagai teks (`str`)**, jangan angka biasa — kalau tidak, nol di depan (`01...`) bakal hilang!
3. **Jangan masukkan kolom `interpretation_columns.csv` sebagai input clustering** (terutama banjir) tanpa mencatatnya sebagai keputusan baru (**D15+**).
4. **Jangan asal membuang atau meng-*assign* desa di `place_later.csv`**: 1.950 desa tanpa persil dilaporkan sebagai kelompok sendiri; 122 baris tereksklusi jangan di-*assign*.
5. **Setiap perubahan pada persiapan data wajib dicatat sebagai keputusan baru (`D15+`).**

---

## Step 1: Cek Ombak — Kenalan sama `X_A_scaled.csv` & Uji *Cluster Tendency*

> Notebook: `modeling/clustering.ipynb` | Hasil angka: `modeling/outputs/step1_summary.json` | Semua grafik tampil *inline* di dalam notebook

### 1. Kenalan langsung sama isi `X_A_scaled.csv`
Begitu "kulkas" `X_A_scaled.csv` dibuka, semua cek integritas lolos mulus:
- **Ukuran pas:** **77.770 desa × 8 kolom** (`62.361` Desa + `15.409` Kelurahan), **0 nilai kosong (`NaN`) / tak hingga (`Inf`)**.
- **Kode wilayah aman:** **24.852 baris** punya `kode8` yang diawali angka `0` (contoh `06010903`) dan semuanya utuh 8 digit karena dibaca sebagai teks (`str`).
- **Pembagian bobot fitur sesuai resep (`transform_recipe.json`):** 6 kolom komposisi hak tanah (`s_hak_milik`, `s_hgb`, `s_hgu`, `s_hak_pakai`, `s_kosong`, `s_other`) memegang **70,1%** total varians (tepat 5,000 unit), sedangkan 2 kolom ukuran & kepadatan (`log_parcel_density`, `log_mean_parcel`) memegang **29,9%** (2,134 unit).

Supaya nggak cuma kebayang angka abstrak, ini **5 desa nyata** yang mewakili "wajah asli" isi `X_A_scaled.csv`:

| Profil Nyata | Desa / Wilayah | Persil (Luas) | Komposisi Hak Asli |
| :--- | :--- | :--- | :--- |
| **Urban SHM + HGB** | `06010903` **Kel. Mayang Mangurai**, Kota Jambi, Jambi | 13.927 persil (693 ha) | **SHM 77,8%**, HGB 15,2%, Hak Pakai 3,6%, Kosong 3,2% |
| **Dominan Kosong** | `12301108` **Desa Arjowilangun**, Kab. Malang, Jawa Timur | 11.812 persil (1.344 ha) | **Kosong 98,4%**, SHM 1,2% |
| **Perkebunan Raksasa** | `16090306` **Desa Mulupan**, Kab. Kutai Timur, Kaltim | 32 persil (9.401 ha) | **HGU 99,98%** (hampir 100% konsesi kebun!) |
| **Dominan Hak Pakai** | `05050101` **Kel. Bangkinang**, Kab. Kampar, Riau | 5.172 persil (547 ha) | **Hak Pakai 83,8%**, Kosong 11,1%, SHM 4,9% |
| **Desa Transisi / Campuran** | `11260808` **Desa Tanjungrejo**, Kab. Purworejo, Jateng | 2.051 persil (153 ha) | **SHM 46,5%**, Kosong 40,4%, Hak Pakai 12,4% |

Kalau dilihat siapa yang paling sering jadi "penguasa lahan" (*dominant right* berdasarkan luas terbesar) di 77.770 desa:
- **Hak Milik (SHM):** 47.458 desa (**61,0%**)
- **Kosong (Belum Hak):** 24.405 desa (**31,4%**)
- **Hak Pakai:** 2.417 desa (**3,1%**)
- **HGU:** 2.281 desa (**2,9%**)
- **HGB:** 969 desa (**1,2%**)
- **Lainnya (<1%):** 240 desa (**0,3%**)

> **Gosip pentingnya:** Lebih dari **92% desa di Indonesia** panggung utamanya cuma pertarungan antara **SHM (sudah sertifikat warga)** vs **Kosong (belum bersertifikat)** — tapi yang ~7,6% sisanya (HGU, Hak Pakai, HGB) punya karakter ekstrem dan unik!

---

### 2. Ngintip "peta awan" desa lewat PCA (Sel 1.3 & 1.4 di `clustering.ipynb`)
Karena mata manusia nggak bisa lihat ruang 8 dimensi sekaligus, kita pakai **PCA** buat memadatkannya ke peta 2D–4D:
- **PC1 (39,7% varians) = Sumbu "Sudah Sertifikat vs Belum Sertifikat":**
  - Makin ke **kiri**, desa makin penuh **SHM (`s_hak_milik` loading -0,608)**.
  - Makin ke **kanan**, desa makin penuh bidang **Kosong (`s_kosong` loading +0,744)**.
- **PC2 (28,0% varians) = Sumbu "Padat Petak Kecil vs Jarang Petak Raksasa":**
  - Makin ke **bawah**, petak tanahnya makin kecil dan **super padat** (`log_parcel_density` -0,619) — di sinilah kebanyakan **Kelurahan** kota ngumpul!
  - Makin ke **atas**, ukuran petak tanahnya makin **gede-gede dan jarang** (`log_mean_parcel` +0,637) — dan ujung paling atas diisi geng perkebunan **HGU**!
- **PC3 (13,5% varians) & PC4 (7,5% varians):** Total **PC1–PC4 sudah menangkap 88,6% cerita data**. Baru di PC3 karakter **Hak Pakai (+0,749)** meledak keluar, dan di PC4 **HGU (+0,739)** & **HGB (+0,293)** makin kepisah. Jadi jangan tertipu tampilan 2D saja — geng seperti Hak Pakai bersembunyi di dimensi ke-3!

**Yang kelihatan di grafik PCA (Sel 1.3 & 1.4):**
- Ada **dua pusat keramaian yang jelas lebih padat** (warna kuning terang di *hexbin*): satu gunung di sisi kiri (geng **SHM padat**), satu lagi di kanan-bawah (geng **Kosong**), plus ekor panjang menjulang ke atas (geng **HGU**).
- Tapi di antara "gunung SHM" dan "gunung Kosong", **jembatannya penuh sesak oleh desa-desa transisi/campuran** (gradasi biru-kuning-merah di Panel 4). Tidak ada jurang kosong pemisah yang tegas!

---

### 3. Uji *Cluster Tendency*: Benar ada gengnya, atau cuma ilusi? (Sel 1.5 di `clustering.ipynb`)
Kita pakai **Hopkins Statistic ($H$)** — analoginya: kita sebar titik-titik desa "palsu" yang posisinya acak merata, lalu bandingkan jarak tetangga terdekatnya dengan jarak tetangga antar-desa asli:
- $H \approx 0{,}50$ → data menyebar acak merata (nggak ada geng).
- $H > 0{,}75$ → data ngumpul tidak merata / punya kecenderungan berkelompok kuat.

Supaya jujur dan nggak tertipu jebakan geometri (karena 6 fitur hak tanah aslinya terikat aturan total = 100%, bukan bebas di kotak 8D), kita uji pakai **3 cara** selama 10 *seed* acak ($m=500$):

| Metode Uji Hopkins | Rata-rata $H$ ($\pm$ SD) | Artinya |
| :--- | :---: | :--- |
| **1. 8D Bounding Box (naif)** | `0.9525 ± 0.0017` | Terinflasi karena ruang kotak 8D banyak ruang kosong yang mustahil ditempati proporsi |
| **2. PCA-4D (rentang p01–p99)** | `0.8863 ± 0.0024` | Jauh di atas 0,75 meski sudah dipangkas ekstremnya ke 4 sumbu utama |
| **3. Simplex-Aware Null (paling jujur)** | `0.9046 ± 0.0029` | Titik palsu dipaksa ikut aturan total share = 100% (`Dirichlet`) + `sqrt` + skala persis `transform_recipe.json`, dan hasilnya **tetap 0,905!** |

Tapi tunggu dulu — lihat grafik sebelah kiri di **Sel 1.5**:
- **Distribusi jarak berpasangan** (sampel 3.000 desa, median = `3,16`) bentuknya **satu puncak mulus (*unimodal*) dengan bahu agak landai di kanan**, bukan dua puncak tajam yang terpisah jurang.
- Sementara jarak ke tetangga ke-10 (10-NN) sangat bervariasi (median `0,28`, p10 `0,16` vs p90 `0,62`, maks `3,45`), tanda kepadatan lokalnya memang beda-beda tajam.

---

### 4. Vonis Step 1 (Bekal buat Step 2)
1. **Apakah datanya acak merata?** **TIDAK!** Hopkins jujur (`0,886–0,905`) membuktikan desa-desa Indonesia **sangat tidak merata / berkumpul di kantong-kantong kepadatan tertentu** (kantor SHM padat, kantong Kosong, ekor HGU, dll.).
2. **Apakah geng-gengnya terpisah kayak pulau-pulau berjauhan?** **JUGA TIDAK!** Peta PCA dan kurva jarak berpasangan menunjukkan **spektrum kontinu (gradasi)** antara desa SHM dan desa Kosong — artinya nanti klaster utama yang terbentuk adalah **segmentasi praktis pada sebuah kontinum + beberapa kantong khusus** (HGU, Hak Pakai, HGB).
3. **Strategi masuk Step 2:** Karena bentuknya begini, kita tidak boleh pakai satu algoritma saja! Kita akan adu 3 "mak comblang" sekaligus:
   - **K-Means** (baseline cepat, membagi wilayah jarak secara tegas),
   - **GMM (Gaussian Mixture Model)** (cocok untuk awan kontinu/lonjong karena punya probabilitas keanggotaan *soft*),
   - **HDBSCAN** (berbasis kepadatan, buat melihat geng padat mana yang muncul alami dan mana yang jadi wilayah transisi).

---

## Step 2: Adu "Mak Comblang" — Eksperimen Algoritma Clustering (K-Means, GMM, HDBSCAN) & Pilih $k$

> Notebook: `modeling/clustering.ipynb` (Sel 2.1–2.5) | Ringkasan angka: `modeling/outputs/step2_summary.json` | Semua grafik tampil *inline* di dalam notebook

### 1. Cara kerja 3 "mak comblang" yang kita adu
Supaya nggak fanatik sama satu metode, kita suruh 3 algoritma dengan karakter beda buat mengelompokkan **77.770 desa** di `X_A_scaled`:
- **K-Means ($k = 2 \dots 10$):** Memotong ruang jadi $k$ geng dengan garis batas tegas berdasarkan jarak paling dekat ke pusat geng.
- **GMM Full ($k = 2 \dots 10$):** Bentuk geng boleh lonjong/miring (*elips*) dan tiap desa dikasih skor keyakinan (*probabilitas*), jadi ketahuan berapa persen desa yang "ragu" di perbatasan.
- **HDBSCAN (4 kombinasi `min_cluster_size`):** Nggak dipaksa milih jumlah $k$ — dia cari sendiri kelompok yang benar-benar padat, dan desa yang nanggung/renggang dicap **`-1` (Noise / Transisi)**.

---

### 2. Kamus kilat metrik rapor (biar nggak bingung baca tabel)
- **Elbow (*Inertia*):** Jarak total desa ke pusat gengnya — makin banyak geng ($k$ naik), pasti makin turun; kita cari titik "siku" tempat penurunannya mulai melandai.
- **Silhouette Score (sampel 10.000 desa):** Seberapa akur desa dengan gengnya sendiri dibanding geng tetangga (*lebih tinggi = lebih bagus*, mendekati `0` = mepet/tumpang tindih).
- **Davies-Bouldin Index:** Mengukur tingkat kemiripan/tumpukan antargeng (*lebih rendah = lebih bagus*).
- **BIC (khusus GMM) & `% Desa Ragu`:** BIC menyeimbangkan kecocokan model vs kerumitan (*lebih rendah = lebih bagus*), sedangkan `% Desa Ragu` menghitung proporsi desa yang probabilitas terkuatnya `< 0,80`.

---

### 3. Hasil gosip paling panas: siapa menang & apa plot twist-nya?

1. **Plot Twist #1 — HDBSCAN membongkar "Benua Raksasa":**
   - Pada konfigurasi paling pas (`min_cluster_size=500, min_samples=50`), HDBSCAN cuma menemukan **3 kelompok padat alami** plus **19,65% desa (`15.283` desa) dicap *noise*/transisi**:
     - **C1 (`78,56%` / `61.094` desa):** Seluruh spektrum **SHM ↔ Campuran ↔ Kosong** nyambung jadi **satu benua besar tanpa jurang pemisah**!
     - **C2 (`1,03%` / `804` desa):** Pulau kecil **HGU murni** (median HGU `77,3%`).
     - **C0 (`0,76%` / `589` desa):** Pulau kecil **Hak Pakai ekstrem** (median Hak Pakai `100,0%`, median hanya `2` persil).
   - Kalau batas kepadatannya diperketat (`mcs=1000`), `84,7%` desa langsung jadi *noise*; di `mcs=2000`, `100%` jadi *noise*.
   - **Maknanya:** HDBSCAN sukses besar sebagai **detektor realitas** (membuktikan HGU & Hak Pakai ekstrem memang pulau nyata), tapi **nggak cocok jadi segmentasi kebijakan nasional** karena 78,6% desa digabung dalam satu karung raksasa + 19,7% dibiarkan tanpa label.

2. **Plot Twist #2 — GMM malah kewalahan dan tumpang tindih!**
   - Di teori, GMM sering dijagokan untuk data lonjong. Tapi begitu masuk $k \ge 3$, **Silhouette GMM anjlok drastis ke `0,04–0,075`** (bahkan minus di $k \ge 8$) dan **Davies-Bouldin bengkak ke `2,07–3,37`** (jauh lebih jelek daripada K-Means `1,06–1,39`).
   - Penyebabnya kelihatan jelas di grafik PCA (Sel 2.5 Panel 3): komponen elips GMM saling bertumpuk di ruang kontinum simplex (C1 dan C2 di kanan tumpang tindih), dan BIC terus meluncur turun sampai $k=10$ karena berusaha menambal bentuk non-Gaussian.
   - Kesepakatan (**ARI**) antara K-Means dan GMM juga rendah (`0,24–0,29`), tanda pembelahan GMM di kontinum ini kurang rapi.

3. **Pemenangnya — K-Means, dan duel seru $k = 4$ vs $k = 5$:**
   - **K-Means jauh paling rapi & konsisten:**
     - **Silhouette** puncak terbaik di **$k=3$ (`0,2953`)** dan **$k=5$ (`0,2942`)** — turun lagi kalau dipaksa ke $k=6$ (`0,2700`).
     - **Davies-Bouldin** mencapai titik **terendah terbaik tepat di $k = 5$ (`1,0600`)** sebelum naik lagi di $k=6$ (`1,1144`).
   - **Kenapa $k = 5$ jauh lebih seksi daripada $k = 4$?**
     - Antara `KM_k4` dan `KM_k5`, **ARI = `0,941`** (hampir identik!). Bedanya cuma satu langkah cerdas: di $k=4$, kelompok spesial `6,0%` masih mencampur **HGU** dan **Hak Pakai** jadi satu geng. Begitu dinaikkan ke **$k=5$**, si `6,0%` itu terbelah rapi jadi dua kantong berbeda tanpa mengganggu 3 geng utama!

---

### 4. Intipan 5 Geng K-Means ($k = 5$) di `X_A_scaled`
*(Baru intipan cepat dari Sel 2.5 — profiling lengkap pakai banjir, RDTR, tahun, dan provinsi bakal kita bedah di Step 4!)*

| Geng (`KM_k5`) | Jumlah Desa (%) | Median SHM | Median Kosong | Median HGU | Median Hak Pakai | Median Persil | % Kelurahan | Watak Awal |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **C4** | 24.860 (`31,97%`) | **92,4%** | 2,3% | 0,0% | 0,8% | 368 | 13,5% | **Matang SHM** (sudah rapi bersertifikat) |
| **C2** | 27.696 (`35,61%`) | **58,0%** | **30,8%** | 0,0% | 4,0% | **2.088** | **28,7%** | **Transisi / Urban-Padat Campuran** (persil terbanyak, banyak Kelurahan) |
| **C1** | 19.360 (`24,89%`) | 19,7% | **76,9%** | 0,0% | 0,3% | 768 | 16,8% | **Dominan Kosong / Target Utama PTSL** |
| **C3** | 3.068 (`3,94%`) | 10,4% | 7,3% | **64,2%** | 0,1% | 482 | 14,4% | **Kantong Perkebunan HGU** |
| **C0** | 2.786 (`3,58%`) | 9,6% | 0,0% | 0,0% | **70,8%** | **9** | 14,2% | **Kantong Tanah Pemerintah / Hak Pakai** |

---

### 5. Vonis Step 2 (Bekal buat Step 3)
- **Kandidat juara yang dibawa ke Step 3:** **`K-Means (k = 5)`** sebagai juara utama, dengan **`K-Means (k = 4)`** sebagai pembanding terdekat (dan catatan perilaku kontinum dari HDBSCAN).
- **Yang wajib diuji di Step 3 (Tes Anti-Goyah):** Apakah 5 geng K-Means ini konsisten kalau:
  1. Acak ulang `random_state` (*multi-seed*)?
  2. Diambil sampel acak berulang (*bootstrap*)?
  3. Dibandingkan dengan **Variant B ([X_B_scaled.csv](file:///Users/otnansirk/S2-MMI/DATA-SCIENCE/spatial-pertanahan-nasional/data/clustering_ready/X_B_scaled.csv))** yang ikut memasukkan luas desa + usia pendaftaran?
  4. Bobot blok komposisinya diubah (misal disamakan 50%:50% dengan kepadatan/ukuran)?

---

## Step 3: Tes Anti-Goyah — Uji Stabilitas & Sensitivitas

> Notebook: `modeling/clustering.ipynb` (Sel 3.1–3.3) | Ringkasan angka: `modeling/outputs/step3_summary.json` | Semua grafik tampil *inline* di dalam notebook

### 1. Empat tes ketahanan yang dijalani `K-Means (k = 5)`
Sebelum nekat memberi julukan ke 5 geng hasil Step 2, kita uji dulu seberapa anti-goyah mereka lewat **4 tes**:
1. **Multi-Seed (10× acak awal):** Kalau komputer start dari posisi awal beda, hasil gengnya berubah nggak?
2. **Bootstrap (20× kocok ulang 77.770 desa):** Kalau isi sampel desa diguncang berulang-ulang, tiap geng tetap utuh atau bubar?
3. **Variant A vs Variant B (`X_B_scaled.csv`):** Kalau luas desa + usia sertifikat ikut masuk hitungan (di 77.098 desa irisan), siapa yang bertahan dan siapa yang pindah geng?
4. **Sensitivitas Bobot Blok Komposisi (Decision D11):** Kalau jatah bobot 6 hak tanah diubah dari default `70,1%` menjadi `50/50`, `Z-score per kolom` (`75,0%`), atau `Comp=1` (`31,9%`), seberapa jauh hasilnya bergeser?

*(Ukuran kemiripan dua versi klaster pakai **ARI / Adjusted Rand Index** & **Jaccard**: `1,00` = kembar identik, `> 0,85` = super stabil, `0,60–0,75` = mirip secara garis besar tapi perbatasan bergeser, `< 0,55` = berubah cukup drastis.)*

---

### 2. Hasil Tes Internal: `k = 5` Ternyata Paling Anti-Goyah!
Kejutan manis di Sel 3.1:
- **Multi-Seed (10 seed, 45 pasang):** ARI rata-rata **`0,9890`** (minimum `0,9722`). Mau diulang dari mana saja, hasilnya nyaris identik!
- **Bootstrap (20 resamples):**
  - **`k = 5`: ARI rata-rata `0,9847`** (min `0,9735`, NMI `0,9747`) — **malah lebih stabil daripada `k = 4` (`0,9771`) maupun `k = 6` (`0,9650`)!**
  - **Ketahanan tiap geng (`k = 5`, Jaccard di 20 bootstrap):** Kelimanya tembus **`> 0,987`**!
    - `C4: Matang SHM` = **`0,9928`**
    - `C3: Perkebunan HGU` = **`0,9897`**
    - `C1: Dominan Kosong` = **`0,9877`**
    - `C0: Hak Pakai (Pem/Fasum)` = **`0,9872`**
    - `C2: Transisi / Padat` = **`0,9870`**
  - **Konsistensi per-desa:** **`97,81%` desa** selalu masuk geng yang persis sama **20 dari 20 kali** (`100%`), dan hanya **`921` desa (`1,18%`)** yang duduk di garis perbatasan (`< 80%`).

> **Kesimpulan internal:** Di dalam data Variant A, batas 5 geng K-Means ini **batu karang banget** — bukan hasil kebetulan *random seed* atau sampel!

---

### 3. Hasil Tes Sensitivitas: Drama Variant A vs B & Bobot D11
Nah, pas aturannya diganti (fitur ditambah atau bobot digeser), ini yang terbongkar di Sel 3.2–3.3:

1. **Variant A vs Variant B (`X_B_scaled.csv`, `77.098` desa irisan): `ARI = 0,6450` (NMI `0,6689`)**
   - Kenapa turun ke `0,645`? Lihat *heatmap* perpindahan anggotanya:
     - **4 geng dengan identitas kuat nyaris tidak goyah:** **`C3: Perkebunan HGU` bertahan `98,4%`**, **`C1: Dominan Kosong` `94,3%`**, **`C0: Hak Pakai` `93,1%`**, dan **`C4: Matang SHM` `86,5%`** (`12,7%` turun ke `C2`).
     - Yang goyang adalah **zona tengah kontinum (`C2: Transisi / Padat`, bertahan `78,0%`)**: **`18,3%`** anggotanya bergeser ke `C1: Dominan Kosong` ketika ukuran desa dan usia registrasi ikut menarik jarak!
     - **Catatan tambahan:** Dari **672 desa *B-only*** (yang punya persil tapi tahun registrasinya kosong/`NaN`), **`604` desa (`89,9%`) memang duduk di `C1: Dominan Kosong`** dan `64` di `C3: HGU` — masuk akal karena tanah yang belum punya sertifikat memang nggak punya tahun terbit!
   - **Artinya:** Penambahan luas desa + usia sertifikat tidak merusak kantong utama (HGU, Kosong, Hak Pakai), tapi memang menggeser garis potong di tengah kontinum SHM ↔ Kosong. Jadi **Variant A** tetap paling tepat sebagai model utama karena fokus murni ke profil hak tanah.

2. **Sensitivitas Bobot Blok Komposisi (Decision D11):**
   - **Bobot 50/50 (komposisi `50%` vs kepadatan/ukuran `50%`):** `ARI = 0,6969` (NMI `0,6772`) — garis besar masih sama, tapi HGU paling terasa bergeser (`Jaccard = 0,548`) karena faktor ukuran persil makin dominan.
   - **Bobot Z-score semua kolom (komposisi `75%`, hak langka terinflasi):** `ARI = 0,6555` (NMI `0,6583`) — geng HGU makin menguat (`0,861`), tapi zona transisi `C2` (`0,691`) tertarik oleh bobot hak langka (`HGB`, `other`).
   - **Bobot `Comp = 1` (komposisi diciutkan ke `31,9%`):** `ARI` jatuh ke **`0,5337`** (NMI `0,5115`) dan `C0: Hak Pakai` anjlok ke Jaccard **`0,360`**! Ini membuktikan keputusan **D11** di pre-processing sudah sangat pas — kalau blok komposisi diperkecil, karakter hak tanah langsung tenggelam oleh ukuran fisik & kepadatan persil.

---

### 4. Vonis Step 3 (Lampu Hijau ke Step 4!)
- **`K-Means (k = 5)` pada Variant A (`X_A_scaled.csv`) resmi lulus uji ketahanan:** super stabil secara internal (`Multi-Seed ARI 0,989`, `Bootstrap ARI 0,985`, semua geng `Jaccard > 0,987`), dan perilaku sensitivitasnya terhadap Variant B / bobot D11 sepenuhnya wajar serta bisa dijelaskan secara transparan.
- **Lanjut ke Step 4:** Saatnya buka buku contekan [interpretation_columns.csv](file:///Users/otnansirk/S2-MMI/DATA-SCIENCE/spatial-pertanahan-nasional/data/clustering_ready/interpretation_columns.csv) & [village_ids.csv](file:///Users/otnansirk/S2-MMI/DATA-SCIENCE/spatial-pertanahan-nasional/data/clustering_ready/village_ids.csv) untuk cek **apakah 5 geng ini cuma nge-copy peta provinsi (Cramér's V)** dan **membongkar profil lengkapnya (RDTR, tahun pendaftaran, tipe wilayah, dan catatan banjir)**!

---

## Step 4: Sesi Kepo — Cek Bias Geografis & Bongkar Profil Tiap Geng

> Notebook: `modeling/clustering.ipynb` (Sel 4.1–4.3) | Ringkasan angka: `modeling/outputs/step4_summary.json` | Semua grafik tampil *inline* di dalam notebook

### 1. Tes Bias Geografis: Jangan-jangan cuma nge-copy peta provinsi?
Begitu 5 geng `K-Means (k = 5)` dicocokkan dengan nama provinsi dan kabupaten di [village_ids.csv](file:///Users/otnansirk/S2-MMI/DATA-SCIENCE/spatial-pertanahan-nasional/data/clustering_ready/village_ids.csv), ini skor **Cramér's V** (*bias-corrected*) dan **NMI**-nya:

| Variabel Eksternal | Cramér's V | NMI | Artinya |
| :--- | :---: | :---: | :--- |
| **Kabupaten/Kota (506)** | `0,418` | `0,093` | Sedang — ada pola lokal per kabupaten, bukan seragam semua |
| **Provinsi (34)** | `0,325` | `0,088` | Sedang — **bukan fotokopi peta provinsi!** (>91% variasi klaster bukan sekadar label provinsi) |
| **Flag Overshoot (1–10×)** | `0,283` | `0,061` | Berkorelasi cukup nyata dengan struktur kepadatan klaster |
| **Punya Dokumen RDTR (>0)** | `0,218` | `0,026` | Kesiapan tata ruang ikut membedakan profil geng |
| **Tipe (Desa vs Kelurahan)** | `0,169` | `0,015` | Ada kecenderungan urban-rural, tapi tidak kaku |
| **Flag Flood All-Zero\* (Ambigu)** | `0,111` | `0,007` | Lemah — lebih mencerminkan pola regional pemetaan banjir |

> **Kesimpulan cek bias:** 5 geng ini **lulus** — mereka bukan sekadar peta provinsi yang diganti warna, melainkan betul-betul memotret **struktur hukum & kepadatan pertanahan**!

---

### 2. Plot Twist Terbesar di Step 4: Kenapa Jakarta & Bali Bukan di `Matang SHM`?!
Ini temuan paling "wah" begitu kita buka [interpretation_columns.csv](file:///Users/otnansirk/S2-MMI/DATA-SCIENCE/spatial-pertanahan-nasional/data/clustering_ready/interpretation_columns.csv):

- Banyak orang bakal mengira provinsi paling maju seperti **DKI Jakarta (`93,6%` desa!)**, **Bali (`89,9%`)**, **DIY (`82,6%`)**, **Jateng (`75,0%`)**, dan **Jatim (`70,6%`)** ada di geng `C4: Matang SHM`. **Ternyata mereka ngumpul di `C2: Transisi / Padat`!**
- **Kenapa?** Karena di Jawa–Bali–Perkotaan, hampir seluruh permukaan desanya **sudah penuh dipetakan** (median **`2.088` persil** dalam desa yang mungil `268,7 ha`, median **`coverage` = `0,896`**, **`23,5%` mengalami *overshoot***, sejarah sertifikat tertua sejak **`1977`**, dan paling siap tata ruang: **`28,1%` punya RDTR** dengan median cakupan `98,5%`!). Karena bidangnya ribuan dan sangat aktif, masih ada sisa **~31% bidang `Kosong`** plus porsi **HGB** & **Hak Pakai** yang belum rampung.
- Sebaliknya, geng **`C4: Matang SHM`** (tinggi di **Bengkulu `60,7%`**, **Sulbar `55,3%`**, **Lampung `53,5%`**, **NTT `53,4%`**, **Sulteng `52,9%`**) memang punya **median SHM `92,4%`** di antara bidang tanah yang *sudah* tergambar di peta BPN, **TAPI** jumlah persilnya relatif sedikit (median **`368` persil** di desa seluas `783,6 ha`, **`coverage` cuma `0,163` = `16,3%` luas desa!**). Artinya, di luar bidang SHM yang sudah tercatat itu, masih banyak wilayah desa yang belum masuk peta persil (mis. kawasan hutan/non-persil atau belum terpetakan).

> **Pelajaran emas:** Tanpa cek `interpretation_columns.csv`, kita bisa salah menyimpulkan tingkat kesiapan *Desa Lengkap* antara `C4` vs `C2`!

---

### 3. Rapor Lengkap 5 Geng (di luar fitur input model)

| Geng (Jumlah Desa, %) | Watak Inti | Fisik & Kepadatan | Tata Ruang & Kronologi | Provinsi Menonjol & Contoh Desa Paling Tipikal |
| :--- | :--- | :--- | :--- | :--- |
| **C4: Matang SHM**<br>*(24.860 desa / `31,97%`)* | **Med SHM `92,4%`**, Kosong `2,3%` | `13,5%` Kel., med luas `784 ha`, **`368` persil**, `coverage 0,163`, overshoot `1,1%` | RDTR `10,2%`; tahun `1994`–`2025` (med `2017`); flood-zero `20,6%` | **Bengkulu (`60,7%`), Sulbar (`55,3%`), Lampung (`53,5%`), NTT (`53,4%`)**.<br>*Contoh:* `03070102` **Desa LADANG PANJANG** (Pasaman, Sumbar — SHM `94,0%`) & `20160814` **Desa Kalibong** (Bone, Sulsel — SHM `94,4%`). |
| **C2: Transisi / Padat**<br>*(27.696 desa / `35,61%`)* | **Med SHM `58,0%`**, **Kosong `30,8%`**, Pakai `4,0%` | **`28,7%` Kel.**, desa kecil `269 ha`, **`2.088` persil**, **`coverage 0,896`**, **overshoot `23,5%`** | **RDTR `28,1%`** (med `98,5%`); tertua **`1977`–`2026`** (med `2018`); flood-zero `20,3%` | **DKI Jakarta (`93,6%`), Bali (`89,9%`), DIY (`82,6%`), Jateng (`75,0%`), Jatim (`70,6%`)**.<br>*Contoh:* `11310813` **Desa Pekiringanalit** (Pekalongan, Jateng — SHM `59,3%`, Kosong `34,1%`) & `18010810` **Kel. PANIKI SATU** (Manado, Sulut). |
| **C1: Dominan Kosong**<br>*(19.360 desa / `24,89%`)* | **Med Kosong `76,9%`**, SHM `19,7%` | `16,8%` Kel., med luas `703 ha`, `768` persil, `coverage 0,786`, overshoot `18,0%` | RDTR `12,9%`; tahun muda `1996`–`2025` (med **`2020`**); `3,1%` tanpa tahun; flood-zero `22,2%` | **Kaltim (`52,0%`), Riau (`51,7%`), Sumbar (`49,8%`), Kalteng (`47,8%`)**; terbanyak di Aceh (`1.892`) & Sumut (`1.442`).<br>*Contoh:* `21160209` **Desa WADIABERO** (Buton Tengah, Sultra — Kosong `79,4%`) & `01140314` **Desa Blang Muko** (Nagan Raya, Aceh). |
| **C3: Perkebunan HGU**<br>*(3.068 desa / `3,94%`)* | **Med HGU `64,2%`**, SHM `10,4%`, Kosong `7,3%` | `14,4%` Kel., **raksasa `4.045 ha`**, `482` persil, `coverage 0,522`, **overshoot `20,6%`** | RDTR `8,9%`; tahun `1996`–`2025` (med `2018`); flood-zero terendah **`6,1%`** | **Kalbar (`23,1%`, lift `5,85×`), Kaltim (`22,1%`), Kalteng (`16,8%`), Kaltara (`15,7%`), Babel (`12,4%`)**.<br>*Contoh:* `15130708` **Desa SIONG** (Barito Timur, Kalteng — HGU `67,7%`) & `14071209` **Desa BAYUN SARI** (Ketapang, Kalbar). |
| **C0: Hak Pakai (Pem/Fasum)**<br>*(2.786 desa / `3,58%`)* | **Med Pakai `70,8%`**, SHM `9,6%`, Kosong `0,0%` | `14,2%` Kel., `543 ha`, **cuma `9` persil**, **`coverage 0,007`**, overshoot `1,2%` | RDTR `9,0%`; paling baru **`2014`–`2024`** (rentang `9` thn); **flood-zero tertinggi `38,7%`** | **Papua (`27,5%`, lift `7,68×`), Papua Barat (`15,4%`), NTT (`10,6%`), Sumut (`8,4%`), Maluku (`7,4%`)**.<br>*Contoh:* `26011305` **Desa SOSIRI** (Jayapura, Papua — Hak Pakai `80,5%`) & `19081119` **Desa salepae** (Parigi Moutong, Sulteng). |

*(Catatan wajib soal banjir: Variasi `flood_all_zero%` dari `6,1%` di C3 sampai `38,7%` di C0 **tidak boleh** disimpulkan sebagai bukti perbedaan risiko banjir fisik, karena `21,8%` nilai nol pada data banjir bersifat ambigu secara regional — lihat Step 0 & README).*

---

### 4. Vonis Step 4 (Tinggal Selangkah Menuju Finish!)
Kelima geng kini sudah **punya bukti kuat, anti-goyah, bebas bias provinsi semata, dan profil kebijakannya super jelas** — termasuk temuan krusial soal *coverage* antara `C4` vs `C2` dan posisi `C1` sebagai prioritas utama sertifikasi PTSL!

Di **Step 5 (Final)** kita tinggal:
1. Memberi **julukan resmi** yang mudah dipahami pembuat kebijakan untuk tiap geng,
2. Menggabungkan seluruh **79.842 desa** dengan melaporkan kelompok **`place_later.csv`** secara eksplisit (**1.950 desa tanpa persil** sebagai kelompok ke-6 *"Belum Terpetakan"* + **122 baris tereksklusi** sebagai *"Perlu Audit Data"*),
3. Mengekspor tabel hasil segmentasi akhir & merangkum **rekomendasi prioritas kebijakan ATR/BPN**.
