# Panduan Presentasi & Q&A: Analisis Spasial Pertanahan Nasional

> Contekan cepat sebelum maju presentasi — mencakup kalimat pembuka 30 detik (*"gunanya apa?"*), kerangka 9 slide mengikuti alur CRISP-DM, 8 pertanyaan jebakan penguji beserta jawaban berbasis angka terverifikasi, dan daftar file hasil akhir.

---

## 1. Kalimat Pembuka 30 Detik ("Gunanya Apa Sih?")

> *"Indonesia punya **79.842 desa/kelurahan** dengan kondisi pertanahan yang sangat jomplang. Selama ini target sertifikasi tanah (PTSL) sering dibagi secara agregat tanpa membedakan karakter desanya. Proyek ini memetakan seluruh 79.842 desa ke dalam **5 segmen profil pertanahan + 2 grup khusus** agar Kementerian ATR/BPN bisa **menargetkan anggaran dan jenis intervensi yang tepat sasaran per kabupaten/kota**—tahu persis mana desa yang tinggal terbit sertifikat, mana yang butuh pemetaan baru, mana yang butuh penertiban HGU, dan mana yang butuh audit data peta."*

---

## 2. Kerangka Slide Presentasi (9 Slide, Alur CRISP-DM)

| Slide | Judul Slide | Isi Inti & Grafik Rujukan (`modeling/clustering.ipynb`) |
| :---: | :--- | :--- |
| **1** | **Latar Belakang & Masalah Kebijakan** | Konteks ATR/BPN (PTSL, Desa Lengkap, RDTR), `79.842` desa, 3 masalah utama: disparitas spasial, anomali peta (`13,8%` *overshoot*), dan belum adanya tipologi objektif. |
| **2** | **Data & Temuan Audit Kualitas** | Ringkas `data/desa.xlsx` (33 kolom) + temuan audit: `122` anomali dikeluarkan (`G7`), `1.950` desa nol persil dipisah (`G6`), `21,8%` banjir nol ambigu → disimpan hanya untuk interpretasi. |
| **3** | **Strategi Persiapan Data (`X_A_scaled`)** | Kenapa pakai **Variant A** (8 fitur *size-neutral*: 6 `sqrt` proporsi luas hak + `log` kepadatan & ukuran persil), bukan nilai absolut atau `CLR`, dan kenapa tidak di-*rescale* ulang (`decision_log.csv` D1–D14). |
| **4** | **Step 1: Struktur Ruang Data (PCA & Hopkins)** | Grafik **Sel 1.3–1.4 (PCA)** + **Sel 1.5 (Hopkins)**. Pesan utama: *Hopkins jujur `0,886–0,905`* (sangat tidak acak), tetapi bentuknya **kontinum SHM ↔ Kosong** + ekor khusus (HGU & Hak Pakai). |
| **5** | **Step 2: Perbandingan Algoritma & Pemilihan $k$** | Grafik **Sel 2.3 (Metrik $k$)** + **Sel 2.5 (4 Peta PCA)**. Pesan utama: HDBSCAN buktikan kontinum (`78,6%` nyambung + pulau HGU/Hak Pakai), GMM tumpang tindih (*Silhouette* `0,04–0,075`), **`K-Means (k=5)` paling rapi & tajam** (*Davies-Bouldin* terendah `1,060`). |
| **6** | **Step 3: Uji Stabilitas & Sensitivitas** | Grafik **Sel 3.3 (4 Panel Anti-Goyah)**. Pesan utama: internal super kokoh (*Multi-Seed* `0,989`, *Bootstrap* `0,985`, `97,81%` desa tidak pernah pindah), serta sensitivitas Variant A vs B (`0,645`) & bobot D11 dijelaskan transparan. |
| **7** | **Step 4: Profil 5 Segmen & Peta 34 Provinsi** | Grafik **Sel 4.3 (Profil + Peta 34 Provinsi)**. Soroti **Cramér's V provinsi = `0,325`** (bukan fotokopi peta!) dan ***plot twist* `S1` (Jawa–Bali, *coverage* `89,6%`) vs `S2` (SHM tinggi, *coverage* `16,3%`)**. |
| **8** | **Step 5: Peta Nasional & Rekomendasi Kebijakan** | Grafik **Sel 5.2 (Rekonsiliasi 79.842 Desa + Top-10 Kab/Kota PTSL)**. Tampilkan 7 grup + 3 *hotspot* kabupaten (PTSL: Aceh Timur `242`, Kuansing `78,0%`; Pemetaan Awal: Manokwari `243`; Audit: Bengkulu `22` eksklusi + `48` *overshoot*). |
| **9** | **Batasan Jujur & Langkah Lanjutan** | 4 batasan jujur (kontinum, banjir nol ambigu, sensitivitas proporsi luas vs cacah persil, konfirmasi pemilik data) + rencana integrasi data elevasi & geometri poligon. |

