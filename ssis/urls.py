"""Konfigurasi URL utama untuk aplikasi SSIS."""
from django.urls import include, path

urlpatterns = [
    path("", include("scores.urls")),
]
