# Initial migration for the clinic app. Generated-equivalent Django ORM migration.
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Doctor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("specialization", models.CharField(max_length=150)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=16, validators=[RegexValidator("^\\+?[0-9]{7,15}$", "Use 7–15 digits, optionally starting with +.")])),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="doctors", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("age", models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])),
                ("gender", models.CharField(blank=True, choices=[("female", "Female"), ("male", "Male"), ("other", "Other"), ("undisclosed", "Prefer not to say")], max_length=20)),
                ("phone", models.CharField(blank=True, max_length=16, validators=[RegexValidator("^\\+?[0-9]{7,15}$", "Use 7–15 digits, optionally starting with +.")])),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="patients", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="PatientDoctorMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("assigned_at", models.DateTimeField(auto_now_add=True)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="patient_mappings", to="clinic.doctor")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="doctor_mappings", to="clinic.patient")),
            ],
            options={"constraints": [models.UniqueConstraint(fields=("patient", "doctor"), name="unique_patient_doctor")]},
        ),
    ]