---

## 3. 8 Hal yang perlu di perhatikan

### 1. "Gunanya clustering ini apa? Kenapa nggak cukup urutkan `% tanah kosong` di Excel aja?"
Kalau cuma mengurutkan `% kosong`, desa yang `kosong`-nya rendah (`2%`) bakal dicampur aduk semua! Padahal desa yang `kosong`-nya rendah bisa jadi **Desa SHM Parsial (`S2`)**, bisa jadi **Perkebunan HGU raksasa (`S4`)**, atau **Desa Papua yang baru punya 9 persil Hak Pakai (`S5`)**. Intervensi kebijakannya berbeda total—itulah sebabnya dibutuhkan segmentasi multivariat (8 fitur sekaligus).

### 2. "Kenapa Silhouette Score K-Means cuma `0,294`? Bukannya itu kecil?"
Nilai Silhouette `~0,29` justru **konsisten dengan geometri asli data**. Di Step 1 dan Step 2 terbukti lewat PCA, distribusi jarak unimodal, dan HDBSCAN bahwa desa-desa SHM–Kosong membentuk **spektrum kontinu (gradasi)**, bukan pulau-pulau kosong yang terpisah jurang. Pada data kontinum sosial-spasial, Silhouette memang tidak akan `> 0,7`. Karena itu kita tidak mengandalkan satu metrik saja: kita buktikan kecenderungan berkelompoknya lewat **Simplex-Aware Hopkins (`0,905`)**, pemisahan terbaik lewat **Davies-Bouldin (`1,060`)**, dan ketahanannya lewat **Bootstrap ARI (`0,985`, semua klaster Jaccard `> 0,987`)**.

### 3. "Kenapa pilih K-Means `k=5`, bukan GMM atau HDBSCAN yang lebih modern?"
Ketiganya sudah diuji secara empiris di Step 2:
- **HDBSCAN** (`mcs=500, ms=50`) menggabungkan `78,6%` desa ke satu klaster raksasa dan menandai `19,7%` sebagai *noise*—sangat berguna sebagai validasi struktur (membuktikan HGU & Hak Pakai pulau kepadatan nyata), tapi tidak bisa dipakai langsung untuk segmentasi kebijakan nasional.
- **GMM Full** mengalami tumpang tindih elips pada kontinum simplex (*Silhouette* turun ke `0,04–0,075`, *Davies-Bouldin* naik ke `2,07–3,37`).
- **`K-Means (k=5)`** unggul di metrik jarak, paling stabil saat di-*bootstrap* (`0,985` > `k=4` `0,977` > `k=6` `0,965`), dan memisahkan kantong HGU (`3,9%`) dari Hak Pakai (`3,6%`) secara bersih.

### 4. "Kok DKI Jakarta (`93,6%`) dan Bali (`89,9%`) malah masuk `S1 (Transisi/Padat)`, bukan `S2 (Dominan SHM)`?"
Justru itu **temuan paling berharga** dari proyek ini. Di Jakarta & Bali (`S1`), hampir seluruh desa sudah dipetakan (**median `2.088` persil**, **`coverage 89,6%`**, RDTR tertinggi `28,1%`), namun karena sangat padat masih tersisa ~31% persil kosong/belum tuntas. Sebaliknya di `S2` (mis. Bengkulu, Sulbar, NTT), `92,4%` bidang yang *sudah terpetakan* memang SHM, **tetapi *coverage*-nya baru `16,3%`** (median hanya `368` persil). Tanpa clustering + validasi eksternal, pengambil kebijakan bisa keliru menganggap `S2` sudah lebih "lengkap" daripada Jawa–Bali.

