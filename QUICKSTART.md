# 🚀 Quick Start - Update Publikasi

## Cara Tercepat (2 menit)

### 1️⃣ Edit File JSON Langsung

```bash
# Buka file
open data/publications.json

# Atau edit di VS Code
code data/publications.json
```

**Tambahkan publikasi baru:**
```json
{
  "title": "Judul Paper Anda",
  "authors": "Ahmad Luky Ramdani, Co-Author",
  "venue": "Nama Konferensi/Jurnal",
  "year": 2025,
  "citations": 0,
  "pdfUrl": "",
  "type": "journal"
}
```

### 2️⃣ Commit & Push

```bash
git add data/publications.json
git commit -m "Add new publication"
git push
```

### 3️⃣ Lihat Hasil

Buka: https://achluky.github.io/https://scholar.google.com/citations?user=gjOzo9MAAAAJ&hl=en

---

## Cara Auto-Update dari Google Scholar

### Install Library

```bash
pip install scholarly
```

### Jalankan Script

```bash
python update_publications.py
# Pilih opsi 1 (Auto-fetch)
```

### Push Changes

```bash
git add data/publications.json
git commit -m "Update publications from Scholar"
git push
```

---

## 📝 Template Copy-Paste

### Untuk Publikasi:
```json
{
  "title": "",
  "authors": "Ahmad Luky Ramdani, ",
  "venue": "",
  "year": 2025,
  "citations": 0,
  "pdfUrl": "",
  "type": "journal"
}
```

### Untuk Presentasi:
```json
{
  "title": "",
  "event": "",
  "date": "2025-06-15",
  "location": "",
  "slidesUrl": ""
}
```

---

## 🔄 Auto-Update Mingguan (Optional)

File `.github/workflows/update-publications.yml` sudah tersedia.

GitHub Actions akan:
- Auto-update setiap Senin jam 00:00 UTC
- Fetch data dari Google Scholar
- Commit otomatis jika ada perubahan

**Cara aktifkan:**
1. Push file workflow ke GitHub
2. Buka tab "Actions" di GitHub repository
3. Klik "Enable workflows"

---

## ❓ FAQ Cepat

**Q: Publikasi tidak muncul?**
A: Cek browser console (F12) untuk error messages

**Q: Format JSON error?**
A: Validate di https://jsonlint.com/

**Q: Cara tambah link PDF?**
A: Isi field `pdfUrl` dengan URL lengkap

**Q: Auto-update tidak jalan?**
A: Install library `scholarly`: `pip install scholarly`

---

## 📞 Bantuan

Baca dokumentasi lengkap: [README_PUBLICATIONS.md](README_PUBLICATIONS.md)

Email: ahmadluky@sd.itera.ac.id
