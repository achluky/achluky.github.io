"""Unit test algoritma & struktur data (J.620100.022.02, J.620100.004.02, J.620100.025.02)."""
from datetime import date

import pytest

from app import algorithms as algo


@pytest.mark.parametrize("isbn,valid", [
    ("9780132350884", True),
    ("978-0-13-235088-4", True),
    ("9780132350885", False),   # checksum salah
    ("978013235088", False),    # 12 digit
    ("97801323508X4", False),   # bukan angka
])
def test_validasi_isbn13(isbn, valid):
    assert algo.validasi_isbn13(isbn) is valid


@pytest.mark.parametrize("kembali,harapan", [
    (date(2026, 1, 10), 0),       # tepat waktu
    (date(2026, 1, 5), 0),        # lebih awal
    (date(2026, 1, 13), 3000),    # terlambat 3 hari
    (date(2026, 4, 1), 50000),    # dibatasi maksimum
])
def test_hitung_denda(kembali, harapan):
    assert algo.hitung_denda(date(2026, 1, 10), kembali, 1000, 50000) == harapan


def test_hitung_denda_tarif_negatif():
    with pytest.raises(ValueError):
        algo.hitung_denda(date(2026, 1, 1), date(2026, 1, 2), -1, 100)


def test_binary_search():
    data = [2, 5, 8, 12, 16, 23, 38]
    assert algo.binary_search(data, 23) == 5
    assert algo.binary_search(data, 2) == 0
    assert algo.binary_search(data, 38) == 6
    assert algo.binary_search(data, 7) == -1
    assert algo.binary_search([], 1) == -1


def test_merge_sort_stabil_dan_reverse():
    data = [("b", 2), ("a", 1), ("c", 2), ("d", 3)]
    assert algo.merge_sort(data, key=lambda x: x[1]) == [("a", 1), ("b", 2), ("c", 2), ("d", 3)]
    assert [x[1] for x in algo.merge_sort(data, key=lambda x: x[1], reverse=True)] == [3, 2, 2, 1]


def test_top_n():
    assert algo.top_n({"A": 5, "B": 9, "C": 1}, 2) == [("B", 9), ("A", 5)]


def test_rekomendasi():
    riwayat = [(1, 10), (1, 20), (2, 10), (2, 20), (2, 30), (3, 40)]
    assert algo.rekomendasi(riwayat, 10) == [20, 30]
    assert algo.rekomendasi(riwayat, 99) == []


def test_antrian_fifo():
    q = algo.AntrianReservasi(buku_id=1)
    q.tambah(7)
    q.tambah(8)
    assert q.posisi(8) == 2
    with pytest.raises(ValueError):
        q.tambah(7)
    assert q.layani() == 7
    assert q.layani() == 8
    assert q.layani() is None
