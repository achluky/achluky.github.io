-- =====================================================================
-- Migrasi 001 - Skema awal SIPERPUS (v1.0.0)
-- Unit J.620100.007.01 - Mengimplementasikan Rancangan Entitas & Keterkaitan
-- Unit J.620100.020.02 - Menggunakan SQL (DDL: tabel, constraint, index, view, trigger)
-- Normalisasi: 3NF (kategori dipisah dari buku, transaksi dipisah dari anggota/buku)
-- =====================================================================

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK (role IN ('admin', 'petugas')),
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE kategori (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT    NOT NULL UNIQUE
);

CREATE TABLE buku (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn        TEXT    NOT NULL UNIQUE CHECK (length(isbn) = 13),
    judul       TEXT    NOT NULL,
    penulis     TEXT    NOT NULL,
    penerbit    TEXT,
    tahun       INTEGER CHECK (tahun BETWEEN 1900 AND 2100),
    kategori_id INTEGER NOT NULL REFERENCES kategori(id) ON UPDATE CASCADE ON DELETE RESTRICT,
    stok        INTEGER NOT NULL DEFAULT 0 CHECK (stok >= 0),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE anggota (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    no_anggota TEXT    NOT NULL UNIQUE,
    nama       TEXT    NOT NULL,
    email      TEXT    UNIQUE,
    telepon    TEXT,
    tgl_daftar TEXT    NOT NULL DEFAULT (date('now')),
    aktif      INTEGER NOT NULL DEFAULT 1 CHECK (aktif IN (0, 1))
);

-- Entitas asosiatif: relasi M:N anggota <-> buku
CREATE TABLE peminjaman (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    anggota_id      INTEGER NOT NULL REFERENCES anggota(id) ON DELETE RESTRICT,
    buku_id         INTEGER NOT NULL REFERENCES buku(id)    ON DELETE RESTRICT,
    petugas_id      INTEGER NOT NULL REFERENCES users(id),
    tgl_pinjam      TEXT    NOT NULL DEFAULT (date('now')),
    tgl_jatuh_tempo TEXT    NOT NULL,
    tgl_kembali     TEXT,
    denda           INTEGER NOT NULL DEFAULT 0 CHECK (denda >= 0),
    status          TEXT    NOT NULL DEFAULT 'dipinjam' CHECK (status IN ('dipinjam', 'kembali')),
    CHECK (tgl_jatuh_tempo >= tgl_pinjam)
);

-- Index untuk kolom yang sering difilter / di-join
CREATE INDEX idx_buku_judul         ON buku(judul);
CREATE INDEX idx_buku_kategori      ON buku(kategori_id);
CREATE INDEX idx_peminjaman_status  ON peminjaman(status);
CREATE INDEX idx_peminjaman_anggota ON peminjaman(anggota_id);
CREATE INDEX idx_peminjaman_buku    ON peminjaman(buku_id);

-- Trigger menjaga konsistensi stok di level database
CREATE TRIGGER trg_cek_stok BEFORE INSERT ON peminjaman
BEGIN
    SELECT RAISE(ABORT, 'Stok buku habis')
    WHERE (SELECT stok FROM buku WHERE id = NEW.buku_id) < 1;
END;

CREATE TRIGGER trg_kurangi_stok AFTER INSERT ON peminjaman
BEGIN
    UPDATE buku SET stok = stok - 1 WHERE id = NEW.buku_id;
END;

CREATE TRIGGER trg_tambah_stok AFTER UPDATE OF status ON peminjaman
WHEN OLD.status = 'dipinjam' AND NEW.status = 'kembali'
BEGIN
    UPDATE buku SET stok = stok + 1 WHERE id = NEW.buku_id;
END;

-- View peminjaman aktif (JOIN 4 tabel)
CREATE VIEW v_peminjaman_aktif AS
SELECT p.id, p.tgl_pinjam, p.tgl_jatuh_tempo,
       a.no_anggota, a.nama AS nama_anggota,
       b.isbn, b.judul,
       u.username AS petugas,
       CAST(julianday('now') - julianday(p.tgl_jatuh_tempo) AS INTEGER) AS hari_terlambat
FROM peminjaman p
JOIN anggota a ON a.id = p.anggota_id
JOIN buku    b ON b.id = p.buku_id
JOIN users   u ON u.id = p.petugas_id
WHERE p.status = 'dipinjam';
