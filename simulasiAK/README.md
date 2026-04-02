# Simulasi Perhitungan Target Angka Kredit (AK) Dosen

Aplikasi web untuk simulasi perhitungan Target Angka Kredit (AK) untuk pengajuan kenaikan jabatan dosen berdasarkan Kepmen Nomor 39/M/KEP/2026.

## Fitur Utama

✅ **Perhitungan AK Konversi** dari SKP (Sasaran Kinerja Pegawai)  
✅ **Perhitungan AK Prestasi** dari penelitian/publikasi ilmiah  
✅ **Pengecekan Syarat** kenaikan jabatan otomatis  
✅ **Validasi Proporsi** AK penelitian (minimal 35%)  
✅ **Status Eligible** untuk uji kompetensi  
✅ **Interface Responsif** dan user-friendly

## Cara Menggunakan

### 1. Buka Aplikasi
- Klik dua kali file `index.html` atau
- Buka file `index.html` dengan browser (Chrome, Firefox, Edge, Safari)

### 2. Input Data Dasar
- Masukkan nama dosen
- Pilih jabatan saat ini (Asisten Ahli, Lektor, atau Lektor Kepala)
- Masukkan AK saat ini (contoh: 150)
- Pilih jabatan target (Lektor, Lektor Kepala, atau Profesor)
- Masukkan target AK (contoh: 200)

### 3. Input Data SKP
- Pilih predikat SKP tahun 2023
- Pilih predikat SKP tahun 2024
- Opsi: Sangat Baik, Baik, Cukup, Kurang

### 4. Tambah Penelitian/Publikasi
- Klik tombol "+ Tambah Penelitian"
- Pilih jenis publikasi (Buku, Jurnal, Prosiding, HKI, dll)
- Masukkan jumlah penulis
- Pilih posisi penulis (Tunggal, Pertama, Kedua, atau Anggota)
- Pilih apakah Anda penulis korespondensi (Ya/Tidak)
- Ulangi untuk setiap publikasi yang dimiliki

### 5. Hitung AK
- Klik tombol "Hitung Angka Kredit"
- Lihat hasil perhitungan lengkap:
  - AK Konversi dari SKP
  - AK Prestasi dari penelitian
  - Rekapitulasi AK kumulatif
  - Pengecekan syarat dan proporsi
  - Status eligible/tidak eligible

## Contoh Penggunaan

**Kasus: Ibu Dina**
- Jabatan: Asisten Ahli (AK 150)
- Target: Lektor (AK 200)
- SKP 2023: Baik
- SKP 2024: Sangat Baik
- Publikasi:
  1. Jurnal SINTA 3 - 2 Penulis - Penulis Pertama + Korespondensi (60%)
  2. Jurnal SINTA 4 - 3 Penulis - Penulis Pertama + Korespondensi (60%)

**Hasil:**
- AK Konversi: 31,25 AK
- AK Prestasi: 12 AK (SINTA 3) + 12 AK (SINTA 4) = 24 AK
- Total AK: 205,25 AK
- **Status: ELIGIBLE** ✓

## Basis Perhitungan

### Koefisien AK per Tahun
- Asisten Ahli: 12,5 AK/tahun
- Lektor: 12,5 AK/tahun
- Lektor Kepala: 12,5 AK/tahun

### Konversi Predikat SKP
- Sangat Baik: 150%
- Baik: 100%
- Cukup: 75%
- Kurang: 50%

### Nilai Publikasi (Maksimal)

#### Buku
- Buku Referensi: 40 AK
- Monograf: 40 AK
- Book Chapter Internasional: 15 AK
- Book Chapter Nasional: 10 AK

#### Jurnal Internasional
- Jurnal Internasional Bereputasi Q1: 40 AK
- Jurnal Internasional Bereputasi Q2: 38 AK
- Jurnal Internasional Bereputasi Q3: 35 AK
- Jurnal Internasional Bereputasi Q4: 33 AK
- Jurnal Internasional Bereputasi Lainnya: 30 AK

#### Jurnal Nasional
- Jurnal Nasional SINTA 1 & 2: 25 AK
- Jurnal Nasional SINTA 3 & 4: 20 AK
- Jurnal Nasional SINTA 5 & 6: 15 AK
- Jurnal Nasional Tidak Terakreditasi: 10 AK

#### Diseminasi
- Prosiding Internasional Terindeks Bereputasi: 20 AK
- Prosiding Internasional Tidak Terindeks: 10 AK
- Prosiding Nasional: 7.5 AK
- Seminar/Lokakarya Internasional: 5 AK
- Seminar/Lokakarya Nasional: 3 AK
- Media Populer: 2 AK

#### HKI (Hak Kekayaan Intelektual)
- Paten Internasional (Diterapkan): 60 AK
- Paten Internasional: 50 AK
- Paten Nasional (Diterapkan): 40 AK
- Paten Nasional: 30 AK
- Paten Sederhana: 20 AK
- Hak Cipta/Desain Industri: 15 AK
- Karya Inovasi Berdampak: 40 AK

#### Kebijakan
- Rumusan Kebijakan Internasional: 20 AK
- Rumusan Kebijakan Nasional: 15 AK
- Rumusan Kebijakan Lokal: 10 AK

### Proporsi Penulis

#### Untuk 1 Penulis (Tunggal)
- Penulis Tunggal: 100%

#### Untuk 2 Penulis
- Penulis Pertama + Korespondensi: 60%
- Penulis Pertama (bukan korespondensi): 50%
- Penulis Kedua + Korespondensi: 50%
- Penulis Kedua: 40%

#### Untuk 3+ Penulis
- Penulis Pertama + Korespondensi: 60%
- Penulis Korespondensi (bukan pertama): 40%
- Penulis Pertama (bukan korespondensi): 40%
- Penulis Anggota Lainnya: Sisanya dibagi rata

## Syarat Kenaikan Jabatan

1. ✅ SKP minimal "Baik" selama 2 tahun terakhir
2. ✅ Memiliki minimal 1 publikasi ilmiah
3. ✅ Proporsi AK penelitian minimal 35% dari total AK yang dibutuhkan
4. ✅ Total AK kumulatif mencapai target jabatan

## File Aplikasi

- `index.html` - Halaman utama aplikasi
- `styles.css` - Styling dan tampilan
- `script.js` - Logika perhitungan
- `README.md` - Panduan penggunaan (file ini)

## Teknologi

- HTML5
- CSS3
- JavaScript (Vanilla JS, tanpa framework)

## Browser yang Didukung

- Google Chrome (Rekomendasi)
- Mozilla Firefox
- Microsoft Edge
- Safari
- Opera

## Catatan

- Aplikasi ini berjalan sepenuhnya di browser (client-side)
- Tidak memerlukan koneksi internet setelah dibuka
- Tidak ada data yang dikirim ke server
- Semua perhitungan dilakukan secara lokal

## Lisensi

Aplikasi ini dibuat untuk keperluan simulasi dan edukasi. Silakan digunakan dan dimodifikasi sesuai kebutuhan.

---
**Versi:** 1.0  
**Terakhir Diperbarui:** April 2026
