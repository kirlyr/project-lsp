"""URL autentikasi dan dashboard role untuk aplikasi akademik."""
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.redirect_dashboard, name="redirect_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/admin-dashboard/", views.admin_dashboard, name="admin_dashboard_legacy"),
    path("guru/guru-dashboard/", views.guru_dashboard, name="guru_dashboard"),
    path("siswa-dashboard/", views.siswa_dashboard, name="siswa_dashboard"),
    path("siswa/siswa-dashboard/", views.siswa_dashboard, name="siswa_dashboard_legacy"),
    path("siswa/", views.siswa_list, name="siswa_list"),
    path("siswa/tambah/", views.siswa_tambah, name="siswa_tambah"),
    path("siswa/edit/<int:id>/", views.siswa_edit, name="siswa_edit"),
    path("siswa/hapus/<int:id>/", views.siswa_hapus, name="siswa_hapus"),
    path("guru/", views.guru_list, name="guru_list"),
    path("guru/tambah/", views.guru_tambah, name="guru_tambah"),
    path("guru/edit/<int:id>/", views.guru_edit, name="guru_edit"),
    path("guru/hapus/<int:id>/", views.guru_hapus, name="guru_hapus"),
    path("mapel/", views.mapel_list, name="mapel_list"),
    path("mapel/tambah/", views.mapel_tambah, name="mapel_tambah"),
    path("mapel/edit/<int:id>/", views.mapel_edit, name="mapel_edit"),
    path("mapel/hapus/<int:id>/", views.mapel_hapus, name="mapel_hapus"),
    path("nilai/input/", views.nilai_input, name="nilai_input"),
    path("nilai/rekap/", views.nilai_rekap, name="nilai_rekap"),
    path("nilai/saya/", views.nilai_saya, name="nilai_saya"),
    path("laporan/", views.laporan, name="laporan"),
]
