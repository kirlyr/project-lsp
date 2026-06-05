"""Manager user untuk autentikasi role SSIS."""
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Mengelola pembuatan user berdasarkan username dan role."""

    def create_user(self, username, password=None, role="siswa", **extra_fields):
        """Membuat user aktif dengan password yang di-hash."""
        if not username:
            raise ValueError("Username wajib diisi.")

        user = self.model(username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """Membuat superuser dengan role admin."""
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, password, **extra_fields)
