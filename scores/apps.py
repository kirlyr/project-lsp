"""Konfigurasi aplikasi nilai siswa."""
from django.apps import AppConfig


class ScoresConfig(AppConfig):
    """Mendaftarkan aplikasi scores di Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "scores"
