"""Manager pengguna untuk autentikasi SSIS."""
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Mengelola pembuatan user berdasarkan role SSIS."""

    def create_user(self, username, password=None, role="siswa", **extra_fields):
        """Membuat user aktif dengan username, password, dan role."""
        if not username:
            raise ValueError("Username wajib diisi.")
        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """Membuat user admin untuk kebutuhan superuser Django."""
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, password, **extra_fields)
