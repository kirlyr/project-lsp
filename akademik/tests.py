"""Tes unit untuk fungsi bisnis akademik SSIS."""
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from .services import (
    hitung_nilai_akhir,
    tentukan_status_kelulusan,
    validasi_nilai,
)


class FungsiNilaiTests(SimpleTestCase):
    """Menguji validasi, perhitungan, dan status kelulusan nilai."""

    def test_validasi_nilai_valid(self):
        """Memastikan nilai pada rentang 0 sampai 100 diterima."""
        self.assertTrue(validasi_nilai(0))
        self.assertTrue(validasi_nilai(100))

    def test_validasi_nilai_tidak_valid(self):
        """Memastikan nilai di luar rentang 0 sampai 100 ditolak."""
        with self.assertRaises(ValidationError):
            validasi_nilai(101)

    def test_hitung_nilai_akhir(self):
        """Memastikan formula nilai akhir sesuai aturan SSIS."""
        self.assertEqual(hitung_nilai_akhir(80, 70, 90), 81.0)

    def test_tentukan_status_kelulusan(self):
        """Memastikan status kelulusan memakai ambang batas 70."""
        self.assertEqual(tentukan_status_kelulusan(70), "Lulus")
        self.assertEqual(tentukan_status_kelulusan(69.99), "Tidak Lulus")
