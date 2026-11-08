# Rancangan Entitas & Keterkaitan (ERD) — SIPERPUS

> Unit **J.620100.007.01** – Mengimplementasikan Rancangan Entitas dan Keterkaitan Antar Entitas
> Implementasi fisik: `app/migrations/001_skema_awal.sql`, `app/migrations/002_reservasi_dan_audit.sql`

## 1. Diagram

```mermaid
erDiagram
    KATEGORI ||--o{ BUKU : "mengelompokkan"
    ANGGOTA  ||--o{ PEMINJAMAN : "melakukan"
    BUKU     ||--o{ PEMINJAMAN : "dipinjam dalam"
    USERS    ||--o{ PEMINJAMAN : "mencatat (petugas)"
    ANGGOTA  ||--o{ RESERVASI : "mengantre"
    BUKU     ||--o{ RESERVASI : "diantre"
    USERS    |o--o{ AUDIT_LOG : "tercatat pada"

    KATEGORI { int id PK  text nama UK }
    BUKU { int id PK  text isbn UK  text judul  text penulis  text penerbit  int tahun  int kategori_id FK  int stok }
    ANGGOTA { int id PK  text no_anggota UK  text nama  text email UK  text telepon  text tgl_daftar  int aktif }
    USERS { int id PK  text username UK  text password_hash  text role }
    PEMINJAMAN { int id PK  int anggota_id FK  int buku_id FK  int petugas_id FK  text tgl_pinjam  text tgl_jatuh_tempo  text tgl_kembali  int denda  text status }
    RESERVASI { int id PK  int anggota_id FK  int buku_id FK  text tgl_reservasi  text status }
    AUDIT_LOG { int id PK  int user_id FK  text aksi  text detail  text ip  text waktu }
```

## 2. Kamus entitas & kardinalitas

| Relasi | Kardinalitas | Implementasi | Aturan referensial |
|---|---|---|---|
| kategori – buku | 1 : N | `buku.kategori_id → kategori.id` | `ON DELETE RESTRICT` (kategori yang masih dipakai tidak bisa dihapus) |
| anggota – buku (meminjam) | **M : N** | entitas asosiatif `peminjaman` | `ON DELETE RESTRICT` (riwayat transaksi dilindungi) |
| users – peminjaman | 1 : N | `peminjaman.petugas_id` | jejak siapa yang mencatat |
| anggota – buku (reservasi) | M : N | entitas asosiatif `reservasi` | `ON DELETE CASCADE` |
| users – audit_log | 1 : N (opsional) | `audit_log.user_id` | `ON DELETE SET NULL` (log tetap ada) |

## 3. Normalisasi

| Bentuk | Pemeriksaan pada SIPERPUS |
|---|---|
| **1NF** | Semua kolom atomik; tidak ada kolom berulang seperti `buku1, buku2` pada anggota — dipindah ke tabel `peminjaman`. |
| **2NF** | Setiap tabel memakai PK tunggal (surrogate key `id`), jadi tidak ada ketergantungan parsial. |
| **3NF** | Nama kategori tidak disimpan di `buku` (dipisah ke `kategori`); data anggota/buku tidak diduplikasi di `peminjaman`; nilai turunan seperti `hari_terlambat` dihitung di VIEW, tidak disimpan. |

Pengecualian yang disengaja: `peminjaman.denda` disimpan sebagai **snapshot** saat pengembalian, sehingga perubahan tarif denda di masa depan tidak mengubah histori.

## 4. Integritas data di level database

- `PRIMARY KEY`, `UNIQUE` (isbn, no_anggota, email, username)
- `CHECK` (stok ≥ 0, tahun 1900–2100, role, status, panjang ISBN = 13, jatuh tempo ≥ tanggal pinjam)
- `FOREIGN KEY` + `PRAGMA foreign_keys = ON` di setiap koneksi (`app/db.py`)
- Trigger `trg_cek_stok`, `trg_kurangi_stok`, `trg_tambah_stok` menjaga konsistensi stok
- Partial unique index `uq_reservasi_aktif`: satu reservasi aktif per anggota per buku
