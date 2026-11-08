"""Seluruh perintah SQL aplikasi (DML & query).

Unit J.620100.020.02 - Menggunakan SQL: SELECT, INSERT, UPDATE, DELETE, JOIN,
  GROUP BY/HAVING, subquery (NOT EXISTS), fungsi agregat, fungsi tanggal, VIEW.
Unit J.620100.021.02 - Menerapkan Akses Basis Data: parameter binding & transaksi.
"""
import sqlite3
from datetime import date, timedelta

from flask import current_app

from . import algorithms as algo
from .db import execute, query, transaction

# Whitelist kolom ORDER BY: nama kolom tidak bisa di-bind sebagai parameter,
# jadi input pengguna dipetakan ke nilai yang sudah pasti aman.
URUTAN_BUKU = {"judul": "b.judul", "tahun": "b.tahun DESC", "stok": "b.stok DESC", "terbaru": "b.id DESC"}


class AturanBisnisError(Exception):
    """Pelanggaran aturan bisnis yang pesannya aman ditampilkan ke pengguna."""


# ----------------------------- Kategori & Buku -----------------------------
def list_kategori():
    return query("SELECT id, nama FROM kategori ORDER BY nama")


def list_buku(keyword="", kategori_id=None, urut="judul"):
    sql = """
        SELECT b.id, b.isbn, b.judul, b.penulis, b.tahun, b.stok, k.nama AS kategori
        FROM buku b JOIN kategori k ON k.id = b.kategori_id
        WHERE (b.judul LIKE :kw OR b.penulis LIKE :kw OR b.isbn LIKE :kw)
    """
    params = {"kw": f"%{keyword}%"}
    if kategori_id:
        sql += " AND b.kategori_id = :kat"
        params["kat"] = kategori_id
    sql += " ORDER BY " + URUTAN_BUKU.get(urut, URUTAN_BUKU["judul"])
    return query(sql, params)


def get_buku(buku_id):
    return query(
        "SELECT b.*, k.nama AS kategori FROM buku b JOIN kategori k ON k.id = b.kategori_id WHERE b.id = ?",
        (buku_id,), one=True,
    )


def isbn_sudah_ada(isbn, kecuali_id=None):
    """Contoh pemakaian binary search pada daftar ISBN terurut.
    (Di level DB keunikan tetap dijamin oleh UNIQUE index.)"""
    rows = query("SELECT isbn FROM buku WHERE id != ? ORDER BY isbn", (kecuali_id or 0,))
    return algo.binary_search([r["isbn"] for r in rows], isbn) != -1


def simpan_buku(data, buku_id=None):
    params = (data["isbn"], data["judul"], data["penulis"], data["penerbit"],
              data["tahun"], data["kategori_id"], data["stok"])
    if buku_id:
        execute("""UPDATE buku SET isbn=?, judul=?, penulis=?, penerbit=?, tahun=?, kategori_id=?, stok=?
                   WHERE id=?""", params + (buku_id,))
        return buku_id
    return execute("""INSERT INTO buku (isbn, judul, penulis, penerbit, tahun, kategori_id, stok)
                      VALUES (?, ?, ?, ?, ?, ?, ?)""", params)


def hapus_buku(buku_id):
    try:
        execute("DELETE FROM buku WHERE id = ?", (buku_id,))
    except sqlite3.IntegrityError:
        raise AturanBisnisError("Buku memiliki riwayat peminjaman sehingga tidak dapat dihapus")


def rekomendasi_untuk(buku_id):
    riwayat = [(r["anggota_id"], r["buku_id"]) for r in query("SELECT anggota_id, buku_id FROM peminjaman")]
    ids = algo.rekomendasi(riwayat, buku_id)
    if not ids:
        return []
    placeholder = ",".join("?" * len(ids))
    rows = {r["id"]: r for r in query(f"SELECT id, judul, penulis FROM buku WHERE id IN ({placeholder})", ids)}
    return [rows[i] for i in ids if i in rows]


# --------------------------------- Anggota ---------------------------------
def list_anggota():
    return query("""
        SELECT a.*, (SELECT COUNT(*) FROM peminjaman p
                     WHERE p.anggota_id = a.id AND p.status = 'dipinjam') AS pinjam_aktif
        FROM anggota a ORDER BY a.nama
    """)


def tambah_anggota(no_anggota, nama, email, telepon):
    try:
        return execute("INSERT INTO anggota (no_anggota, nama, email, telepon) VALUES (?, ?, ?, ?)",
                       (no_anggota, nama, email or None, telepon or None))
    except sqlite3.IntegrityError:
        raise AturanBisnisError("Nomor anggota atau email sudah terdaftar")


# -------------------------------- Sirkulasi --------------------------------
def list_peminjaman_aktif():
    return query("SELECT * FROM v_peminjaman_aktif ORDER BY tgl_jatuh_tempo")


