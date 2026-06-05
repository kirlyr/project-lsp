"""Layanan bisnis untuk perhitungan dan laporan nilai."""
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError


def validasi_nilai(nilai):
    """Memvalidasi nilai agar berada pada rentang 0 sampai 100."""
    nilai_decimal = Decimal(str(nilai))
    if nilai_decimal < 0 or nilai_decimal > 100:
        raise ValidationError("Nilai harus berada pada rentang 0 sampai 100.")
    return True


def hitung_nilai_akhir(tugas, uts, uas):
    """Menghitung nilai akhir dari komponen tugas, UTS, dan UAS."""
    for nilai in (tugas, uts, uas):
        validasi_nilai(nilai)

    hasil = (
        Decimal(str(tugas)) * Decimal("0.3")
        + Decimal(str(uts)) * Decimal("0.3")
        + Decimal(str(uas)) * Decimal("0.4")
    )
    return float(hasil.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def tentukan_status_kelulusan(nilai_akhir):
    """Menentukan status kelulusan berdasarkan nilai akhir."""
    validasi_nilai(nilai_akhir)
    return "Lulus" if Decimal(str(nilai_akhir)) >= Decimal("70") else "Tidak Lulus"


def buat_laporan_nilai(queryset):
    """Membentuk data laporan nilai dari queryset nilai."""
    data = []
    for nilai in queryset.select_related("siswa", "guru", "mata_pelajaran"):
        data.append(
            {
                "nis": nilai.siswa.nis,
                "nama_siswa": nilai.siswa.nama,
                "kelas": nilai.siswa.kelas,
                "guru": nilai.guru.nama_guru,
                "kode_mapel": nilai.mata_pelajaran.kode_mapel,
                "mata_pelajaran": nilai.mata_pelajaran.nama_mapel,
                "nilai_tugas": nilai.nilai_tugas,
                "nilai_uts": nilai.nilai_uts,
                "nilai_uas": nilai.nilai_uas,
                "nilai_akhir": nilai.nilai_akhir,
                "status_kelulusan": nilai.status_kelulusan,
            }
        )
    return data
