# Starter PWA Absensi Mahasiswa

## Isi
- `app.py`: aplikasi Gradio baru dengan dua peran: Mahasiswa dan Petugas/Admin.
- `pwa/`: shell PWA untuk di-host terpisah melalui GitHub Pages.
- `requirements.txt`: dependensi Python.

## Jalankan di Google Colab
1. Buka notebook baru.
2. Upload `app.py` atau salin kode `app.py` ke cell.
3. Sebelum menjalankan, ganti `ADMIN_PASSWORD = "GANTI_PASSWORD_ADMIN"` dengan password rahasia.
4. Jalankan `!pip install -q gradio`
5. Jalankan `!python app.py`
6. Buka URL `https://....gradio.live` yang muncul.

## Alur penggunaan
- Petugas membuka tab Petugas/Admin, login, membuat nama sesi dan kode absensi.
- Mahasiswa membuka tab Mahasiswa, memasukkan NIM, nama, dan kode yang diberikan petugas.
- Petugas memperbarui tabel dan mengunduh rekap CSV.

## Menjadikan PWA
1. Setelah Gradio berjalan, salin URL `gradio.live` yang baru.
2. Di `pwa/index.html`, ganti dua teks `https://GANTI-LINK-GRADIO.gradio.live` dengan URL Gradio baru.
3. Upload seluruh isi folder `pwa` (index.html, manifest.json, service-worker.js, icons) ke repository GitHub.
4. Aktifkan GitHub Pages dari Settings > Pages > Deploy from a branch > main > /(root).
5. Buka URL GitHub Pages di Chrome Android dan pilih Install app / Tambahkan ke layar utama.

## Penting
- Link `gradio.live` dari Colab bersifat sementara dan dapat berubah saat runtime berhenti.
- SQLite pada runtime Colab juga sementara. Unduh/backup rekap CSV secara berkala. Untuk pemakaian resmi, pindahkan backend dan database ke hosting permanen.
- Versi awal ini menggunakan kode absensi, bukan QR, GPS, atau verifikasi identitas kampus.
- Ganti password admin sebelum membagikan link. Jangan bagikan password admin ke mahasiswa.
