"""View web untuk dashboard dan CRUD SSIS."""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import role_required
from .forms import GuruForm, MataPelajaranForm, NilaiForm, SiswaForm, UserForm
from .models import Guru, MataPelajaran, Nilai, Siswa, User
from .services import buat_laporan_nilai


def login_view(request):
    """Menangani login user dengan Django auth."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Username atau password salah.")
    return render(request, "scores/login.html")


def logout_view(request):
    """Menangani logout user."""
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    """Mengarahkan dashboard sesuai role pengguna."""
    if request.user.role == User.ROLE_SISWA:
        return redirect("nilai_saya")
    if request.user.role == User.ROLE_GURU:
        return redirect("rekap_guru")
    return redirect("laporan_nilai")


@login_required
@role_required(User.ROLE_ADMIN)
def user_list(request):
    """Menampilkan daftar user untuk admin."""
    users = User.objects.order_by("username")
    return render(request, "scores/generic_list.html", {"title": "User", "items": users})


@login_required
@role_required(User.ROLE_ADMIN)
def user_form(request, pk=None):
    """Membuat atau mengubah data user."""
    instance = get_object_or_404(User, pk=pk) if pk else None
    form = UserForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("user_list")
    return render(request, "scores/form.html", {"title": "User", "form": form})


@login_required
@role_required(User.ROLE_ADMIN)
def user_delete(request, pk):
    """Menghapus data user melalui konfirmasi POST."""
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.delete()
        return redirect("user_list")
    return render(request, "scores/confirm_delete.html", {"object": user})


@login_required
@role_required(User.ROLE_ADMIN)
def siswa_list(request):
    """Menampilkan daftar siswa untuk admin."""
    siswa = Siswa.objects.select_related("user").order_by("kelas", "nama")
    return render(request, "scores/generic_list.html", {"title": "Siswa", "items": siswa})


@login_required
@role_required(User.ROLE_ADMIN)
def siswa_form(request, pk=None):
    """Membuat atau mengubah data siswa."""
    instance = get_object_or_404(Siswa, pk=pk) if pk else None
    form = SiswaForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("siswa_list")
    return render(request, "scores/form.html", {"title": "Siswa", "form": form})


@login_required
@role_required(User.ROLE_ADMIN)
def siswa_delete(request, pk):
    """Menghapus data siswa melalui konfirmasi POST."""
    siswa = get_object_or_404(Siswa, pk=pk)
    if request.method == "POST":
        siswa.delete()
        return redirect("siswa_list")
    return render(request, "scores/confirm_delete.html", {"object": siswa})


@login_required
@role_required(User.ROLE_ADMIN)
def guru_list(request):
    """Menampilkan daftar guru untuk admin."""
    guru = Guru.objects.select_related("user").order_by("nama_guru")
    return render(request, "scores/generic_list.html", {"title": "Guru", "items": guru})


@login_required
@role_required(User.ROLE_ADMIN)
def guru_form(request, pk=None):
    """Membuat atau mengubah data guru."""
    instance = get_object_or_404(Guru, pk=pk) if pk else None
    form = GuruForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("guru_list")
    return render(request, "scores/form.html", {"title": "Guru", "form": form})


@login_required
@role_required(User.ROLE_ADMIN)
def guru_delete(request, pk):
    """Menghapus data guru melalui konfirmasi POST."""
    guru = get_object_or_404(Guru, pk=pk)
    if request.method == "POST":
        guru.delete()
        return redirect("guru_list")
    return render(request, "scores/confirm_delete.html", {"object": guru})


@login_required
@role_required(User.ROLE_ADMIN)
def mapel_list(request):
    """Menampilkan daftar mata pelajaran untuk admin."""
    mapel = MataPelajaran.objects.select_related("guru").order_by("kode_mapel")
    return render(request, "scores/generic_list.html", {"title": "Mata Pelajaran", "items": mapel})


@login_required
@role_required(User.ROLE_ADMIN)
def mapel_form(request, pk=None):
    """Membuat atau mengubah data mata pelajaran."""
    instance = get_object_or_404(MataPelajaran, pk=pk) if pk else None
    form = MataPelajaranForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("mapel_list")
    return render(request, "scores/form.html", {"title": "Mata Pelajaran", "form": form})


@login_required
@role_required(User.ROLE_ADMIN)
def mapel_delete(request, pk):
    """Menghapus data mata pelajaran melalui konfirmasi POST."""
    mapel = get_object_or_404(MataPelajaran, pk=pk)
    if request.method == "POST":
        mapel.delete()
        return redirect("mapel_list")
    return render(request, "scores/confirm_delete.html", {"object": mapel})


@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GURU)
def nilai_form(request, pk=None):
    """Membuat atau mengubah nilai oleh admin atau guru."""
    instance = get_object_or_404(Nilai, pk=pk) if pk else None
    form = NilaiForm(request.POST or None, instance=instance)
    if request.user.role == User.ROLE_GURU:
        guru = get_object_or_404(Guru, user=request.user)
        if instance and instance.guru_id != guru.id:
            raise PermissionDenied("Guru hanya boleh mengubah nilai miliknya.")
        form.fields["guru"].initial = guru
        form.fields["guru"].queryset = Guru.objects.filter(pk=guru.pk)
        form.fields["mata_pelajaran"].queryset = MataPelajaran.objects.filter(guru=guru)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("rekap_guru" if request.user.role == User.ROLE_GURU else "laporan_nilai")
    return render(request, "scores/form.html", {"title": "Nilai", "form": form})


@login_required
@role_required(User.ROLE_ADMIN)
def nilai_delete(request, pk):
    """Menghapus data nilai melalui konfirmasi POST."""
    nilai = get_object_or_404(Nilai, pk=pk)
    if request.method == "POST":
        nilai.delete()
        return redirect("laporan_nilai")
    return render(request, "scores/confirm_delete.html", {"object": nilai})


@login_required
@role_required(User.ROLE_ADMIN, User.ROLE_GURU)
def rekap_guru(request):
    """Menampilkan rekap nilai untuk guru atau seluruh guru bagi admin."""
    if request.user.role == User.ROLE_GURU:
        guru = get_object_or_404(Guru, user=request.user)
        nilai = guru.get_rekap_nilai()
    else:
        nilai = Nilai.objects.select_related("siswa", "guru", "mata_pelajaran")
    return render(request, "scores/nilai_table.html", {"title": "Rekap Nilai", "nilai_list": nilai})


@login_required
@role_required(User.ROLE_SISWA)
def nilai_saya(request):
    """Menampilkan nilai dan status kelulusan milik siswa login."""
    siswa = get_object_or_404(Siswa, user=request.user)
    return render(
        request,
        "scores/nilai_table.html",
        {"title": "Nilai Saya", "nilai_list": siswa.get_nilai(), "read_only": True},
    )


@login_required
@role_required(User.ROLE_ADMIN)
def laporan_nilai(request):
    """Menampilkan laporan nilai terformat untuk admin."""
    queryset = Nilai.objects.select_related("siswa", "guru", "mata_pelajaran")
    laporan = buat_laporan_nilai(queryset)
    return render(request, "scores/laporan.html", {"laporan": laporan})
