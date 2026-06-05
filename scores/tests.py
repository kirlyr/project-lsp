"""Tes unit untuk aturan bisnis nilai SSIS."""
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .services import (
    hitung_nilai_akhir,
    tentukan_status_kelulusan,
    validasi_nilai,
)


class ServiceNilaiTests(SimpleTestCase):
    """Menguji fungsi terstruktur untuk perhitungan nilai."""

    def test_validasi_nilai_menerima_rentang_valid(self):
        """Memastikan nilai 0 sampai 100 diterima."""
        self.assertTrue(validasi_nilai(0))
        self.assertTrue(validasi_nilai(100))

    def test_validasi_nilai_menolak_rentang_tidak_valid(self):
        """Memastikan nilai di luar rentang ditolak."""
        with self.assertRaises(ValidationError):
            validasi_nilai(101)

    def test_hitung_nilai_akhir(self):
        """Memastikan formula nilai akhir sesuai aturan."""
        self.assertEqual(hitung_nilai_akhir(80, 70, 90), 81.0)

    def test_tentukan_status_kelulusan(self):
        """Memastikan status kelulusan memakai batas 70."""
        self.assertEqual(tentukan_status_kelulusan(70), "Lulus")
        self.assertEqual(tentukan_status_kelulusan(69.99), "Tidak Lulus")