def pinjam_buku(anggota_id, buku_id, petugas_id, hari_ini=None):
    cfg = current_app.config
    hari_ini = hari_ini or date.today()
    jatuh_tempo = hari_ini + timedelta(days=cfg["LAMA_PINJAM_HARI"])
    with transaction():
        anggota = query("SELECT aktif FROM anggota WHERE id = ?", (anggota_id,), one=True)
        if anggota is None or not anggota["aktif"]:
            raise AturanBisnisError("Anggota tidak ditemukan / tidak aktif")
        aktif = query("SELECT COUNT(*) AS n FROM peminjaman WHERE anggota_id = ? AND status = 'dipinjam'",
                      (anggota_id,), one=True)["n"]
        if aktif >= cfg["MAKS_PINJAM_AKTIF"]:
            raise AturanBisnisError(f"Batas peminjaman aktif ({cfg['MAKS_PINJAM_AKTIF']} buku) tercapai")
        try:
            pid = execute("""INSERT INTO peminjaman (anggota_id, buku_id, petugas_id, tgl_pinjam, tgl_jatuh_tempo)
                             VALUES (?, ?, ?, ?, ?)""",
                          (anggota_id, buku_id, petugas_id, hari_ini.isoformat(), jatuh_tempo.isoformat()))
        except sqlite3.IntegrityError as exc:  # RAISE(ABORT) dari trigger trg_cek_stok
            raise AturanBisnisError("Stok buku habis, silakan buat reservasi") from exc
        execute("""UPDATE reservasi SET status = 'terpenuhi'
                   WHERE anggota_id = ? AND buku_id = ? AND status = 'menunggu'""", (anggota_id, buku_id))
    return pid


def kembalikan_buku(peminjaman_id, hari_ini=None):
    """Mengembalikan (denda, anggota_id_reservasi_berikutnya | None)."""
    cfg = current_app.config
    hari_ini = hari_ini or date.today()
    with transaction():
        p = query("SELECT * FROM peminjaman WHERE id = ? AND status = 'dipinjam'", (peminjaman_id,), one=True)
        if p is None:
            raise AturanBisnisError("Data peminjaman tidak ditemukan atau sudah dikembalikan")
        denda = algo.hitung_denda(date.fromisoformat(p["tgl_jatuh_tempo"]), hari_ini,
                                  cfg["DENDA_PER_HARI"], cfg["DENDA_MAKSIMUM"])
        execute("UPDATE peminjaman SET status = 'kembali', tgl_kembali = ?, denda = ? WHERE id = ?",
                (hari_ini.isoformat(), denda, peminjaman_id))
        antrian = antrian_reservasi(p["buku_id"])
        berikutnya = antrian.layani()
    return denda, berikutnya


def antrian_reservasi(buku_id):
    antrian = algo.AntrianReservasi(buku_id)
    for r in query("""SELECT anggota_id FROM reservasi WHERE buku_id = ? AND status = 'menunggu'
                      ORDER BY tgl_reservasi, id""", (buku_id,)):
        antrian.tambah(r["anggota_id"])
    return antrian


def buat_reservasi(anggota_id, buku_id):
    try:
        execute("INSERT INTO reservasi (anggota_id, buku_id) VALUES (?, ?)", (anggota_id, buku_id))
    except sqlite3.IntegrityError:
        raise AturanBisnisError("Anggota sudah memiliki reservasi aktif untuk buku ini")
    return antrian_reservasi(buku_id).posisi(anggota_id)


def list_reservasi():
    return query("""
        SELECT r.id, r.tgl_reservasi, a.nama AS nama_anggota, b.judul
        FROM reservasi r JOIN anggota a ON a.id = r.anggota_id JOIN buku b ON b.id = r.buku_id
        WHERE r.status = 'menunggu' ORDER BY b.judul, r.tgl_reservasi
    """)


# --------------------------------- Laporan ---------------------------------
def statistik_dashboard():
    return query("""
        SELECT (SELECT COUNT(*) FROM buku)                                   AS total_judul,
               (SELECT COALESCE(SUM(stok), 0) FROM buku)                      AS total_stok,
               (SELECT COUNT(*) FROM anggota WHERE aktif = 1)                 AS anggota_aktif,
               (SELECT COUNT(*) FROM peminjaman WHERE status = 'dipinjam')    AS dipinjam,
               (SELECT COUNT(*) FROM v_peminjaman_aktif WHERE hari_terlambat > 0) AS terlambat
    """, one=True)


def buku_terpopuler(limit=5):
    rows = query("""
        SELECT b.judul, COUNT(p.id) AS jumlah
        FROM buku b JOIN peminjaman p ON p.buku_id = b.id
        GROUP BY b.id
    """)
    return algo.top_n({r["judul"]: r["jumlah"] for r in rows}, limit)


def anggota_dengan_denda(minimal=1):
    return query("""
        SELECT a.no_anggota, a.nama, COUNT(p.id) AS kali_terlambat, SUM(p.denda) AS total_denda
        FROM anggota a JOIN peminjaman p ON p.anggota_id = a.id
        WHERE p.denda > 0
        GROUP BY a.id
        HAVING SUM(p.denda) >= ?
        ORDER BY total_denda DESC
    """, (minimal,))


def peminjaman_per_bulan():
    return query("""
        SELECT strftime('%Y-%m', tgl_pinjam) AS bulan, COUNT(*) AS jumlah
        FROM peminjaman GROUP BY bulan ORDER BY bulan
    """)


def buku_tidak_pernah_dipinjam():
    return query("""
        SELECT b.isbn, b.judul, b.penulis FROM buku b
        WHERE NOT EXISTS (SELECT 1 FROM peminjaman p WHERE p.buku_id = b.id)
        ORDER BY b.judul
    """)


# -------------------------------- Pengguna ---------------------------------
def get_user_by_username(username):
    return query("SELECT * FROM users WHERE username = ?", (username,), one=True)


def list_audit(limit=100):
    return query("""
        SELECT l.waktu, COALESCE(u.username, '-') AS username, l.aksi, l.detail, l.ip
        FROM audit_log l LEFT JOIN users u ON u.id = l.user_id
        ORDER BY l.id DESC LIMIT ?
    """, (limit,))
