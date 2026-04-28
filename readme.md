# Dokumentasi Proyek UAS: Smart Brightness Control via Gesture (Fuzzy Logic)

Proyek ini adalah sistem kontrol kecerahan layar laptop otomatis menggunakan deteksi jumlah jari tangan (Hand Gesture) berbasis Logika Fuzzy. Sistem ini menggunakan kamera untuk menghitung jari yang terbuka dan menyesuaikan kecerahan layar secara halus (smooth transition).

## 1. Fitur Utama

- **Fuzzy Logic Controller**: Menggunakan kurva keanggotaan Segitiga untuk transisi akurat.
- **Hand Tracking**: Berbasis MediaPipe untuk deteksi landmark tangan yang cepat.
- **Smoothing Transition**: Perubahan kecerahan dilakukan bertahap per 5% untuk kenyamanan mata.

## 2. Persyaratan Sistem (Requirements)

Pastikan Anda menggunakan Python versi 3.9 hingga 3.11. Gunakan file `requirements.txt` untuk menginstal dependensi:

```text
numpy==1.26.4
opencv-python==4.10.0.84
mediapipe==0.10.11
scikit-fuzzy==0.5.0
scipy==1.11.4
screen-brightness-control==0.23.0
packaging
networkx
```

### Cara Instalasi:

1. Buat virtual environment: `python -m venv venv`
2. Aktifkan venv: `.\\venv\\Scripts\\activate`
3. Instal library: `pip install -r requirements.txt`

## 3. Alur Perhitungan Fuzzy (Flow Logic)

### A. Fuzzifikasi (Input)

Input sistem adalah **Jumlah Jari** ($0$ hingga $5$). Variabel ini dimasukkan ke dalam Himpunan Fuzzy dengan kurva **Segitiga (Triangular Membership Function)**.

- **Himpunan**: {Nol, Satu, Dua, Tiga, Empat, Lima}
- **Alasan Kurva Segitiga**: Dipilih karena memiliki titik puncak tunggal yang presisi, sehingga setiap penambahan satu jari memberikan respon output yang linear dan jelas.

### B. Inferensi (Rules)

Sistem menggunakan aturan IF-THEN sederhana untuk memetakan jumlah jari ke target brightness:

1. IF Jari **Nol** THEN Brightness **0%**
2. IF Jari **Satu** THEN Brightness **20%**
3. IF Jari **Dua** THEN Brightness **40%**
4. IF Jari **Tiga** THEN Brightness **60%**
5. IF Jari **Empat** THEN Brightness **80%**
6. IF Jari **Lima** THEN Brightness **100%**

### C. Defuzzifikasi (Output)

Sistem menggunakan metode **Centroid (Titik Berat)** untuk menghasilkan nilai tegas (_crisp value_).

- **Catatan**: Karena sifat metode Centroid yang mencari nilai rata-rata area, nilai ujung (0 dan 100) dikoreksi menggunakan logika _Hard-Limit_ agar sistem dapat mencapai batas maksimal dan minimal secara sempurna.

## 4. Logika Pemrograman

1. **Image Processing**: Kamera menangkap frame, dibalik (mirrored), dan dikonversi ke RGB.
2. **Hand Detection**: MediaPipe mencari 21 titik koordinat tangan.
3. **Finger Counting**:
   - Jari telunjuk-kelingking dicek berdasarkan posisi koordinat Y ujung jari terhadap pangkalnya.
4. **Execution**: Target brightness dari Fuzzy dibandingkan dengan brightness saat ini. Jika selisih > 5%, maka brightness layar diubah secara bertahap (+5% atau -5%).

---

## 5. penggunaan Logika Fuzzy dalam aplikasi

1. Smoothing: Menghilangkan efek lompatan nilai yang drastis.
2. Robustness: Tetap stabil meskipun input dari kamera mengalami sedikit gangguan atau noise.
3. Human-like: Memberikan respon yang lebih alami sesuai dengan perilaku gesture manusia.

**Mata Kuliah:** Logika Fuzzy
