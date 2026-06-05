"""Form input dan validasi data SSIS."""
from django import forms

from .models import Guru, MataPelajaran, Nilai, Siswa, User
from .services import validasi_nilai


class UserForm(forms.ModelForm):
    """Form untuk membuat dan mengubah data user."""

    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        """Mengatur field user yang dapat diisi dari form."""

        model = User
        fields = ["username", "password", "role", "is_active"]

    def save(self, commit=True):
        """Menyimpan user dan mengenkripsi password bila diisi."""
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class SiswaForm(forms.ModelForm):
    """Form CRUD data siswa."""

    class Meta:
        """Mengatur field siswa yang dapat diisi dari form."""

        model = Siswa
        fields = ["nis", "nama", "kelas", "user"]


class GuruForm(forms.ModelForm):
    """Form CRUD data guru."""

    class Meta:
        """Mengatur field guru yang dapat diisi dari form."""

        model = Guru
        fields = ["id_guru", "nama_guru", "user"]


class MataPelajaranForm(forms.ModelForm):
    """Form CRUD data mata pelajaran."""

    class Meta:
        """Mengatur field mata pelajaran yang dapat diisi dari form."""

        model = MataPelajaran
        fields = ["kode_mapel", "nama_mapel", "guru"]


class NilaiForm(forms.ModelForm):
    """Form input nilai dengan validasi rentang 0 sampai 100."""

    class Meta:
        """Mengatur field nilai yang dapat diisi dari form."""

        model = Nilai
        fields = [
            "siswa",
            "guru",
            "mata_pelajaran",
            "nilai_tugas",
            "nilai_uts",
            "nilai_uas",
        ]

    def clean_nilai_tugas(self):
        """Memvalidasi nilai tugas."""
        nilai = self.cleaned_data["nilai_tugas"]
        validasi_nilai(nilai)
        return nilai

    def clean_nilai_uts(self):
        """Memvalidasi nilai UTS."""
        nilai = self.cleaned_data["nilai_uts"]
        validasi_nilai(nilai)
        return nilai

    def clean_nilai_uas(self):
        """Memvalidasi nilai UAS."""
        nilai = self.cleaned_data["nilai_uas"]
        validasi_nilai(nilai)
        return nilai
