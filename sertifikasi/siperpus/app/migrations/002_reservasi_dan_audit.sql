-- =====================================================================
-- Migrasi 002 - v1.1.0: fitur reservasi (antrian) + audit log keamanan
-- Unit J.620100.047.01 - Melakukan Pembaharuan Perangkat Lunak
-- Unit J.620100.043.01 - Analisis dampak: lihat docs/ANALISIS_DAMPAK.md
-- Perubahan bersifat ADITIF (tabel baru) -> tidak merusak data/fitur v1.0.0
-- =====================================================================

CREATE TABLE reservasi (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    anggota_id     INTEGER NOT NULL REFERENCES anggota(id) ON DELETE CASCADE,
    buku_id        INTEGER NOT NULL REFERENCES buku(id)    ON DELETE CASCADE,
    tgl_reservasi  TEXT    NOT NULL DEFAULT (datetime('now')),
    status         TEXT    NOT NULL DEFAULT 'menunggu'
                   CHECK (status IN ('menunggu', 'terpenuhi', 'batal'))
);
CREATE INDEX idx_reservasi_buku_status ON reservasi(buku_id, status);

-- Satu anggota hanya boleh punya satu reservasi aktif untuk buku yang sama
CREATE UNIQUE INDEX uq_reservasi_aktif ON reservasi(anggota_id, buku_id) WHERE status = 'menunggu';

-- Jejak audit (J.62090.011.01 - akuntabilitas, ISO/IEC 27001 A.8.15 Logging)
CREATE TABLE audit_log (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    aksi    TEXT    NOT NULL,
    detail  TEXT,
    ip      TEXT,
    waktu   TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_audit_waktu ON audit_log(waktu);
