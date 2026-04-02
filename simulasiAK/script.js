// Data koefisien AK per jabatan per tahun
const koefisienAK = {
    'Asisten Ahli': 12.5,
    'Lektor': 12.5,
    'Lektor Kepala': 12.5
};

// Data konversi predikat SKP
const konversiSKP = {
    'Sangat Baik': 1.5,
    'Baik': 1.0,
    'Cukup': 0.75,
    'Kurang': 0.5
};

// Data nilai maksimal publikasi
const nilaiPublikasi = {
    // Buku
    'Buku Referensi': 40,
    'Monograf': 40,
    'Book Chapter Internasional': 15,
    'Book Chapter Nasional': 10,
    
    // Jurnal Internasional
    'Jurnal Internasional Bereputasi Q1': 40,
    'Jurnal Internasional Bereputasi Q2': 38,
    'Jurnal Internasional Bereputasi Q3': 35,
    'Jurnal Internasional Bereputasi Q4': 33,
    'Jurnal Internasional Bereputasi Lainnya': 30,
    
    // Jurnal Nasional
    'Jurnal Nasional Terakreditasi SINTA 1': 25,
    'Jurnal Nasional Terakreditasi SINTA 2': 25,
    'Jurnal Nasional Terakreditasi SINTA 3': 20,
    'Jurnal Nasional Terakreditasi SINTA 4': 20,
    'Jurnal Nasional Terakreditasi SINTA 5': 15,
    'Jurnal Nasional Terakreditasi SINTA 6': 15,
    'Jurnal Nasional Tidak Terakreditasi': 10,
    
    // Diseminasi - Prosiding
    'Prosiding Internasional Terindeks Bereputasi': 20,
    'Prosiding Internasional Tidak Terindeks': 10,
    'Prosiding Nasional': 7.5,
    
    // Diseminasi - Tanpa Prosiding
    'Seminar/Lokakarya Internasional': 5,
    'Seminar/Lokakarya Nasional': 3,
    'Media Populer (Koran/Majalah)': 2,
    
    // Kegiatan Penelitian Lainnya
    'Hasil Penelitian di Perpustakaan/Industri': 2,
    'Menerjemahkan Buku Ilmiah': 15,
    'Mengedit/Menyunting Buku Ilmiah': 10,
    
    // HKI
    'Paten Internasional (Diterapkan)': 60,
    'Paten Internasional': 50,
    'Paten Nasional (Diterapkan)': 40,
    'Paten Nasional': 30,
    'Paten Sederhana': 20,
    'Hak Cipta/Desain Industri': 15,
    'Karya Inovasi Berdampak': 40,
    
    // Kebijakan
    'Rumusan Kebijakan Internasional': 20,
    'Rumusan Kebijakan Nasional': 15,
    'Rumusan Kebijakan Lokal': 10
};

// Fungsi untuk menghitung proporsi penulis
function hitungProporsiPenulis(jumlahPenulis, posisiPenulis, isKorespondensi) {
    if (jumlahPenulis === 1) {
        return 1.0; // 100% untuk penulis tunggal
    } else if (jumlahPenulis === 2) {
        if (posisiPenulis === 'Pertama' && isKorespondensi === 'Ya') {
            return 0.6; // 60%
        } else if (posisiPenulis === 'Pertama' && isKorespondensi === 'Tidak') {
            return 0.5; // 50%
        } else if (posisiPenulis === 'Kedua' && isKorespondensi === 'Ya') {
            return 0.5; // 50%
        } else {
            return 0.4; // 40%
        }
    } else { // 3 atau lebih
        if (posisiPenulis === 'Pertama' && isKorespondensi === 'Ya') {
            return 0.6; // 60%
        } else if (isKorespondensi === 'Ya') {
            return 0.4; // 40% untuk korespondensi bukan pertama
        } else if (posisiPenulis === 'Pertama' && isKorespondensi === 'Tidak') {
            return 0.4; // 40%
        } else {
            // Sisanya dibagi rata
            const sisa = (posisiPenulis === 'Pertama') ? 0.4 : 0.2;
            const jumlahAnggotaLain = (posisiPenulis === 'Pertama') ? jumlahPenulis - 1 : jumlahPenulis - 2;
            return sisa / jumlahAnggotaLain;
        }
    }
}

let penelitianCounter = 0;

// Inisialisasi
document.addEventListener('DOMContentLoaded', function() {
    tambahPenelitian();
});

