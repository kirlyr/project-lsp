"""Model database SSIS sesuai skema akademik yang ditentukan."""
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .managers import UserManager
from .services import hitung_nilai_akhir, tentukan_status_kelulusan, validasi_nilai


class User(AbstractBaseUser):
    """Model tabel users untuk autentikasi dan role pengguna."""

    ROLE_ADMIN = "admin"
    ROLE_GURU = "guru"
    ROLE_SISWA = "siswa"
    ROLE_CHOICES = (
        (ROLE_ADMIN, "Admin"),
        (ROLE_GURU, "Guru"),
        (ROLE_SISWA, "Siswa"),
    )

    last_login = None
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        """Menghubungkan model User ke tabel users."""

        db_table = "users"

    @property
    def is_staff(self):
        """Mengizinkan role admin mengakses fitur staff Django."""
        return self.role == self.ROLE_ADMIN

    @property
    def is_superuser(self):
        """Menganggap role admin sebagai superuser aplikasi."""
        return self.role == self.ROLE_ADMIN

    def has_perm(self, perm, obj=None):
        """Memberikan seluruh permission hanya kepada admin."""
        return self.role == self.ROLE_ADMIN

    def has_module_perms(self, app_label):
        """Memberikan akses modul Django hanya kepada admin."""
        return self.role == self.ROLE_ADMIN

    def __str__(self):
        """Mengembalikan username sebagai representasi user."""
        return self.username


class Siswa(models.Model):
    """Model tabel siswa dengan data NIS, nama, kelas, dan user terkait."""

    nis = models.CharField(max_length=30, unique=True)
    nama = models.CharField(max_length=150)
    kelas = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")

    class Meta:
        """Menghubungkan model Siswa ke tabel siswa."""

        db_table = "siswa"

    def __str__(self):
        """Mengembalikan identitas ringkas siswa."""
        return f"{self.nis} - {self.nama}"

    def get_nilai(self):
        """Mengambil seluruh nilai milik siswa."""
        return self.nilai_set.select_related("guru", "mata_pelajaran")

    def get_status_kelulusan(self):
        """Mengambil status kelulusan siswa untuk setiap mata pelajaran."""
        return [
            {
                "kode_mapel": nilai.mata_pelajaran.kode_mapel,
                "nama_mapel": nilai.mata_pelajaran.nama_mapel,
                "status_kelulusan": nilai.status_kelulusan,
            }
            for nilai in self.get_nilai()
        ]

    def get_profile(self):
        """Mengambil profil siswa dalam bentuk dictionary."""
        return {
            "nis": self.nis,
            "nama": self.nama,
            "kelas": self.kelas,
            "username": self.user.username,
        }


class Guru(models.Model):
    """Model tabel guru dengan data ID guru, nama guru, dan user terkait."""

    id_guru = models.CharField(max_length=30, unique=True)
    nama_guru = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")

    class Meta:
        """Menghubungkan model Guru ke tabel guru."""

        db_table = "guru"

    def __str__(self):
        """Mengembalikan identitas ringkas guru."""
        return f"{self.id_guru} - {self.nama_guru}"

    def input_nilai(self, siswa, mata_pelajaran, nilai_tugas, nilai_uts, nilai_uas):
        """Membuat atau memperbarui nilai siswa untuk mata pelajaran guru."""
        if mata_pelajaran.guru_id != self.id:
            raise ValueError("Guru hanya dapat menginput nilai mata pelajarannya.")

        nilai, _ = Nilai.objects.update_or_create(
            siswa=siswa,
            guru=self,
            mata_pelajaran=mata_pelajaran,
            defaults={
                "nilai_tugas": nilai_tugas,
                "nilai_uts": nilai_uts,
                "nilai_uas": nilai_uas,
            },
        )
        nilai.save()
        return nilai

    def get_rekap_nilai(self):
        """Mengambil rekap nilai yang diinput oleh guru."""
        return self.nilai_set.select_related("siswa", "mata_pelajaran")

    def validasi_nilai(self, nilai):
        """Memvalidasi nilai memakai aturan rentang SSIS."""
        return validasi_nilai(nilai)


class MataPelajaran(models.Model):
    """Model tabel mata_pelajaran untuk data mapel dan guru pengampu."""

    kode_mapel = models.CharField(max_length=30, unique=True)
    nama_mapel = models.CharField(max_length=150)
    guru = models.ForeignKey(Guru, on_delete=models.CASCADE, db_column="guru_id")

    class Meta:
        """Menghubungkan model MataPelajaran ke tabel mata_pelajaran."""

        db_table = "mata_pelajaran"

    def __str__(self):
        """Mengembalikan identitas ringkas mata pelajaran."""
        return f"{self.kode_mapel} - {self.nama_mapel}"

    def get_nilai_siswa(self):
        """Mengambil seluruh nilai siswa pada mata pelajaran ini."""
        return self.nilai_set.select_related("siswa", "guru")


class Nilai(models.Model):
    """Model tabel nilai untuk komponen nilai dan status kelulusan siswa."""

    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, db_column="siswa_id")
    guru = models.ForeignKey(Guru, on_delete=models.CASCADE, db_column="guru_id")
    mata_pelajaran = models.ForeignKey(
        MataPelajaran,
        on_delete=models.CASCADE,
        db_column="mata_pelajaran_id",
    )
    nilai_tugas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    nilai_uts = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    nilai_uas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    nilai_akhir = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    status_kelulusan = models.CharField(max_length=20, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Menghubungkan model Nilai ke tabel nilai."""

        db_table = "nilai"

    def __str__(self):
        """Mengembalikan identitas ringkas nilai siswa."""
        return f"{self.siswa.nama} - {self.mata_pelajaran.nama_mapel}"

    def hitung_nilai_akhir(self):
        """Menghitung nilai akhir dari tugas, UTS, dan UAS."""
        return hitung_nilai_akhir(self.nilai_tugas, self.nilai_uts, self.nilai_uas)

    def tentukan_status(self):
        """Menentukan status kelulusan berdasarkan nilai akhir."""
        return tentukan_status_kelulusan(self.nilai_akhir)

    def clean(self):
        """Memvalidasi semua komponen nilai sebelum disimpan."""
        validasi_nilai(self.nilai_tugas)
        validasi_nilai(self.nilai_uts)
        validasi_nilai(self.nilai_uas)

    def save(self, *args, **kwargs):
        """Menghitung nilai akhir dan status kelulusan sebelum menyimpan."""
        self.full_clean()
        self.nilai_akhir = self.hitung_nilai_akhir()
        self.status_kelulusan = tentukan_status_kelulusan(self.nilai_akhir)
        super().save(*args, **kwargs)
