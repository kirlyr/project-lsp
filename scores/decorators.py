"""Decorator akses berdasarkan role pengguna."""
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Membatasi akses view hanya untuk role yang diizinkan."""
    def decorator(view_func):
        """Membungkus view dengan pemeriksaan role."""
        def wrapper(request, *args, **kwargs):
            """Menjalankan view jika role user sesuai."""
            if request.user.is_authenticated and request.user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("Anda tidak memiliki akses ke halaman ini.")

        return wrapper

    return decorator