// Fungsi tambah penelitian
function tambahPenelitian() {
    penelitianCounter++;
    const penelitianList = document.getElementById('penelitianList');
    
    const penelitianItem = document.createElement('div');
    penelitianItem.className = 'penelitian-item';
    penelitianItem.id = `penelitian-${penelitianCounter}`;
    
    penelitianItem.innerHTML = `
        <button type="button" class="btn-remove" onclick="hapusPenelitian(${penelitianCounter})">Hapus</button>
        <h4>Penelitian ${penelitianCounter}</h4>
        <div class="form-group">
            <label>Jenis Publikasi:</label>
            <select id="jenis-${penelitianCounter}">
                <option value="">-- Pilih Jenis --</option>
                <optgroup label="Buku">
                    <option value="Buku Referensi">Buku Referensi (40 AK)</option>
                    <option value="Monograf">Monograf (40 AK)</option>
                    <option value="Book Chapter Internasional">Book Chapter Internasional (15 AK)</option>
                    <option value="Book Chapter Nasional">Book Chapter Nasional (10 AK)</option>
                </optgroup>
                <optgroup label="Jurnal Internasional">
                    <option value="Jurnal Internasional Bereputasi Q1">Jurnal Internasional Bereputasi Q1 (40 AK)</option>
                    <option value="Jurnal Internasional Bereputasi Q2">Jurnal Internasional Bereputasi Q2 (38 AK)</option>
                    <option value="Jurnal Internasional Bereputasi Q3">Jurnal Internasional Bereputasi Q3 (35 AK)</option>
                    <option value="Jurnal Internasional Bereputasi Q4">Jurnal Internasional Bereputasi Q4 (33 AK)</option>
                    <option value="Jurnal Internasional Bereputasi Lainnya">Jurnal Internasional Bereputasi Lainnya (30 AK)</option>
                </optgroup>
                <optgroup label="Jurnal Nasional">
                    <option value="Jurnal Nasional Terakreditasi SINTA 1">Jurnal Nasional SINTA 1 (25 AK)</option>
                    <option value="Jurnal Nasional Terakreditasi SINTA 2">Jurnal Nasional SINTA 2 (25 AK)</option>
                    <option value="Jurnal Nasional Terakreditasi SINTA 3">Jurnal Nasional SINTA 3 (20 AK)</option>
                    <option value="Jurnal Nasional Terakreditasi SINTA 4">Jurnal Nasional SINTA 4 (20 AK)</option>
                    <option value="Jurnal Nasional Terakreditasi SINTA 5">Jurnal Nasional SINTA 5 (15 AK)</option>
                    <option value="Jurnal Nasional Terakreditasi SINTA 6">Jurnal Nasional SINTA 6 (15 AK)</option>
                    <option value="Jurnal Nasional Tidak Terakreditasi">Jurnal Nasional Tidak Terakreditasi (10 AK)</option>
                </optgroup>
                <optgroup label="Prosiding">
                    <option value="Prosiding Internasional Terindeks Bereputasi">Prosiding Internasional Terindeks Bereputasi (20 AK)</option>
                    <option value="Prosiding Internasional Tidak Terindeks">Prosiding Internasional Tidak Terindeks (10 AK)</option>
                    <option value="Prosiding Nasional">Prosiding Nasional (7.5 AK)</option>
                </optgroup>
                <optgroup label="Seminar/Lokakarya">
                    <option value="Seminar/Lokakarya Internasional">Seminar/Lokakarya Internasional (5 AK)</option>
                    <option value="Seminar/Lokakarya Nasional">Seminar/Lokakarya Nasional (3 AK)</option>
                </optgroup>
                <optgroup label="Lainnya">
                    <option value="Media Populer (Koran/Majalah)">Media Populer - Koran/Majalah (2 AK)</option>
                    <option value="Hasil Penelitian di Perpustakaan/Industri">Hasil Penelitian di Perpustakaan/Industri (2 AK)</option>
                    <option value="Menerjemahkan Buku Ilmiah">Menerjemahkan Buku Ilmiah (15 AK)</option>
                    <option value="Mengedit/Menyunting Buku Ilmiah">Mengedit/Menyunting Buku Ilmiah (10 AK)</option>
                </optgroup>
                <optgroup label="HKI">
                    <option value="Paten Internasional (Diterapkan)">Paten Internasional - Diterapkan (60 AK)</option>
                    <option value="Paten Internasional">Paten Internasional (50 AK)</option>
                    <option value="Paten Nasional (Diterapkan)">Paten Nasional - Diterapkan (40 AK)</option>
                    <option value="Paten Nasional">Paten Nasional (30 AK)</option>
                    <option value="Paten Sederhana">Paten Sederhana (20 AK)</option>
                    <option value="Hak Cipta/Desain Industri">Hak Cipta/Desain Industri (15 AK)</option>
                    <option value="Karya Inovasi Berdampak">Karya Inovasi Berdampak (40 AK)</option>
                </optgroup>
                <optgroup label="Kebijakan">
                    <option value="Rumusan Kebijakan Internasional">Rumusan Kebijakan Internasional (20 AK)</option>
                    <option value="Rumusan Kebijakan Nasional">Rumusan Kebijakan Nasional (15 AK)</option>
                    <option value="Rumusan Kebijakan Lokal">Rumusan Kebijakan Lokal (10 AK)</option>
                </optgroup>
            </select>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Jumlah Penulis:</label>
                <input type="number" id="jumlahPenulis-${penelitianCounter}" min="1" placeholder="Contoh: 3">
            </div>
            <div class="form-group">
                <label>Posisi Penulis:</label>
                <select id="posisi-${penelitianCounter}">
                    <option value="">-- Pilih --</option>
                    <option value="Tunggal">Penulis Tunggal</option>
                    <option value="Pertama">Penulis Pertama</option>
                    <option value="Kedua">Penulis Kedua</option>
                    <option value="Anggota">Penulis Anggota/Lainnya</option>
                </select>
            </div>
            <div class="form-group">
                <label>Penulis Korespondensi:</label>
                <select id="korespondensi-${penelitianCounter}">
                    <option value="">-- Pilih --</option>
                    <option value="Ya">Ya</option>
                    <option value="Tidak">Tidak</option>
                </select>
            </div>
        </div>
    `;
    
    penelitianList.appendChild(penelitianItem);
}

