"""Model data utama untuk SchoolScore Information Sistem."""
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .managers import UserManager
from .services import hitung_nilai_akhir, tentukan_status_kelulusan, validasi_nilai


class User(AbstractBaseUser):
    """Model pengguna SSIS dengan role admin, guru, atau siswa."""

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
        """Mengikat model user ke tabel users."""

        db_table = "users"

    @property
    def is_staff(self):
        """Menandai admin sebagai staff untuk kompatibilitas auth."""
        return self.role == self.ROLE_ADMIN

    @property
    def is_superuser(self):
        """Menandai admin sebagai superuser untuk kompatibilitas auth."""
        return self.role == self.ROLE_ADMIN

    def has_perm(self, perm, obj=None):
        """Memberikan seluruh permission kepada admin."""
        return self.role == self.ROLE_ADMIN

    def has_module_perms(self, app_label):
        """Memberikan akses modul kepada admin."""
        return self.role == self.ROLE_ADMIN


class Siswa(models.Model):
    """Model siswa dengan profil dan akses nilai pribadi."""

    nis = models.CharField(max_length=30, unique=True)
    nama = models.CharField(max_length=150)
    kelas = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")

    class Meta:
        """Mengikat model siswa ke tabel siswa."""

        db_table = "siswa"

    def __str__(self):
        """Mengembalikan representasi nama siswa."""
        return f"{self.nis} - {self.nama}"

    def get_nilai(self):
        """Mengambil seluruh nilai milik siswa."""
        return self.nilai_set.select_related("guru", "mata_pelajaran")

    def get_status_kelulusan(self):
        """Mengambil daftar status kelulusan siswa per mata pelajaran."""
        return [
            {
                "mata_pelajaran": nilai.mata_pelajaran.nama_mapel,
                "status_kelulusan": nilai.status_kelulusan,
            }
            for nilai in self.get_nilai()
        ]

    def get_profile(self):
        """Mengambil data profil siswa dalam bentuk dictionary."""
        return {"nis": self.nis, "nama": self.nama, "kelas": self.kelas}


class Guru(models.Model):
    """Model guru dengan akses input, rekap, dan validasi nilai."""

    id_guru = models.CharField(max_length=30, unique=True)
    nama_guru = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")

    class Meta:
        """Mengikat model guru ke tabel guru."""

        db_table = "guru"

    def __str__(self):
        """Mengembalikan representasi nama guru."""
        return f"{self.id_guru} - {self.nama_guru}"

    def input_nilai(self, siswa, mata_pelajaran, nilai_tugas, nilai_uts, nilai_uas):
        """Menyimpan nilai siswa untuk mata pelajaran yang diajar guru."""
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
    """Model mata pelajaran yang diampu oleh guru."""

    kode_mapel = models.CharField(max_length=30, unique=True)
    nama_mapel = models.CharField(max_length=150)
    guru = models.ForeignKey(Guru, on_delete=models.CASCADE, db_column="guru_id")

    class Meta:
        """Mengikat model mata pelajaran ke tabel mata_pelajaran."""

        db_table = "mata_pelajaran"

    def __str__(self):
        """Mengembalikan representasi nama mata pelajaran."""
        return f"{self.kode_mapel} - {self.nama_mapel}"

    def get_nilai_siswa(self):
        """Mengambil nilai siswa untuk mata pelajaran ini."""
        return self.nilai_set.select_related("siswa", "guru")


class Nilai(models.Model):
    """Model nilai siswa untuk satu mata pelajaran dan guru."""

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
        """Mengikat model nilai ke tabel nilai."""

        db_table = "nilai"

    def __str__(self):
        """Mengembalikan representasi nilai siswa."""
        return f"{self.siswa.nama} - {self.mata_pelajaran.nama_mapel}"

    def hitung_nilai_akhir(self):
        """Menghitung nilai akhir dari nilai tugas, UTS, dan UAS."""
        return hitung_nilai_akhir(self.nilai_tugas, self.nilai_uts, self.nilai_uas)

    def tentukan_status(self):
        """Menentukan status kelulusan dari nilai akhir."""
        return tentukan_status_kelulusan(self.nilai_akhir)

    def clean(self):
        """Memvalidasi rentang semua komponen nilai."""
        validasi_nilai(self.nilai_tugas)
        validasi_nilai(self.nilai_uts)
        validasi_nilai(self.nilai_uas)

    def save(self, *args, **kwargs):
        """Menghitung nilai akhir dan status sebelum menyimpan data."""
        self.full_clean()
        self.nilai_akhir = self.hitung_nilai_akhir()
        self.status_kelulusan = tentukan_status_kelulusan(self.nilai_akhir)
        super().save(*args, **kwargs)
