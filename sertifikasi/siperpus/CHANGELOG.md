# Changelog

Format mengikuti [Keep a Changelog](https://keepachangelog.com/id-ID/1.1.0/) dan [Semantic Versioning](https://semver.org/lang/id/).

## [1.1.0] - 2026-10-28
### Ditambahkan
- Fitur reservasi buku dengan antrian FIFO (tabel `reservasi`, struktur `AntrianReservasi`).
- Audit log aktivitas pengguna (tabel `audit_log`, halaman `/admin/audit`).
- Halaman monitor resource `/admin/monitor` dan health-check `/health`.
- Pembatasan percobaan login (5 kali gagal / 5 menit).
### Diubah
- `kembalikan_buku()` kini mengembalikan `(denda, anggota_berikutnya)`.
### Diperbaiki
- BUG-02: validasi CSRF lolos ketika sesi belum memiliki token.
- BUG-04: backup tidak lagi dibuat untuk database baru.
### Keamanan
- Dependensi diperbarui: Flask 3.0.3, Werkzeug 3.0.6 (hasil `pip-audit`).

## [1.0.0] - 2026-09-15
### Ditambahkan
- Skema awal: users, kategori, buku, anggota, peminjaman + trigger stok + view peminjaman aktif.
- CRUD buku & anggota, peminjaman/pengembalian dengan denda, laporan.
- Login berbasis role (admin, petugas), CSRF, security headers.
