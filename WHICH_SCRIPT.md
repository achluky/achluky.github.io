# 🚀 Quick Guide: Pilih Script yang Tepat

## ❓ Script Mana yang Harus Saya Gunakan?

### 📊 Pilihan Script:

```
achluky.github.io/
├── update_publications.py         ❌ JANGAN GUNAKAN (versi lama, sering error)
├── update_publications_v2.py      ✅ GUNAKAN INI! (dengan proxy & retry)
├── simple_update.py               ✅ Alternatif (tanpa proxy, lebih lambat)
└── data/publications.json         ✅ Edit manual jika script gagal
```

---

## 🎯 Rekomendasi Berdasarkan Situasi

### Situasi 1: Setup Pertama Kali (Banyak Publikasi)
**Gunakan:** `update_publications_v2.py`

```bash
python3 update_publications_v2.py
# Pilih opsi 1
```

**Kenapa?**
- Punya proxy support (lebih sukses)
- Auto-retry jika gagal
- Bisa handle banyak publikasi

---

### Situasi 2: Script V2 Gagal / Kena Blocking
**Gunakan:** `simple_update.py`

```bash
python3 simple_update.py
```

**Kenapa?**
- Lebih lambat = lebih aman
- Tanpa proxy = lebih stabil
- Limit 10 publikasi terbaru saja

---

### Situasi 3: Semua Script Gagal
**Gunakan:** Manual Entry

```bash
# Cara 1: Via script
python3 update_publications.py
# Pilih opsi 2 (Manual entry)

# Cara 2: Edit langsung
open data/publications.json
# atau
code data/publications.json
```

---

### Situasi 4: Update Rutin (1-2 Publikasi Baru per Bulan)
**Gunakan:** Edit Manual

```bash
open data/publications.json
```

Tambahkan entry baru:
```json
{
  "title": "Judul Paper Baru",
  "authors": "Ahmad Luky Ramdani, ...",
  "venue": "Nama Konferensi",
  "year": 2026,
  "citations": 0,
  "pdfUrl": "",
  "type": "conference"
}
```

**Kenapa?**
- Lebih cepat (2 menit)
- Tidak ada resiko blocking
- Kontrol penuh atas data

---

## ⚡ Langkah Cepat (TL;DR)

### Opsi A: Auto-Fetch (5-10 menit)
```bash
cd ~/achluky.github.io
python3 update_publications_v2.py
# Pilih 1
# Tunggu proses selesai
git add data/publications.json
git commit -m "Update publications"
git push
```

### Opsi B: Manual (2 menit)
```bash
cd ~/achluky.github.io
open data/publications.json
# Edit, tambah publikasi
git add data/publications.json
git commit -m "Add new publication"
git push
```

---

## 🔄 Workflow Kombinasi (RECOMMENDED!)

**Setup Awal:**
1. Gunakan `update_publications_v2.py` untuk fetch semua publikasi existing
2. Jika gagal, gunakan `simple_update.py`
3. Jika tetap gagal, manual entry untuk 5-10 publikasi penting

**Update Rutin:**
1. Manual entry setiap ada publikasi baru (paling cepat!)
2. Atau jalankan `simple_update.py` setiap 3-6 bulan sekali

---

## 📝 Template Copy-Paste untuk Manual Entry

```json
{
  "title": "",
  "authors": "Ahmad Luky Ramdani, ",
  "venue": "",
  "year": 2026,
  "citations": 0,
  "pdfUrl": "",
  "type": "journal"
}
```

---

## ✅ Checklist Setelah Update

- [ ] File `data/publications.json` ada dan valid
- [ ] Test di browser: `http://localhost:8888/https://scholar.google.com/citations?user=gjOzo9MAAAAJ&hl=en`
- [ ] Data tampil dengan benar
- [ ] Commit dan push ke GitHub
- [ ] Verifikasi di: `https://achluky.github.io/https://scholar.google.com/citations?user=gjOzo9MAAAAJ&hl=en`

---

## 🆘 Jika Masih Error

1. **Baca:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - solusi lengkap untuk semua error
2. **Coba:** Manual entry terlebih dahulu
3. **Tunggu:** 24 jam lalu coba auto-fetch lagi
4. **Email:** ahmadluky@sd.itera.ac.id

---

## 💯 Rekomendasi Final

**Untuk kemudahan jangka panjang:**

1. ✅ **Setup awal:** Gunakan `update_publications_v2.py` (1x saja)
2. ✅ **Update rutin:** Edit manual `data/publications.json` (paling praktis!)
3. ✅ **Setiap 6 bulan:** Run `simple_update.py` untuk update citations count

**Alasan:**
- Manual entry hanya 2 menit per publikasi
- Tidak ada resiko blocking
- Lebih cepat daripada troubleshooting auto-fetch

---

**Created**: 2026-05-28  
**Author**: Ahmad Luky Ramdani