### 5. "Kenapa banjir, RDTR, sama tahun pendaftaran nggak dimasukkan jadi fitur clustering?"
Sesuai **Decision D12**:
- `21,8%` desa punya nilai banjir nol yang **ambigu** (tidak rawan vs belum terpetakan, sangat regional)—kalau dimasukkan malah merusak klaster;
- RDTR baru tersedia pada `~17%` desa;
- Tahun pendaftaran *missing* (MNAR) pada desa tanpa sertifikat.
Dengan menyimpannya di luar model (`interpretation_columns.csv`), ketiganya justru berfungsi sebagai **validasi eksternal yang independen**.

### 6. "Kenapa `1.950` desa nol persil dan `122` baris anomali nggak di-imputasi aja?"
Untuk `1.950` desa tanpa persil, proporsi hak tanah bernilai `0/0` (tidak terdefinisi). Mengisinya dengan rata-rata sama saja **mengarang nasib pertanahan desa tersebut**. Lebih jujur dan operasional melaporkannya sebagai grup terpisah **`G6: Belum Terpetakan`** (target survei dasar, mis. `243` desa di Manokwari), dan `122` baris anomali sebagai **`G7: Audit Data Spasial`** (mis. `22` desa luas=0 di Bengkulu).

### 7. "Jangan-jangan 5 klaster ini cuma memisahkan batas provinsi?"
Sudah diuji dengan **Cramér's V** di Step 4: asosiasinya dengan `provinsi` hanya **`0,325`** (**NMI = `0,088`**), artinya **>91% informasi klaster tidak dijelaskan oleh label provinsi**. Konsentrasi regional memang ada secara wajar (HGU di Kalimantan, padat di Jawa–Bali), tetapi klaster terbentuk dari struktur hak & kepadatan persil, bukan fotokopi peta administratif.

### 8. "Kalau variabel luas desa & usia sertifikat dimasukkan (Variant B), apakah kesimpulannya berubah total?"
Tidak berubah total (**`ARI = 0,645`** pada `77.098` desa irisan). Empat segmen berkarakter kuat tetap bertahan sangat tinggi (**`S4 HGU 98,4%`**, **`S3 Prioritas PTSL 94,3%`**, **`S5 Hak Pakai 93,1%`**, **`S2 SHM Parsial 86,5%`**). Yang bergeser hanya perbatasan zona tengah `S1` (`78,0%`). Karena itu **Variant A** dipilih sebagai model utama agar tipologi tetap murni berbasis profil hak tanah tanpa bias ukuran fisik desa.

---

## 4. Ringkasan 4 Batasan Jujur (*Honest Limitations*) & File Hasil Akhir

1. **Kontinum, bukan pulau terpisah:** `S1`–`S2`–`S3` adalah segmentasi kebijakan di atas spektrum kontinu SHM ↔ Kosong (sedangkan `S4` dan `S5` adalah kantong kepadatan nyata).
2. **Sensitivitas proporsi:** Hasil didasarkan pada proporsi **luas persil** (Variant A); memakai proporsi **jumlah persil** (`rho = 0,621`) atau menambah ukuran/usia (**Variant B**, `ARI = 0,645`) akan menggeser batas zona transisi.
3. **Banjir nol ambigu (`21,8%`):** Jangan mengklaim perbedaan angka banjir antarklaster sebagai bukti bahaya banjir fisik sebelum dikonfirmasi pemilik data atau dibandingkan dengan data elevasi.
4. **Kunci kabupaten & asumsi kolom:** `kab_key` masih membagi Kab. Bogor ke dua kode lama, dan definisi kolom sumber (`kosong`, satuan $m^2$, `rdtr_luas`, `banjir_*`, `tahun_*`) menunggu konfirmasi pemilik data.

**File Deliverable:**
- Notebook analisis lengkap (Step 1–5, seluruh grafik *inline*): `modeling/clustering.ipynb`
- Tabel tipologi final 79.842 desa: `modeling/outputs/desa_tipologi_final.csv`
- Tabel prioritas 506 Kabupaten/Kota (`kab_key`): `modeling/outputs/kabupaten_prioritas.csv`
- Catatan belajar langkah-demi-langkah: `docs/CATATAN_BELAJAR.md`
