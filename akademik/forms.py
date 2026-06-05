"""Form admin dan guru untuk pengelolaan data akademik SSIS."""
from django import forms

from .models import Guru, MataPelajaran, Nilai, Siswa, User
from .services import validasi_nilai


class SiswaForm(forms.ModelForm):
    """Form tambah dan edit siswa dengan validasi NIS unik."""

    class Meta:
        """Mengatur field siswa yang diisi admin."""

        model = Siswa
        fields = ["nis", "nama", "kelas"]

    def clean_nis(self):
        """Memastikan NIS unik pada tabel siswa dan aman sebagai username."""
        nis = self.cleaned_data["nis"].strip()
        siswa_qs = Siswa.objects.filter(nis=nis)
        user_qs = User.objects.filter(username=nis)

        if self.instance.pk:
            siswa_qs = siswa_qs.exclude(pk=self.instance.pk)
            user_qs = user_qs.exclude(pk=self.instance.user_id)

        if siswa_qs.exists():
            raise forms.ValidationError("NIS sudah digunakan siswa lain.")
        if user_qs.exists():
            raise forms.ValidationError("NIS sudah digunakan sebagai username.")

        return nis


class GuruForm(forms.ModelForm):
    """Form tambah dan edit guru dengan validasi ID guru unik."""

    class Meta:
        """Mengatur field guru yang diisi admin."""

        model = Guru
        fields = ["id_guru", "nama_guru"]

    def clean_id_guru(self):
        """Memastikan ID guru unik dan aman sebagai username."""
        id_guru = self.cleaned_data["id_guru"].strip()
        guru_qs = Guru.objects.filter(id_guru=id_guru)
        user_qs = User.objects.filter(username=id_guru)

        if self.instance.pk:
            guru_qs = guru_qs.exclude(pk=self.instance.pk)
            user_qs = user_qs.exclude(pk=self.instance.user_id)

        if guru_qs.exists():
            raise forms.ValidationError("ID guru sudah digunakan guru lain.")
        if user_qs.exists():
            raise forms.ValidationError("ID guru sudah digunakan sebagai username.")

        return id_guru


class MataPelajaranForm(forms.ModelForm):
    """Form tambah dan edit mata pelajaran oleh admin."""

    class Meta:
        """Mengatur field mata pelajaran yang diisi admin."""

        model = MataPelajaran
        fields = ["kode_mapel", "nama_mapel", "guru"]

    def __init__(self, *args, **kwargs):
        """Mengurutkan pilihan guru agar mudah dipilih admin."""
        super().__init__(*args, **kwargs)
        self.fields["guru"].queryset = Guru.objects.order_by("nama_guru")

    def clean_kode_mapel(self):
        """Memastikan kode mata pelajaran unik."""
        kode_mapel = self.cleaned_data["kode_mapel"].strip().upper()
        mapel_qs = MataPelajaran.objects.filter(kode_mapel=kode_mapel)

        if self.instance.pk:
            mapel_qs = mapel_qs.exclude(pk=self.instance.pk)

        if mapel_qs.exists():
            raise forms.ValidationError("Kode mata pelajaran sudah digunakan.")

        return kode_mapel


class NilaiInputForm(forms.ModelForm):
    """Form input nilai oleh guru untuk siswa dan mata pelajaran."""

    class Meta:
        """Mengatur field nilai yang dapat diisi guru."""

        model = Nilai
        fields = [
            "siswa",
            "mata_pelajaran",
            "nilai_tugas",
            "nilai_uts",
            "nilai_uas",
        ]

    def __init__(self, *args, guru=None, **kwargs):
        """Membatasi pilihan mata pelajaran sesuai guru yang login."""
        super().__init__(*args, **kwargs)
        self.guru = guru
        self.fields["siswa"].queryset = Siswa.objects.order_by("kelas", "nama")
        if guru is not None:
            self.fields["mata_pelajaran"].queryset = MataPelajaran.objects.filter(
                guru=guru
            ).order_by("kode_mapel")

    def clean_nilai_tugas(self):
        """Memvalidasi nilai tugas pada rentang 0 sampai 100."""
        nilai = self.cleaned_data["nilai_tugas"]
        validasi_nilai(nilai)
        return nilai

    def clean_nilai_uts(self):
        """Memvalidasi nilai UTS pada rentang 0 sampai 100."""
        nilai = self.cleaned_data["nilai_uts"]
        validasi_nilai(nilai)
        return nilai

    def clean_nilai_uas(self):
        """Memvalidasi nilai UAS pada rentang 0 sampai 100."""
        nilai = self.cleaned_data["nilai_uas"]
        validasi_nilai(nilai)
        return nilai

    def clean_mata_pelajaran(self):
        """Memastikan guru hanya memilih mata pelajaran miliknya."""
        mata_pelajaran = self.cleaned_data["mata_pelajaran"]
        if self.guru is not None and mata_pelajaran.guru_id != self.guru.id:
            raise forms.ValidationError("Mata pelajaran tidak sesuai dengan guru login.")
        return mata_pelajaran
