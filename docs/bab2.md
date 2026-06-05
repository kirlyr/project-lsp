# TUGAS 2 — IMPLEMENTASI PROGRAM

## Aplikasi Pengolahan Nilai Siswa (SIPENILAI)

**Stack: PHP 8 + MySQL (XAMPP) · PDO · Bootstrap 5**

## 1. Struktur Proyek

```
aplikasi-nilai-siswa/
├── config/
│ ├── database.php # Kelas Database (koneksi PDO - OOP)
│ └── bootstrap.php # Inisialisasi: session, BASE_URL, autoload
├── classes/ # PEMROGRAMAN OOP
│ ├── Siswa.php · Guru.php · Nilai.php · User.php
├── includes/
│ ├── functions.php # PEMROGRAMAN TERSTRUKTUR (fungsi/prosedur)
│ ├── auth.php # Guard login & role
│ ├── header.php · sidebar.php · footer.php # Layout
├── auth/login.php · logout.php
├── admin/ (dashboard, siswa, guru, users, nilai, laporan)
├── guru/ (dashboard, input_nilai, rekap_nilai, validasi)
├── siswa/ (dashboard, nilai_saya, sertifikat)
├── assets/css/style.css
├── database/db_nilai_siswa.sql
└── index.php
```
## 2. Koneksi Database (Bukti Pengujian Database)

