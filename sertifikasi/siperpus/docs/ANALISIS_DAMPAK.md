# Analisis Dampak Perubahan — v1.0.0 → v1.1.0

> Unit **J.620100.043.01** – Menganalisis Dampak Perubahan Terhadap Aplikasi

## 1. Permintaan perubahan (Change Request CR-002)

| Item | Isi |
|---|---|
| Pemohon | Kepala Perpustakaan |
| Kebutuhan | (a) Anggota dapat **mereservasi** buku yang stoknya habis, dilayani urut kedatangan (FIFO). (b) Setiap aksi penting tercatat di **audit log**. |
| Prioritas | Sedang |
| Target rilis | v1.1.0 |

## 2. Identifikasi komponen terdampak

| Lapisan | Komponen | Jenis perubahan | Dampak |
|---|---|---|---|
| Database | tabel `reservasi`, `audit_log`, 3 index baru | **Tambah** (migrasi 002) | Tidak mengubah tabel lama → data v1.0.0 aman |
| Database | trigger stok | Tidak berubah | – |
| Struktur data | `AntrianReservasi` (deque) | Tambah | – |
| Repository | `pinjam_buku()` | **Ubah**: tandai reservasi anggota sebagai `terpenuhi` | Perlu regresi test peminjaman |
| Repository | `kembalikan_buku()` | **Ubah**: kembalikan anggota berikutnya di antrian | Signature return berubah `int → (int, int\|None)` → **pemanggil wajib disesuaikan** (`views/sirkulasi.py`) |
| Repository | `buat_reservasi()`, `list_reservasi()`, `list_audit()` | Tambah | – |
| Keamanan | `audit()` dipanggil di seluruh view | Ubah | +1 INSERT per aksi → beban tulis naik sedikit |
| View/Template | `buku_detail.html`, `sirkulasi.html`, `audit.html` | Ubah/Tambah | UI baru |
| Seed | `seed_data()` | Ubah | Harus kompatibel dengan skema v1.0.0 (`try/except OperationalError`) |
| Test | test reservasi, audit, migrasi | Tambah | – |

## 3. Matriks dampak

| Aspek | Tingkat | Keterangan |
|---|---|---|
| Fungsional | Sedang | Alur pinjam/kembali berubah sedikit |
| Data | **Rendah** | Perubahan aditif, tidak ada kolom dihapus/diubah |
| Kinerja | Rendah | +1 query di `kembalikan_buku`, +1 INSERT audit per aksi; diberi index `idx_reservasi_buku_status`, `idx_audit_waktu` |
| Keamanan | Positif | Akuntabilitas meningkat (audit log) |
| Pengguna | Rendah | Menu baru "Audit" khusus admin |
| Downtime | ± 1 menit | Saat migrasi di production |

## 4. Risiko & mitigasi

| Risiko | Mitigasi |
|---|---|
| Migrasi gagal di tengah jalan | Migrasi dijalankan dalam satu transaksi + backup otomatis (`app/migrate.py`) |
| Pemanggil `kembalikan_buku` lama rusak karena return berubah | Dicari semua pemanggil (`grep -rn kembalikan_buku`) dan diperbarui; test `test_kembali_terlambat_menghasilkan_denda` |
| Tabel `audit_log` membesar | Index pada `waktu`; rencana arsip bulanan |
| Rollback diperlukan | Restore file backup `perpus_prod.backup-<timestamp>.db` + deploy ulang tag `v1.0.0` |

## 5. Rekomendasi
Perubahan **disetujui** untuk dirilis sebagai *minor version* (1.0.0 → 1.1.0) karena bersifat kompatibel ke belakang (*backward compatible*) di level data. Rilis dilakukan ke **staging** terlebih dahulu, diuji, kemudian ke **production** mengikuti prosedur di `README.md` → *Prosedur Pembaharuan*.