// Fungsi hapus penelitian
function hapusPenelitian(id) {
    const item = document.getElementById(`penelitian-${id}`);
    if (item) {
        item.remove();
    }
}

// Fungsi hitung AK
function hitungAK() {
    // Validasi input dasar
    const namaDosen = document.getElementById('namaDosen').value;
    const jabatanSekarang = document.getElementById('jabatanSekarang').value;
    const akSekarang = parseFloat(document.getElementById('akSekarang').value);
    const jabatanTarget = document.getElementById('jabatanTarget').value;
    const akTarget = parseFloat(document.getElementById('akTarget').value);
    const skpTahun1 = document.getElementById('skpTahun1').value;
    const skpTahun2 = document.getElementById('skpTahun2').value;

    if (!namaDosen || !jabatanSekarang || !akSekarang || !jabatanTarget || !akTarget || !skpTahun1 || !skpTahun2) {
        alert('Mohon lengkapi semua data dasar dan SKP!');
        return;
    }

    // Hitung AK Konversi dari SKP
    const koefisien = koefisienAK[jabatanSekarang];
    const akTahun1 = koefisien * konversiSKP[skpTahun1];
    const akTahun2 = koefisien * konversiSKP[skpTahun2];
    const totalAKKonversi = akTahun1 + akTahun2;

    // Hitung AK Prestasi dari Penelitian
    let totalAKPrestasi = 0;
    let jumlahPublikasi = 0;
    let detailPenelitian = [];

    const penelitianItems = document.querySelectorAll('.penelitian-item');
    penelitianItems.forEach((item, index) => {
        const id = item.id.split('-')[1];
        const jenis = document.getElementById(`jenis-${id}`)?.value;
        const jumlahPenulis = parseInt(document.getElementById(`jumlahPenulis-${id}`)?.value);
        const posisi = document.getElementById(`posisi-${id}`)?.value;
        const korespondensi = document.getElementById(`korespondensi-${id}`)?.value;

        if (jenis && jumlahPenulis && posisi && korespondensi) {
            jumlahPublikasi++;
            const nilaiMaksimal = nilaiPublikasi[jenis];
            
            // Hitung proporsi berdasarkan jumlah penulis dan posisi
            let proporsi;
            if (posisi === 'Tunggal') {
                proporsi = 1.0;
            } else {
                proporsi = hitungProporsiPenulis(jumlahPenulis, posisi, korespondensi);
            }
            
            const akPenelitian = nilaiMaksimal * proporsi;
            totalAKPrestasi += akPenelitian;

            // Format deskripsi posisi
            let deskripsiPosisi = posisi;
            if (posisi !== 'Tunggal') {
                deskripsiPosisi += (korespondensi === 'Ya') ? ' + Korespondensi' : '';
                deskripsiPosisi += ` (${jumlahPenulis} penulis)`;
            }

            detailPenelitian.push({
                no: jumlahPublikasi,
                jenis: jenis,
                posisi: deskripsiPosisi,
                nilaiMaksimal: nilaiMaksimal,
                proporsi: (proporsi * 100).toFixed(1) + '%',
                ak: akPenelitian
            });
        }
    });

    // Total AK Kumulatif
    const totalAKKumulatif = akSekarang + totalAKKonversi + totalAKPrestasi;
    const selisihAK = akTarget - akSekarang;
    const proporsiPenelitian = selisihAK > 0 ? (totalAKPrestasi / selisihAK) * 100 : 0;

    // Cek syarat-syarat
    const syaratSKPBaik = (skpTahun1 === 'Baik' || skpTahun1 === 'Sangat Baik') && 
                          (skpTahun2 === 'Baik' || skpTahun2 === 'Sangat Baik');
    const syaratPublikasi = jumlahPublikasi >= 1;
    const syaratProporsi = proporsiPenelitian >= 35;
    const syaratAKTercapai = totalAKKumulatif >= akTarget;

    const isEligible = syaratSKPBaik && syaratPublikasi && syaratProporsi && syaratAKTercapai;

    // Tampilkan hasil
    tampilkanHasil({
        namaDosen,
        jabatanSekarang,
        akSekarang,
        jabatanTarget,
        akTarget,
        skpTahun1,
        skpTahun2,
        akTahun1,
        akTahun2,
        totalAKKonversi,
        detailPenelitian,
        totalAKPrestasi,
        totalAKKumulatif,
        selisihAK,
        proporsiPenelitian,
        jumlahPublikasi,
        syaratSKPBaik,
        syaratPublikasi,
        syaratProporsi,
        syaratAKTercapai,
        isEligible
    });
}

