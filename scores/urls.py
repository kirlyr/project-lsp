"""URL aplikasi scores untuk SSIS."""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("users/", views.user_list, name="user_list"),
    path("users/tambah/", views.user_form, name="user_create"),
    path("users/<int:pk>/ubah/", views.user_form, name="user_update"),
    path("users/<int:pk>/hapus/", views.user_delete, name="user_delete"),
    path("siswa/", views.siswa_list, name="siswa_list"),
    path("siswa/tambah/", views.siswa_form, name="siswa_create"),
    path("siswa/<int:pk>/ubah/", views.siswa_form, name="siswa_update"),
    path("siswa/<int:pk>/hapus/", views.siswa_delete, name="siswa_delete"),
    path("guru/", views.guru_list, name="guru_list"),
    path("guru/tambah/", views.guru_form, name="guru_create"),
    path("guru/<int:pk>/ubah/", views.guru_form, name="guru_update"),
    path("guru/<int:pk>/hapus/", views.guru_delete, name="guru_delete"),
    path("mapel/", views.mapel_list, name="mapel_list"),
    path("mapel/tambah/", views.mapel_form, name="mapel_create"),
    path("mapel/<int:pk>/ubah/", views.mapel_form, name="mapel_update"),
    path("mapel/<int:pk>/hapus/", views.mapel_delete, name="mapel_delete"),
    path("nilai/input/", views.nilai_form, name="nilai_create"),
    path("nilai/<int:pk>/ubah/", views.nilai_form, name="nilai_update"),
    path("nilai/<int:pk>/hapus/", views.nilai_delete, name="nilai_delete"),
    path("rekap/", views.rekap_guru, name="rekap_guru"),
    path("nilai-saya/", views.nilai_saya, name="nilai_saya"),
    path("laporan/", views.laporan_nilai, name="laporan_nilai"),
]
