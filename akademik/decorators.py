"""Decorator akses role untuk halaman akademik SSIS."""
from functools import wraps

from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """Membatasi akses view hanya untuk role yang diizinkan."""
    def decorator(view_func):
        """Membungkus view dengan pemeriksaan role user."""
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            """Menjalankan view jika user login dan role sesuai."""
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("Anda tidak memiliki akses ke halaman ini.")

        return wrapper

    return decorator
