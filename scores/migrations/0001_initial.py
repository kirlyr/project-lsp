"""Migrasi awal skema ketat SSIS."""
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Membuat tabel users, siswa, guru, mata_pelajaran, dan nilai."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("username", models.CharField(max_length=150, unique=True)),
                ("role", models.CharField(choices=[("admin", "Admin"), ("guru", "Guru"), ("siswa", "Siswa")], max_length=10)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "users"},
        ),
        migrations.CreateModel(
            name="Guru",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("id_guru", models.CharField(max_length=30, unique=True)),
                ("nama_guru", models.CharField(max_length=150)),
                ("user", models.ForeignKey(db_column="user_id", on_delete=django.db.models.deletion.CASCADE, to="scores.user")),
            ],
            options={"db_table": "guru"},
        ),
        migrations.CreateModel(
            name="Siswa",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nis", models.CharField(max_length=30, unique=True)),
                ("nama", models.CharField(max_length=150)),
                ("kelas", models.CharField(max_length=50)),
                ("user", models.ForeignKey(db_column="user_id", on_delete=django.db.models.deletion.CASCADE, to="scores.user")),
            ],
            options={"db_table": "siswa"},
        ),
        migrations.CreateModel(
            name="MataPelajaran",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kode_mapel", models.CharField(max_length=30, unique=True)),
                ("nama_mapel", models.CharField(max_length=150)),
                ("guru", models.ForeignKey(db_column="guru_id", on_delete=django.db.models.deletion.CASCADE, to="scores.guru")),
            ],
            options={"db_table": "mata_pelajaran"},
        ),
        migrations.CreateModel(
            name="Nilai",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nilai_tugas", models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("nilai_uts", models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("nilai_uas", models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("nilai_akhir", models.DecimalField(decimal_places=2, editable=False, max_digits=5)),
                ("status_kelulusan", models.CharField(editable=False, max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("guru", models.ForeignKey(db_column="guru_id", on_delete=django.db.models.deletion.CASCADE, to="scores.guru")),
                ("mata_pelajaran", models.ForeignKey(db_column="mata_pelajaran_id", on_delete=django.db.models.deletion.CASCADE, to="scores.matapelajaran")),
                ("siswa", models.ForeignKey(db_column="siswa_id", on_delete=django.db.models.deletion.CASCADE, to="scores.siswa")),
            ],
            options={"db_table": "nilai"},
        ),
        migrations.RunSQL(
            sql=(
                "ALTER TABLE users MODIFY role "
                "ENUM('admin','guru','siswa') NOT NULL"
            ),
            reverse_sql="ALTER TABLE users MODIFY role VARCHAR(10) NOT NULL",
        ),
    ]