Koneksi memakai **PDO** dengan pola **Singleton** pada kelas Database:
class Database {
private const HOST='localhost', NAME='db_nilai_siswa', USER='root', PASS='';
private static ?PDO $instance = null;
public static function getConnection(): PDO {
if (self::$instance === null) {
$dsn = "mysql:host=".self::HOST.";dbname=".self::NAME.";charset=utf8mb4";
self::$instance = new PDO($dsn, self::USER, self::PASS, [
PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
PDO::ATTR_EMULATE_PREPARES => false,
]);
}
return self::$instance;
}
}
**Bukti koneksi berhasil:** setelah db_nilai_siswa.sql diimpor dan XAMPP aktif,
membuka [http://localhost/aplikasi-nilai-siswa/](http://localhost/aplikasi-nilai-siswa/) dan berhasil login membuktikan
query (SELECT users) berjalan. Bila koneksi gagal, aplikasi menampilkan pesan


yang jelas beserta petunjuk perbaikan (lihat blok catch (PDOException)).
_Uji cepat koneksi (opsional) — jalankan di terminal:
```bash
php -r "require 'config/database.php'; Database::getConnection(); echo 'KONEKSI OK';"
```_

## 3. Halaman Login Berdasarkan Role (Output #1)

Berkas: auth/login.php. Role diambil otomatis dari akun,
lalu user diarahkan ke dashboard sesuai role.
$user = (new User())->login($username, $password);
if ($user) {
session_regenerate_id(true); // cegah session fixation
$_SESSION['user'] = $user;
redirect(dashboardUrl($user['role'])); // admin/guru/siswa -> dashboard berbeda
}
User::login() memverifikasi password ter-hash:
if ($user && password_verify($password, $user['password'])) { ... }



## 4. Form Input Data Siswa & Nilai (Output #2)

● **Data siswa (CRUD):** admin/siswa.php — form modal
tambah/edit + hapus, dengan pencarian.
● **Input nilai:** guru/input_nilai.php — guru memilih
siswa lalu mengisi Tugas/UTS/UAS; mata pelajaran otomatis sesuai guru.
$hasil = (new Nilai())->simpan([
'nis' => $_POST['nis'],
'id_guru' => $guru['id_guru'],
'mata_pelajaran' => $guru['mata_pelajaran'],
'nilai_tugas' => $_POST['nilai_tugas'],
'nilai_uts' => $_POST['nilai_uts'],
'nilai_uas' => $_POST['nilai_uas'],
]);
setFlash($hasil['msg'], $hasil['ok']? 'success' : 'danger');


## 5. Proses Perhitungan Nilai Akhir (Output #3)

Inti perhitungan ada pada fungsi terstruktur, dipanggil dari method OOP
Nilai::simpan() → **integrasi terstruktur + OOP** :
// includes/functions.php (TERSTRUKTUR)
function hitungNilaiAkhir($tugas, $uts, $uas): float {
return round((0.30*$tugas) + (0.30*$uts) + (0.40*$uas), 2);
}
function tentukanStatusKelulusan($nilaiAkhir): string {
return ((float)$nilaiAkhir >= 70)? 'Lulus' : 'Tidak Lulus';
}
// classes/Nilai.php (OOP memakai fungsi terstruktur)
public function simpan(array $data): array {
$errors = $this->validasiData($data); // pakai validasiNilai()
if ($errors) return ['ok'=>false, 'msg'=>implode(' ', $errors)];
$nilaiAkhir = hitungNilaiAkhir($data['nilai_tugas'], $data['nilai_uts'],
$data['nilai_uas']);
$status = tentukanStatusKelulusan($nilaiAkhir);


// ... INSERT / UPDATE ke tabel nilai ...
}
Contoh: Tugas 80, UTS 75, UAS 90 → 0.3·80 + 0.3·75 + 0.4·90 = 82.5 → **Lulus**.

## 6. Laporan Hasil Nilai Siswa (Output #4)

● **Laporan admin:** admin/laporan.php — rekap
(memakai olahLaporan()) + tabel, filter kelas, tombol Cetak/PDF.
● **Rekap guru:** guru/rekap_nilai.php.
● **Nilai siswa:** siswa/nilai_saya.php.
● **Surat keterangan:** siswa/sertifikat.php —
dapat diunduh sebagai PDF (Save as PDF) bila siswa lulus semua mapel.
function olahLaporan(array $dataNilai): array {
$total=count($dataNilai); $lulus=0; $jumlah=0;
foreach ($dataNilai as $n) { $jumlah+=$n['nilai_akhir']; if($n['status']==='Lulus')
$lulus++; }


```
return [
'total'=>$total, 'lulus'=>$lulus, 'tidak_lulus'=>$total-$lulus,
'rata_rata'=>$total?round($jumlah/$total,2):0,
'persen_lulus'=>$total?round($lulus/$total*100,1):0,
];
}
```
## 7. Potongan Kode Fungsi/Procedure (Output #8)

Lihat includes/functions.php. Ringkasan:
**Fungsi Tujuan**

validasiNilai() (^) Validasi nilai 0–
hitungNilaiAkhir() (^) Perhitungan nilai akhir 30/30/
tentukanStatusKelulusan() (^) Penentuan Lulus/Tidak Lulus
olahLaporan() (^) Pengolahan rekap laporan
konversiHurufMutu() (^) Konversi ke huruf mutu A–E
e(), csrf_field(), csrf_check() Helper keamanan


## 8. Potongan Kode Class & Method (Output #9)

Lihat folder classes/. Contoh kelas Siswa (CRUD dengan
prepared statement):
class Siswa {
private PDO $db;
public string $nis = '', $nama = '', $kelas = '';
public function __construct() { $this->db = Database::getConnection(); }
public function create(string $nis, string $nama, string $kelas): bool {
$stmt = $this->db->prepare('INSERT INTO siswa (nis,nama,kelas) VALUES (?,?,?)');
return $stmt->execute([$nis, $nama, $kelas]);
}
public function getByNis(string $nis): ?array {
$stmt = $this->db->prepare('SELECT * FROM siswa WHERE nis = ?');
$stmt->execute([$nis]);
return $stmt->fetch() ?: null;
}
}
Daftar kelas: Database, Siswa, Guru, Nilai, User (5 kelas).

## 9. Penjelasan Library / Komponen yang Digunakan (Output #10)

```
Komponen Versi Fungsi
PHP 8.x Bahasa pemrograman sisi server
MySQL (MariaDB) XAMPP Basis data relasional
PDO bawaan PHP Abstraksi akses database +
prepared statement
PDO_MySQL bawaan PHP Driver PDO untuk MySQL
Bootstrap 5.3.3 (CDN) Framework CSS — UI responsif
Bootstrap Icons 1.11.3 (CDN) Ikon antarmuka
password_hash /
password_verify
bawaan PHP Hashing password (bcrypt)
session bawaan PHP Manajemen login per role
FPDF 1.9 Membuat file PDF native (surat
keterangan & laporan)
```

```
Chart.js 4.4.1 (CDN) Grafik statistik kelulusan &
rata-rata nilai
window.print() browser Cetak langsung surat
keterangan/laporan
Semua dependensi PHP bersifat **bawaan** (tanpa Composer). Bootstrap dimuat
via CDN sehingga tidak perlu instalasi tambahan.
```
## 10. Coding Guidelines & Best Practices (Output #11)

1. **Pemisahan tanggung jawab** — konfigurasi, kelas (OOP), fungsi (terstruktur),
layout, dan halaman per-role dipisah ke folder berbeda.
2. **Keamanan:**
    ● **SQL Injection** → seluruh query memakai *prepared statement* (PDO).
    ● **XSS** → output di-escape dengan htmlspecialchars() via helper e().
    ● **Password** → disimpan ter-hash bcrypt, tidak pernah plaintext.
    ● **CSRF** → setiap form POST menyertakan token (csrf_field/csrf_check).
    ● **Session fixation** → session_regenerate_id() setelah login.
    ● **Otorisasi** → requireRole() membatasi akses tiap halaman.
3. **Penamaan konsisten** — camelCase untuk fungsi/variabel, PascalCase
untuk kelas, nama deskriptif berbahasa Indonesia sesuai domain.
4. **DRY (Don't Repeat Yourself)** — layout & koneksi dipakai ulang; fungsi
terstruktur dipanggil oleh kelas OOP.
5. **Komentar & dokumentasi** — setiap berkas/method diberi komentar penjelas.
6. **Type declaration** — parameter & return type ditegaskan (mis. : bool).
7. **Error handling** — mode PDO::ERRMODE_EXCEPTION + pesan ramah pengguna.


## 11. Catatan Error / Debugging & Perbaikan (Output #6 & #7)

Tabel debugging selama pengembangan:
**# Error yang
Muncul
Penyebab Perbaikan Hasil**
1 SQLSTATE[HY000]^
[1045] Access
denied for user
'root'
Password MySQL
salah di config
Sesuaikan
Database::PASS
dengan XAMPP
(kosong)
Koneksi berhasil
2 Base^ table^ or^
view not found:
'db_nilai_siswa
.users'
Database belum
diimpor
Import
database/db_nil
ai_siswa.sql via
phpMyAdmin
Tabel tersedia
3 Login selalu gagal
walau password
benar
Awalnya password
disimpan
plaintext,
dibandingkan
dengan
password_verify
Simpan hash
bcrypt pada seed
& saat create user
Login berhasil
4 Nilai akhir tampil
tidak bulat (mis.
82.4999)
Hasil float tanpa
pembulatan
Tambahkan
round($na, 2)
pada
hitungNilaiAkhi
r()
Nilai rapi 2
desimal
5 Warning:^
Undefined array
key 'ref_id'
Akun guru/siswa
belum ditautkan
Tambah
pengecekan ?? ''
& pesan "hubungi
Admin"
Tidak ada warning
6 CSS/menu tidak
muncul di
subfolder
Path aset relatif
salah
Gunakan
BASE_URL absolut
yang dideteksi
otomatis
Aset tampil benar
_Lihat juga hasil pengujian otomatis fungsi inti pada **Tugas 3** (24/24 lolos)._


## 12. Fitur Tambahan (Pengembangan)

Selain kebutuhan inti, aplikasi dilengkapi fitur tambahan berikut:
**Fitur Berkas Keterangan
Download PDF native** siswa/sertifikat_pdf.php,
admin/laporan_pdf.php
Mengunduh surat keterangan &
laporan sebagai file PDF asli
memakai FPDF (bukan sekadar
print browser).
**Grafik statistik** admin/dashboard.php^ Grafik *doughnut* (lulus vs
tidak lulus) & *bar* (rata-rata
nilai per kelas) memakai
Chart.js.
**Export Excel** admin/laporan_excel.php^ Mengekspor data nilai ke berkas
.xls yang dapat dibuka di
Microsoft Excel.
**Ganti password mandiri** profil.php +
User::gantiPassword()
Setiap pengguna dapat
mengganti password sendiri
(verifikasi password lama).
// classes/User.php — ganti password mandiri
public function gantiPassword(int $id, string $lama, string $baru): array {
$user = $this->getById($id);
if (!$user || !password_verify($lama, $user['password'])) {
return ['ok' => false, 'msg' => 'Password lama salah.'];
}
$hash = password_hash($baru, PASSWORD_BCRYPT);
$stmt = $this->db->prepare('UPDATE users SET password =? WHERE id = ?');
$stmt->execute([$hash, $id]);
return ['ok' => true, 'msg' => 'Password berhasil diubah.'];
}

## Output Tugas 2 — Checklist

● ✓ Halaman login berdasarkan role
● ✓ Form input data siswa & nilai
● ✓ Proses perhitungan nilai akhir
● ✓ Laporan hasil nilai siswa
● ✓ Bukti pengujian database (koneksi PDO berhasil)
● ✓ Catatan error/debugging
● ✓ Perbaikan error & hasil setelah diperbaiki
● ✓ Potongan kode fungsi/procedure
● ✓ Potongan kode class & method
● ✓ Penjelasan library/komponen
● ✓ Penjelasan coding guidelines & best practices


