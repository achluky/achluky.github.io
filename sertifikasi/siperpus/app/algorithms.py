"""Struktur data & algoritma yang dipakai aplikasi.

Unit J.620100.004.02 - Menggunakan Struktur Data
  list, tuple, dict, set, deque (antrian FIFO), heap (priority queue), dataclass.
Unit J.620100.022.02 - Mengimplementasikan Algoritma Pemrograman
  validasi checksum, perhitungan denda (percabangan), binary search, merge sort,
  top-N dengan heap, rekomendasi berbasis irisan himpunan. Kompleksitas dicatat
  pada docstring setiap fungsi.
"""
import heapq
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date


# ---------------------------------------------------------------------------
# 1. Validasi ISBN-13  -- O(n), n = 13
# ---------------------------------------------------------------------------
def validasi_isbn13(isbn: str) -> bool:
    """Checksum ISBN-13: bobot 1,3,1,3,... ; (jumlah) mod 10 harus 0.

    Invarian loop: `total` = jumlah berbobot digit ke-0 .. ke-(i-1).
    """
    isbn = isbn.replace("-", "").strip()
    if len(isbn) != 13 or not isbn.isdigit():
        return False
    total = 0
    for i, ch in enumerate(isbn):
        total += int(ch) * (1 if i % 2 == 0 else 3)
    return total % 10 == 0


def normalisasi_isbn(isbn: str) -> str:
    return isbn.replace("-", "").strip()


# ---------------------------------------------------------------------------
# 2. Perhitungan denda -- O(1)
# ---------------------------------------------------------------------------
def hitung_denda(jatuh_tempo: date, tgl_kembali: date, tarif_per_hari: int, maksimum: int) -> int:
    """Denda = hari_terlambat x tarif, dibatasi `maksimum`. Tidak terlambat -> 0."""
    if tarif_per_hari < 0 or maksimum < 0:
        raise ValueError("Tarif dan batas denda tidak boleh negatif")
    terlambat = (tgl_kembali - jatuh_tempo).days
    if terlambat <= 0:
        return 0
    return min(terlambat * tarif_per_hari, maksimum)


# ---------------------------------------------------------------------------
# 3. Binary search -- O(log n), data harus terurut
# ---------------------------------------------------------------------------
def binary_search(data_terurut: list, target) -> int:
    """Mengembalikan indeks target atau -1.

    Invarian: jika target ada, maka indeksnya berada di [kiri, kanan].
    Varian  : (kanan - kiri) berkurang setiap iterasi -> loop pasti berhenti.
    """
    kiri, kanan = 0, len(data_terurut) - 1
    while kiri <= kanan:
        tengah = (kiri + kanan) // 2
        if data_terurut[tengah] == target:
            return tengah
        if data_terurut[tengah] < target:
            kiri = tengah + 1
        else:
            kanan = tengah - 1
    return -1


# ---------------------------------------------------------------------------
# 4. Merge sort (stabil) -- O(n log n) waktu, O(n) memori
# ---------------------------------------------------------------------------
def merge_sort(items: list, key=lambda x: x, reverse=False) -> list:
    if len(items) <= 1:
        return list(items)
    tengah = len(items) // 2
    kiri = merge_sort(items[:tengah], key, reverse)
    kanan = merge_sort(items[tengah:], key, reverse)
    hasil, i, j = [], 0, 0
    while i < len(kiri) and j < len(kanan):
        a, b = key(kiri[i]), key(kanan[j])
        ambil_kiri = a >= b if reverse else a <= b
        if ambil_kiri:
            hasil.append(kiri[i])
            i += 1
        else:
            hasil.append(kanan[j])
            j += 1
    hasil.extend(kiri[i:])
    hasil.extend(kanan[j:])
    return hasil


# ---------------------------------------------------------------------------
# 5. Top-N dengan heap -- O(n log k)
# ---------------------------------------------------------------------------
def top_n(frekuensi: dict, n: int) -> list:
    """Mengambil n item dengan frekuensi terbesar: [(item, jumlah), ...]."""
    return heapq.nlargest(n, frekuensi.items(), key=lambda kv: kv[1])


# ---------------------------------------------------------------------------
# 6. Rekomendasi "yang meminjam buku ini juga meminjam" -- dict of set
# ---------------------------------------------------------------------------
def rekomendasi(riwayat: list, buku_id: int, n: int = 3) -> list:
    """riwayat: list of tuple (anggota_id, buku_id).

    1) bangun indeks buku -> set(anggota) (dict of set, O(m))
    2) peminjam buku target = himpunan P
    3) skor buku lain = |P ∩ peminjam(buku lain)|  (irisan set)
    """
    peminjam = defaultdict(set)
    for anggota_id, b_id in riwayat:
        peminjam[b_id].add(anggota_id)
    target = peminjam.get(buku_id, set())
    skor = {b: len(target & a) for b, a in peminjam.items() if b != buku_id and target & a}
    return [b for b, _ in top_n(skor, n)]


# ---------------------------------------------------------------------------
# 7. Antrian reservasi FIFO -- deque: enqueue/dequeue O(1)
# ---------------------------------------------------------------------------
@dataclass
class AntrianReservasi:
    buku_id: int
    _antrian: deque = field(default_factory=deque)

    def tambah(self, anggota_id: int) -> int:
        if anggota_id in self._antrian:
            raise ValueError("Anggota sudah ada di antrian")
        self._antrian.append(anggota_id)
        return len(self._antrian)

    def layani(self):
        return self._antrian.popleft() if self._antrian else None

    def posisi(self, anggota_id: int) -> int:
        return list(self._antrian).index(anggota_id) + 1 if anggota_id in self._antrian else -1

    def __len__(self):
        return len(self._antrian)
