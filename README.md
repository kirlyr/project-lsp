# SSIS - SchoolScore Information Sistem

SSIS adalah aplikasi web berbasis Django untuk mengelola data akademik sekolah, terutama data siswa, guru, mata pelajaran, input nilai, rekap nilai, dan laporan kelulusan. Project ini memakai database MySQL dan sistem login berbasis role `admin`, `guru`, dan `siswa`.

README ini disusun untuk kebutuhan pengumpulan project kampus agar asesor dapat melakukan setup, migrasi database, dan menjalankan aplikasi dengan langkah yang jelas.

## Fitur Utama

- Login dan logout pengguna.
- Role pengguna: admin, guru, dan siswa.
- Dashboard berbeda sesuai role pengguna.
- Admin dapat mengelola data siswa.
- Admin dapat mengelola data guru.
- Admin dapat mengelola data mata pelajaran.
- Akun siswa dibuat otomatis dari NIS saat admin menambah siswa.
- Akun guru dibuat otomatis dari ID guru saat admin menambah guru.
- Guru dapat menginput nilai tugas, UTS, dan UAS.
- Sistem menghitung nilai akhir secara otomatis.
- Sistem menentukan status kelulusan secara otomatis.
- Guru dapat melihat rekap nilai yang pernah diinput.
- Siswa dapat melihat nilai miliknya sendiri.
- Admin dan guru dapat melihat laporan nilai dengan filter kelas, mata pelajaran, dan status kelulusan.

## Teknologi yang Digunakan

- Python
- Django 5.2
- MySQL
- mysqlclient
- python-dotenv
- HTML
- CSS

## Struktur Folder Project

Struktur utama project:

```text
SSIS/
|-- akademik/
|   |-- migrations/
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- decorators.py
|   |-- forms.py
|   |-- managers.py
|   |-- models.py
|   |-- services.py
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- docs/
|   `-- bab2.md
|-- scores/
|   |-- migrations/
|   |-- __init__.py
|   |-- apps.py
|   |-- decorators.py
|   |-- forms.py
|   |-- managers.py
|   |-- models.py
|   |-- services.py
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- setup/
|   |-- __init__.py
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- ssis/
|   |-- __init__.py
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- static/
|   `-- css/
|       `-- app.css
|-- templates/
|   |-- akademik/
|   `-- scores/
|-- .env
|-- .gitignore
|-- manage.py
|-- README.md
`-- requirements.txt
```

Catatan struktur:

- Entry point command Django adalah `manage.py`.
- `manage.py` memakai konfigurasi aktif `setup.settings`.
- App yang aktif pada `setup.settings` adalah `akademik`.
- Folder `scores` dan `ssis` masih ada di project, tetapi command default dari `manage.py` diarahkan ke konfigurasi `setup`.

## Persiapan Awal

Pastikan sudah menginstal:

- Python
- MySQL Server
- Git, jika mengambil project dari repository

## Setup Virtual Environment

Jalankan perintah dari root project `SSIS`.

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Jika aktivasi PowerShell diblokir, jalankan:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Lalu aktifkan ulang virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

### macOS atau Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Requirements

Pastikan virtual environment sudah aktif, lalu jalankan:

```bash
pip install -r requirements.txt
```

## Konfigurasi .env

Buat file `.env` di root project jika belum ada. Contoh isi file `.env`:

```env
SECRET_KEY=isi-secret-key-django
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
MYSQL_DATABASE=ssis
MYSQL_USER=root
MYSQL_PASSWORD=12345678
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

Keterangan:

- `SECRET_KEY`: secret key untuk Django.
- `DEBUG`: gunakan `1` untuk development.
- `ALLOWED_HOSTS`: host yang diizinkan untuk akses aplikasi.
- `MYSQL_DATABASE`: nama database MySQL.
- `MYSQL_USER`: username MySQL.
- `MYSQL_PASSWORD`: password MySQL.
- `MYSQL_HOST`: host MySQL.
- `MYSQL_PORT`: port MySQL, default `3306`.

## Membuat Database MySQL

Masuk ke MySQL:

```bash
mysql -u root -p
```

Buat database:

```sql
CREATE DATABASE ssis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Jika memakai user MySQL selain `root`, sesuaikan nilai `MYSQL_USER` dan `MYSQL_PASSWORD` di file `.env`.

Keluar dari MySQL:

```sql
EXIT;
```

## Migrasi Database

Pastikan database sudah dibuat dan konfigurasi `.env` sudah benar. Jalankan:

```bash
python manage.py makemigrations
python manage.py migrate
```

Project ini menggunakan custom user model `akademik.User`, sehingga migrasi harus dilakukan sebelum membuat superuser.

## Membuat Superuser

Jalankan:

```bash
python manage.py createsuperuser
```

Ikuti input yang diminta di terminal. Superuser akan dibuat sebagai user dengan role `admin`.

## Menjalankan Server

Jalankan:

```bash
python manage.py runserver
```

Jika berhasil, server berjalan di:

```text
http://127.0.0.1:8000/
```

## URL Akses Aplikasi

URL utama:

- Home: `http://127.0.0.1:8000/`
- Login: `http://127.0.0.1:8000/login/`
- Redirect dashboard setelah login: `http://127.0.0.1:8000/dashboard/`

URL role admin:

- Dashboard admin: `http://127.0.0.1:8000/admin-dashboard/`
- Kelola siswa: `http://127.0.0.1:8000/siswa/`
- Kelola guru: `http://127.0.0.1:8000/guru/`
- Kelola mata pelajaran: `http://127.0.0.1:8000/mapel/`
- Laporan nilai: `http://127.0.0.1:8000/laporan/`

URL role guru:

- Dashboard guru: `http://127.0.0.1:8000/guru/guru-dashboard/`
- Input nilai: `http://127.0.0.1:8000/nilai/input/`
- Rekap nilai: `http://127.0.0.1:8000/nilai/rekap/`
- Laporan nilai: `http://127.0.0.1:8000/laporan/`

URL role siswa:

- Dashboard siswa: `http://127.0.0.1:8000/siswa-dashboard/`
- Nilai saya: `http://127.0.0.1:8000/nilai/saya/`

## Akun Login Guru dan Siswa

Saat admin menambah data guru, sistem otomatis membuat akun guru:

- Username: ID guru
- Password awal: ID guru

Saat admin menambah data siswa, sistem otomatis membuat akun siswa:

- Username: NIS
- Password awal: NIS