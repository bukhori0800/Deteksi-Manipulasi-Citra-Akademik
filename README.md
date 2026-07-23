# 🛡️ Secure e-Document System

Aplikasi berbasis web untuk mengamankan dan memverifikasi dokumen akademik menggunakan kombinasi **Steganografi LSB (Least Significant Bit)** dan **Enkripsi AES-256**. 

Sistem ini memungkinkan penyisipan data kredensial (seperti Nama, NIM, dan IPK) ke dalam gambar *cover* (PNG) secara kasat mata, dan melindunginya dengan password agar tidak bisa dibaca atau dimanipulasi oleh pihak yang tidak bertanggung jawab.

## ✨ Fitur Utama
- **Encoding & Enkripsi:** Menyembunyikan teks kredensial ke dalam gambar PNG yang dilindungi dengan password (AES-256).
- **Verifikasi Dokumen:** Mengekstrak dan mendekripsi teks dari gambar (Stego Image) untuk memvalidasi keaslian dokumen.
- **Kalkulasi Metrik:** Menampilkan metrik kualitas gambar (PSNR dan MSE) serta kapasitas piksel yang terpakai setelah proses steganografi.
- **Indikator Kekuatan Password:** Memastikan keamanan kunci enkripsi yang digunakan.

## 🛠️ Teknologi yang Digunakan
- **Python 3**
- **Streamlit** (User Interface)
- **PyCryptodome** (Enkripsi AES)
- **Pillow & NumPy** (Pemrosesan Gambar & Steganografi LSB)
- **Scikit-Image** (Kalkulasi Metrik PSNR & MSE)

## 🚀 Cara Menjalankan Secara Lokal

1. **Clone repository ini**
   ```bash
   git clone [https://github.com/bukhori0800/Deteksi-Manipulasi-Citra-Akademik.git](https://github.com/bukhori0800/Deteksi-Manipulasi-Citra-Akademik.git)
   cd Deteksi-Manipulasi-Citra-Akademik
