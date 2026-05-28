# 📚 Sistem Publikasi Dinamis - Panduan Penggunaan

Sistem ini memungkinkan Anda menampilkan publikasi dari Google Scholar secara otomatis di website GitHub Pages Anda.

## 🚀 Cara Kerja

Sistem ini menggunakan:
1. **File JSON** (`data/publications.json`) - menyimpan data publikasi
2. **JavaScript** (`js/publications.js`) - menampilkan data secara dinamis
3. **Python Script** (`update_publications.py`) - membantu update data

## 📋 Struktur File

```
achluky.github.io/
├── data/
│   └── publications.json          # Data publikasi Anda
├── js/
│   └── publications.js            # Script untuk menampilkan data
├── update_publications.py         # Script Python untuk update data
└── article_presentation.html      # Halaman publikasi
```

## 🔧 Cara Update Publikasi

### Metode 1: Edit Manual (Paling Mudah)

1. Buka file `data/publications.json`
2. Tambahkan publikasi baru dengan format:

```json
{
  "title": "Judul Publikasi Anda",
  "authors": "Ahmad Luky Ramdani, Penulis Lain",
  "venue": "Nama Jurnal/Konferensi",
  "year": 2025,
  "citations": 0,
  "pdfUrl": "https://link-ke-pdf.com/paper.pdf",
  "type": "journal"
}
```

3. Save file
4. Commit dan push ke GitHub

### Metode 2: Menggunakan Python Script (Auto-fetch dari Google Scholar)

#### Instalasi Library

```bash
pip install scholarly
```

#### Jalankan Script

```bash
cd achluky.github.io
python update_publications.py
```

#### Pilihan yang tersedia:
- **Opsi 1**: Auto-fetch dari Google Scholar (requires library `scholarly`)
- **Opsi 2**: Input manual interaktif
- **Opsi 3**: Buka file JSON untuk edit manual

### Metode 3: Manual Entry via Script

```bash
python update_publications.py
# Pilih opsi 2, lalu isi data publikasi
```

## 📊 Format Data JSON Lengkap

```json
{
  "lastUpdated": "2026-05-28",
  "scholarProfile": "https://scholar.google.com/citations?user=gjOzo9MAAAAJ",
  "totalCitations": 150,
  "publications": [
    {
      "title": "Judul Publikasi",
      "authors": "Ahmad Luky Ramdani, Penulis Lain",
      "venue": "Nama Konferensi/Jurnal",
      "year": 2025,
      "citations": 10,
      "pdfUrl": "https://link-ke-pdf.com",
      "type": "journal"
    }
  ],
  "presentations": [
    {
      "title": "Judul Presentasi",
      "event": "Nama Event",
      "date": "2025-06-15",
      "location": "Lokasi Event",
      "slidesUrl": "https://link-ke-slides.com"
    }
  ]
}
```

## 🎨 Fitur yang Ditampilkan

### 1. Statistics Bar
Menampilkan:
- Total publikasi
- Total sitasi
- Total presentasi
- Tanggal update terakhir

### 2. Daftar Publikasi
Menampilkan:
- Judul publikasi
- Nama penulis
- Venue (jurnal/konferensi)
- Tahun publikasi
- Jumlah sitasi
- Link ke PDF (jika ada)

### 3. Daftar Presentasi
Menampilkan:
- Judul presentasi
- Nama event
- Lokasi dan tanggal
- Link ke slides (jika ada)

## 🔄 Workflow Update Rutin

### Update Berkala (Recommended: setiap bulan)

1. **Cek publikasi baru di Google Scholar**
   - Buka: https://scholar.google.com/citations?user=gjOzo9MAAAAJ

2. **Update data**
   ```bash
   # Menggunakan script Python
   python update_publications.py
   
   # Atau edit manual
   open data/publications.json
   ```

3. **Commit changes**
   ```bash
   git add data/publications.json
   git commit -m "Update publications data"
   git push origin main
   ```

4. **Verifikasi di website**
   - Buka: https://achluky.github.io/article_presentation.html
   - Refresh halaman untuk melihat update

## 🛠️ Troubleshooting

### Publikasi tidak muncul?

1. **Cek Console Browser**
   - Buka Developer Tools (F12)
   - Lihat tab Console untuk error messages

2. **Verifikasi file JSON**
   - Pastikan format JSON valid
   - Gunakan: https://jsonlint.com/ untuk validasi

3. **Cek path file**
   - Pastikan `data/publications.json` ada
   - Pastikan `js/publications.js` di-load dengan benar

### Error loading data?

```javascript
// Buka Browser Console (F12) dan ketik:
fetch('data/publications.json')
  .then(r => r.json())
  .then(d => console.log(d))
```

## 📱 Testing Lokal

Untuk test di komputer lokal:

```bash
# Menggunakan Python
cd achluky.github.io
python3 -m http.server 8000

# Buka browser
open http://localhost:8000/article_presentation.html
```

## 🎯 Tips & Best Practices

1. **Update rutin**: Update data setiap ada publikasi baru
2. **Backup data**: Simpan copy `publications.json` di tempat lain
3. **Link PDF**: Gunakan DOI link atau institutional repository
4. **Sitasi akurat**: Update jumlah sitasi secara berkala
5. **Format konsisten**: Gunakan format penulisan yang sama untuk semua entry

## 🔐 Keamanan & Privacy

- ✅ Semua data disimpan di repository GitHub Anda
- ✅ Tidak ada API key atau credentials yang dibutuhkan
- ✅ Data publikasi bersifat public (sesuai Google Scholar)
- ✅ Anda punya kontrol penuh atas data yang ditampilkan

## 📞 Support

Jika ada pertanyaan atau masalah:
1. Cek dokumentasi ini
2. Lihat contoh di `data/publications.json`
3. Hubungi: ahmadluky@sd.itera.ac.id

## 🚀 Future Enhancements (Optional)

Jika ingin fitur lebih advanced:
- [ ] GitHub Actions untuk auto-update berkala
- [ ] Integration dengan Semantic Scholar API
- [ ] Export ke BibTeX format
- [ ] Filter publikasi berdasarkan tahun/tipe
- [ ] Search functionality
- [ ] Citation graph visualization

---

**Last Updated**: May 28, 2026  
**Maintainer**: Ahmad Luky Ramdani
