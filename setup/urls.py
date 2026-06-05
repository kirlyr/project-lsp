"""Konfigurasi URL utama proyek SSIS."""
from django.http import HttpResponse
from django.urls import include, path


def home(request):
    """Menampilkan respons sederhana untuk pengecekan proyek."""
    return HttpResponse("SchoolScore Information Sistem aktif.")


urlpatterns = [
    path("", home, name="home"),
    path("", include("akademik.urls")),
]
