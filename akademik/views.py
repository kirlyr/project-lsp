"""View autentikasi dan dashboard role untuk SSIS."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import role_required
from .forms import GuruForm, MataPelajaranForm, NilaiInputForm, SiswaForm
from .models import Guru, MataPelajaran, Nilai, Siswa, User
from .services import (
    buat_laporan_nilai,
    hitung_nilai_akhir,
    tentukan_status_kelulusan,
    validasi_nilai,
)


def login_view(request):
    """Menampilkan satu form login dan memproses autentikasi semua role."""
    if request.user.is_authenticated:
        return redirect("redirect_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("redirect_dashboard")

        messages.error(request, "Username atau password salah.")

    return render(request, "akademik/login.html")


@login_required
def redirect_dashboard(request):
    """Mengarahkan user login ke dashboard sesuai role."""
    role_redirects = {
        User.ROLE_ADMIN: "admin_dashboard",
        User.ROLE_GURU: "guru_dashboard",
        User.ROLE_SISWA: "siswa_dashboard",
    }
    return redirect(role_redirects[request.user.role])


@login_required
def logout_view(request):
    """Mengeluarkan user dari sesi aplikasi."""
    logout(request)
    return redirect("login")


@login_required
@role_required(User.ROLE_ADMIN)
def admin_dashboard(request):
    """Menampilkan ringkasan data untuk dashboard admin."""
    context = {
        "jumlah_siswa": Siswa.objects.count(),
        "jumlah_guru": Guru.objects.count(),
        "jumlah_mapel": MataPelajaran.objects.count(),
        "jumlah_user": User.objects.count(),
    }
    return render(request, "akademik/admin_dashboard.html", context)


@login_required
@role_required(User.ROLE_GURU)
def guru_dashboard(request):
    """Menampilkan dashboard khusus guru."""
    guru = get_object_or_404(Guru, user=request.user)
    context = {
        "jumlah_nilai": guru.get_rekap_nilai().count(),
        "jumlah_mapel": guru.matapelajaran_set.count(),
    }
    return render(request, "akademik/guru_dashboard.html", context)


@login_required
@role_required(User.ROLE_SISWA)
def siswa_dashboard(request):
    """Menampilkan dashboard siswa berisi profil milik sendiri."""
    siswa = get_object_or_404(Siswa.objects.select_related("user"), user=request.user)
    return render(request, "akademik/siswa_dashboard.html", {"siswa": siswa})


@login_required
@role_required(User.ROLE_ADMIN)
def siswa_list(request):
    """Menampilkan semua siswa dengan pencarian nama atau kelas."""
    query = request.GET.get("q", "").strip()
    siswa_list = Siswa.objects.select_related("user").order_by("kelas", "nama")

    if query:
        siswa_list = siswa_list.filter(Q(nama__icontains=query) | Q(kelas__icontains=query))

    return render(
        request,
        "akademik/siswa_list.html",
        {"siswa_list": siswa_list, "query": query},
    )


@login_required
@role_required(User.ROLE_ADMIN)
def siswa_tambah(request):
    """Menambah siswa dan membuat akun user otomatis dari NIS."""
    form = SiswaForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            siswa = form.save(commit=False)
            user = User.objects.create_user(
                username=siswa.nis,
                password=siswa.nis,
                role=User.ROLE_SISWA,
            )
            siswa.user = user
            siswa.save()
        messages.success(request, "Siswa dan akun login berhasil dibuat.")
        return redirect("siswa_list")

    return render(request, "akademik/siswa_form.html", {"form": form, "title": "Tambah Siswa"})


@login_required
@role_required(User.ROLE_ADMIN)
def siswa_edit(request, id):
    """Mengubah data siswa dan menyelaraskan username akun terkait."""
    siswa = get_object_or_404(Siswa.objects.select_related("user"), pk=id)
    form = SiswaForm(request.POST or None, instance=siswa)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            siswa = form.save()
            siswa.user.username = siswa.nis
            siswa.user.save(update_fields=["username"])
        messages.success(request, "Data siswa berhasil diperbarui.")
        return redirect("siswa_list")

    return render(request, "akademik/siswa_form.html", {"form": form, "title": "Edit Siswa"})


@login_required
@role_required(User.ROLE_ADMIN)
def siswa_hapus(request, id):
    """Menghapus siswa beserta akun user terkait."""
    siswa = get_object_or_404(Siswa.objects.select_related("user"), pk=id)

    if request.method == "POST":
        user = siswa.user
        user.delete()
        messages.success(request, "Siswa dan akun login berhasil dihapus.")
        return redirect("siswa_list")

    return render(request, "akademik/confirm_delete.html", {"object": siswa, "jenis": "siswa"})


@login_required
@role_required(User.ROLE_ADMIN)
def guru_list(request):
    """Menampilkan semua guru dengan pencarian nama atau ID guru."""
    query = request.GET.get("q", "").strip()
    guru_list = Guru.objects.select_related("user").order_by("nama_guru")

    if query:
        guru_list = guru_list.filter(
            Q(nama_guru__icontains=query) | Q(id_guru__icontains=query)
        )

    return render(
        request,
        "akademik/guru_list.html",
        {"guru_list": guru_list, "query": query},
    )


@login_required
@role_required(User.ROLE_ADMIN)
def guru_tambah(request):
    """Menambah guru dan membuat akun user otomatis dari ID guru."""
    form = GuruForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            guru = form.save(commit=False)
            user = User.objects.create_user(
                username=guru.id_guru,
                password=guru.id_guru,
                role=User.ROLE_GURU,
            )
            guru.user = user
            guru.save()
        messages.success(request, "Guru dan akun login berhasil dibuat.")
        return redirect("guru_list")

    return render(request, "akademik/guru_form.html", {"form": form, "title": "Tambah Guru"})


@login_required
@role_required(User.ROLE_ADMIN)
def guru_edit(request, id):
    """Mengubah data guru dan menyelaraskan username akun terkait."""
    guru = get_object_or_404(Guru.objects.select_related("user"), pk=id)
    form = GuruForm(request.POST or None, instance=guru)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            guru = form.save()
            guru.user.username = guru.id_guru
            guru.user.save(update_fields=["username"])
        messages.success(request, "Data guru berhasil diperbarui.")
        return redirect("guru_list")

    return render(request, "akademik/guru_form.html", {"form": form, "title": "Edit Guru"})


@login_required
@role_required(User.ROLE_ADMIN)
def guru_hapus(request, id):
    """Menghapus guru beserta akun user terkait."""
    guru = get_object_or_404(Guru.objects.select_related("user"), pk=id)

    if request.method == "POST":
        user = guru.user
        user.delete()
        messages.success(request, "Guru dan akun login berhasil dihapus.")
        return redirect("guru_list")

    return render(request, "akademik/confirm_delete.html", {"object": guru, "jenis": "guru"})


@login_required
@role_required(User.ROLE_ADMIN)
def mapel_list(request):
    """Menampilkan semua mata pelajaran dengan pencarian kode, nama, atau guru."""
    query = request.GET.get("q", "").strip()
    mapel_list = MataPelajaran.objects.select_related("guru").order_by("kode_mapel")

    if query:
        mapel_list = mapel_list.filter(
            Q(kode_mapel__icontains=query)
            | Q(nama_mapel__icontains=query)
            | Q(guru__nama_guru__icontains=query)
        )

    return render(
        request,
        "akademik/mapel_list.html",
        {"mapel_list": mapel_list, "query": query},
    )


@login_required
@role_required(User.ROLE_ADMIN)
def mapel_tambah(request):
    """Menambah data mata pelajaran dan guru pengampunya."""
    form = MataPelajaranForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Mata pelajaran berhasil dibuat.")
        return redirect("mapel_list")

    return render(
        request,
        "akademik/mapel_form.html",
        {"form": form, "title": "Tambah Mata Pelajaran"},
    )


@login_required
@role_required(User.ROLE_ADMIN)
def mapel_edit(request, id):
    """Mengubah data mata pelajaran dan guru pengampunya."""
    mapel = get_object_or_404(MataPelajaran.objects.select_related("guru"), pk=id)
    form = MataPelajaranForm(request.POST or None, instance=mapel)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Mata pelajaran berhasil diperbarui.")
        return redirect("mapel_list")

    return render(
        request,
        "akademik/mapel_form.html",
        {"form": form, "title": "Edit Mata Pelajaran"},
    )


@login_required
@role_required(User.ROLE_ADMIN)
def mapel_hapus(request, id):
    """Menghapus data mata pelajaran."""
    mapel = get_object_or_404(MataPelajaran, pk=id)

    if request.method == "POST":
        mapel.delete()
        messages.success(request, "Mata pelajaran berhasil dihapus.")
        return redirect("mapel_list")

    return render(
        request,
        "akademik/confirm_delete.html",
        {"object": mapel, "jenis": "mata pelajaran"},
    )


@login_required
@role_required(User.ROLE_GURU)
def nilai_input(request):
    """Menginput nilai siswa oleh guru dan menghitung hasil sebelum simpan."""
    guru = get_object_or_404(Guru, user=request.user)
    form = NilaiInputForm(request.POST or None, guru=guru)

    if request.method == "POST" and form.is_valid():
        nilai_tugas = form.cleaned_data["nilai_tugas"]
        nilai_uts = form.cleaned_data["nilai_uts"]
        nilai_uas = form.cleaned_data["nilai_uas"]

        validasi_nilai(nilai_tugas)
        validasi_nilai(nilai_uts)
        validasi_nilai(nilai_uas)
        nilai_akhir = hitung_nilai_akhir(nilai_tugas, nilai_uts, nilai_uas)
        status_kelulusan = tentukan_status_kelulusan(nilai_akhir)

        nilai, _ = Nilai.objects.update_or_create(
            siswa=form.cleaned_data["siswa"],
            guru=guru,
            mata_pelajaran=form.cleaned_data["mata_pelajaran"],
            defaults={
                "nilai_tugas": nilai_tugas,
                "nilai_uts": nilai_uts,
                "nilai_uas": nilai_uas,
                "nilai_akhir": nilai_akhir,
                "status_kelulusan": status_kelulusan,
            },
        )
        nilai.save()
        messages.success(request, "Nilai berhasil disimpan.")
        return redirect("nilai_rekap")

    return render(request, "akademik/nilai_input.html", {"form": form})


@login_required
@role_required(User.ROLE_GURU)
def nilai_rekap(request):
    """Menampilkan semua nilai yang pernah diinput oleh guru login."""
    guru = get_object_or_404(Guru, user=request.user)
    nilai_list = guru.get_rekap_nilai().order_by(
        "siswa__kelas",
        "siswa__nama",
        "mata_pelajaran__kode_mapel",
    )
    return render(request, "akademik/nilai_rekap.html", {"nilai_list": nilai_list})


@login_required
@role_required(User.ROLE_SISWA)
def nilai_saya(request):
    """Menampilkan seluruh nilai milik siswa login."""
    siswa = get_object_or_404(Siswa.objects.select_related("user"), user=request.user)
    nilai_list = siswa.get_nilai().order_by("mata_pelajaran__kode_mapel")
    return render(
        request,
        "akademik/nilai_saya.html",
        {"siswa": siswa, "nilai_list": nilai_list},
    )


@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GURU)
def laporan(request):
    """Menampilkan laporan nilai dengan filter dan tampilan siap cetak."""
    queryset = Nilai.objects.select_related("siswa", "guru", "mata_pelajaran")

    if request.user.role == User.ROLE_GURU:
        guru = get_object_or_404(Guru, user=request.user)
        queryset = queryset.filter(guru=guru)

    kelas = request.GET.get("kelas", "").strip()
    mata_pelajaran_id = request.GET.get("mata_pelajaran", "").strip()
    status_kelulusan = request.GET.get("status_kelulusan", "").strip()

    if kelas:
        queryset = queryset.filter(siswa__kelas=kelas)
    if mata_pelajaran_id:
        queryset = queryset.filter(mata_pelajaran_id=mata_pelajaran_id)
    if status_kelulusan:
        queryset = queryset.filter(status_kelulusan=status_kelulusan)

    queryset = queryset.order_by(
        "siswa__kelas",
        "siswa__nama",
        "mata_pelajaran__nama_mapel",
    )
    laporan_data = buat_laporan_nilai(queryset)

    kelas_options = Siswa.objects.order_by("kelas").values_list("kelas", flat=True)
    kelas_options = kelas_options.distinct()
    mapel_options = MataPelajaran.objects.order_by("nama_mapel")
    if request.user.role == User.ROLE_GURU:
        mapel_options = mapel_options.filter(guru__user=request.user)

    context = {
        "laporan": laporan_data,
        "kelas_options": kelas_options,
        "mapel_options": mapel_options,
        "status_options": ["Lulus", "Tidak Lulus"],
        "filters": {
            "kelas": kelas,
            "mata_pelajaran": mata_pelajaran_id,
            "status_kelulusan": status_kelulusan,
        },
        "print_mode": request.GET.get("print") == "1",
    }
    return render(request, "akademik/laporan.html", context)
