"""Data contoh untuk development/staging. JANGAN dijalankan di production."""
import sqlite3
from datetime import date, timedelta

from flask import current_app
from werkzeug.security import generate_password_hash

from .db import execute, query, transaction

KATEGORI = ["Basis Data", "Pemrograman", "Rekayasa Perangkat Lunak", "Keamanan Informasi"]

# (isbn, judul, penulis, penerbit, tahun, kategori, stok)
BUKU = [
    ("9780073523323", "Database System Concepts", "Silberschatz, Korth, Sudarshan", "McGraw-Hill", 2019, 0, 3),
    ("9780321884497", "Fundamentals of Database Systems", "Elmasri & Navathe", "Pearson", 2015, 0, 2),
    ("9781491954249", "Learning SQL", "Alan Beaulieu", "O'Reilly", 2020, 0, 4),
    ("9781491991732", "Flask Web Development", "Miguel Grinberg", "O'Reilly", 2018, 1, 2),
    ("9781593279288", "Python Crash Course", "Eric Matthes", "No Starch Press", 2019, 1, 1),
    ("9780132350884", "Clean Code", "Robert C. Martin", "Prentice Hall", 2008, 2, 2),
    ("9780135957059", "The Pragmatic Programmer", "Hunt & Thomas", "Addison-Wesley", 2019, 2, 1),
    ("9781119096726", "The Web Application Hacker's Handbook", "Stuttard & Pinto", "Wiley", 2011, 3, 1),
]

ANGGOTA = [
    ("A-0001", "Rina Wulandari", "rina@example.com", "081200000001"),
    ("A-0002", "Budi Santoso", "budi@example.com", "081200000002"),
    ("A-0003", "Sari Melati", "sari@example.com", "081200000003"),
    ("A-0004", "Dedi Pratama", "dedi@example.com", None),
]


def seed_data():
    if current_app.config["ENV_NAME"] == "production":
        raise RuntimeError("Seed data tidak boleh dijalankan di production")
    with transaction():
        if query("SELECT 1 FROM users LIMIT 1", one=True):
            return
        execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("admin", generate_password_hash("Admin#2026"), "admin"))
        execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                ("petugas", generate_password_hash("Petugas#2026"), "petugas"))
        kat_ids = [execute("INSERT INTO kategori (nama) VALUES (?)", (k,)) for k in KATEGORI]
        buku_ids = [
            execute("""INSERT INTO buku (isbn, judul, penulis, penerbit, tahun, kategori_id, stok)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""", (i, j, p, pb, t, kat_ids[k], s))
            for i, j, p, pb, t, k, s in BUKU
        ]
        ang_ids = [execute("INSERT INTO anggota (no_anggota, nama, email, telepon) VALUES (?, ?, ?, ?)", a)
                   for a in ANGGOTA]

        # Riwayat peminjaman: (anggota, buku, mundur_hari, dikembalikan_setelah_hari | None)
        riwayat = [(0, 0, 40, 6), (0, 3, 38, 12), (1, 0, 30, 7), (1, 3, 29, 9), (2, 2, 25, 5),
                   (2, 0, 20, 10), (3, 5, 15, 7), (0, 2, 10, None), (1, 6, 9, None), (2, 3, 3, None)]
        hari_ini = date.today()
        for a, b, mundur, kembali in riwayat:
            pinjam = hari_ini - timedelta(days=mundur)
            tempo = pinjam + timedelta(days=current_app.config["LAMA_PINJAM_HARI"])
            pid = execute("""INSERT INTO peminjaman (anggota_id, buku_id, petugas_id, tgl_pinjam, tgl_jatuh_tempo)
                             VALUES (?, ?, 2, ?, ?)""",
                          (ang_ids[a], buku_ids[b], pinjam.isoformat(), tempo.isoformat()))
            if kembali is not None:
                tgl_kembali = pinjam + timedelta(days=kembali)
                denda = max(0, (tgl_kembali - tempo).days) * current_app.config["DENDA_PER_HARI"]
                execute("UPDATE peminjaman SET status='kembali', tgl_kembali=?, denda=? WHERE id=?",
                        (tgl_kembali.isoformat(), denda, pid))
        try:
            execute("INSERT INTO reservasi (anggota_id, buku_id) VALUES (?, ?)", (ang_ids[3], buku_ids[6]))
        except sqlite3.OperationalError:
            pass  # tabel reservasi belum ada (skema v1.0.0)
