# Cara Menambahkan Foto Profil

## Langkah-langkah:

1. **Tambahkan foto Anda** ke folder `images/` dengan nama `profile.jpg` atau `profile.png`

2. **Edit file index.html** - Cari baris ini (sekitar baris 152):
   ```html
   <div class="profile-img">
       <!-- Anda bisa mengganti ini dengan <img src="foto-anda.jpg" class="profile-img"> -->
       <i class="fas fa-user"></i>
   </div>
   ```

3. **Ganti dengan**:
   ```html
   <img src="images/profile.jpg" alt="Ahmad Luky" class="profile-img">
   ```

## Rekomendasi Foto:
- **Ukuran**: 500x500 pixels atau lebih
- **Format**: JPG atau PNG
- **Background**: Lebih baik background polos atau blur
- **Ukuran file**: Maksimal 500KB untuk loading cepat

## Tips:
- Pastikan foto berkualitas baik dan profesional
- Foto wajah yang jelas dengan pencahayaan baik
- Ekspresi yang ramah dan profesional
