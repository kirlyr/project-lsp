"""Konfigurasi aplikasi akademik."""
from django.apps import AppConfig


class AkademikConfig(AppConfig):
    """Mendaftarkan aplikasi akademik pada proyek Django."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'akademik'