// Fungsi tampilkan hasil
function tampilkanHasil(data) {
    // SKP
    document.getElementById('hasilSKP').innerHTML = `
        <div class="detail-item">
            <span class="detail-label">Tahun 2023 (${data.skpTahun1}):</span>
            <span class="detail-value">${konversiSKP[data.skpTahun1] * 100}% × ${koefisienAK[data.jabatanSekarang]} AK = ${data.akTahun1.toFixed(2)} AK</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Tahun 2024 (${data.skpTahun2}):</span>
            <span class="detail-value">${konversiSKP[data.skpTahun2] * 100}% × ${koefisienAK[data.jabatanSekarang]} AK = ${data.akTahun2.toFixed(2)} AK</span>
        </div>
        <div class="detail-item total-row">
            <span>Total AK Konversi (SKP):</span>
            <span>${data.totalAKKonversi.toFixed(2)} AK</span>
        </div>
    `;

    // Penelitian
    let htmlPenelitian = '';
    data.detailPenelitian.forEach(p => {
        htmlPenelitian += `
            <div class="detail-item">
                <span class="detail-label">Penelitian ${p.no}: ${p.jenis}</span>
                <span class="detail-value">${p.proporsi} × ${p.nilaiMaksimal} AK = ${p.ak.toFixed(2)} AK</span>
            </div>
        `;
    });
    htmlPenelitian += `
        <div class="detail-item total-row">
            <span>Total AK Prestasi (Penelitian):</span>
            <span>${data.totalAKPrestasi.toFixed(2)} AK</span>
        </div>
    `;
    document.getElementById('hasilPenelitian').innerHTML = htmlPenelitian;

    // Rekapitulasi
    document.getElementById('hasilRekapitulasi').innerHTML = `
        <div class="detail-item">
            <span class="detail-label">AK Dasar (${data.jabatanSekarang}):</span>
            <span class="detail-value">${data.akSekarang.toFixed(2)} AK</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Tambahan AK Konversi (SKP):</span>
            <span class="detail-value">${data.totalAKKonversi.toFixed(2)} AK</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Tambahan AK Prestasi (Penelitian):</span>
            <span class="detail-value">${data.totalAKPrestasi.toFixed(2)} AK</span>
        </div>
        <div class="detail-item total-row">
            <span>Total AK Kumulatif:</span>
            <span>${data.totalAKKumulatif.toFixed(2)} AK</span>
        </div>
        <p style="margin-top: 15px; color: #666; font-style: italic;">
            Target AK untuk ${data.jabatanTarget}: ${data.akTarget} AK
        </p>
    `;

    // Syarat
    const checkIcon = (status) => status ? '✓' : '✗';
    const checkClass = (status) => status ? 'check-pass' : 'check-fail';
    
    document.getElementById('hasilSyarat').innerHTML = `
        <div class="check-item">
            <span class="check-icon ${checkClass(data.syaratSKPBaik)}">${checkIcon(data.syaratSKPBaik)}</span>
            <span>SKP Minimal "Baik" 2 Tahun Terakhir: ${data.syaratSKPBaik ? 'Terpenuhi' : 'Tidak Terpenuhi'}</span>
        </div>
        <div class="check-item">
            <span class="check-icon ${checkClass(data.syaratPublikasi)}">${checkIcon(data.syaratPublikasi)}</span>
            <span>Memiliki Minimal 1 Publikasi Ilmiah: ${data.syaratPublikasi ? 'Terpenuhi' : 'Tidak Terpenuhi'} (${data.jumlahPublikasi} publikasi)</span>
        </div>
        <div class="check-item">
            <span class="check-icon ${checkClass(data.syaratProporsi)}">${checkIcon(data.syaratProporsi)}</span>
            <span>Proporsi AK Penelitian Minimal 35%: ${data.syaratProporsi ? 'Terpenuhi' : 'Tidak Terpenuhi'} (${data.proporsiPenelitian.toFixed(2)}%)</span>
        </div>
        <p style="margin-top: 10px; color: #666; font-size: 14px;">
            • Total tambahan AK yang dibutuhkan: ${data.selisihAK.toFixed(2)} AK<br>
            • Syarat minimum penelitian (35%): ${(data.selisihAK * 0.35).toFixed(2)} AK<br>
            • Total AK Prestasi Penelitian: ${data.totalAKPrestasi.toFixed(2)} AK
        </p>
        <div class="check-item">
            <span class="check-icon ${checkClass(data.syaratAKTercapai)}">${checkIcon(data.syaratAKTercapai)}</span>
            <span>Target AK Tercapai: ${data.syaratAKTercapai ? 'Terpenuhi' : 'Tidak Terpenuhi'}</span>
        </div>
    `;

    // Status
    const statusBox = document.getElementById('hasilStatus');
    if (data.isEligible) {
        statusBox.className = 'status-box status-eligible';
        statusBox.innerHTML = `
            <div class="status-icon">✓</div>
            <div>STATUS: ELIGIBLE</div>
            <p style="font-size: 14px; margin-top: 10px; font-weight: normal;">
                ${data.namaDosen} memenuhi semua syarat dan siap direkomendasikan untuk mengikuti 
                Penilaian Uji Kompetensi ${data.jabatanTarget}.
            </p>
        `;
    } else {
        statusBox.className = 'status-box status-not-eligible';
        statusBox.innerHTML = `
            <div class="status-icon">✗</div>
            <div>STATUS: TIDAK ELIGIBLE</div>
            <p style="font-size: 14px; margin-top: 10px; font-weight: normal;">
                ${data.namaDosen} belum memenuhi semua syarat untuk kenaikan jabatan ${data.jabatanTarget}.
            </p>
        `;
    }

    // Tampilkan section hasil
    document.getElementById('hasilSection').style.display = 'block';
    document.getElementById('hasilSection').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Fungsi reset
function resetForm() {
    if (confirm('Apakah Anda yakin ingin mereset semua data?')) {
        document.getElementById('namaDosen').value = '';
        document.getElementById('jabatanSekarang').value = '';
        document.getElementById('akSekarang').value = '';
        document.getElementById('jabatanTarget').value = '';
        document.getElementById('akTarget').value = '';
        document.getElementById('skpTahun1').value = '';
        document.getElementById('skpTahun2').value = '';
        document.getElementById('penelitianList').innerHTML = '';
        document.getElementById('hasilSection').style.display = 'none';
        penelitianCounter = 0;
        tambahPenelitian();
    }
}
