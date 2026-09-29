from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

phone_validator = RegexValidator(r"^\+?[0-9]{7,15}$", "Use 7–15 digits, optionally starting with +.")


class Patient(models.Model):
    GENDER_CHOICES = [
        ("female", "Female"), ("male", "Male"),
        ("other", "Other"), ("undisclosed", "Prefer not to say"),
    ]
    name = models.CharField(max_length=150)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=16, blank=True, validators=[phone_validator])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patients")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=16, blank=True, validators=[phone_validator])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="doctors")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"


class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="doctor_mappings")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="patient_mappings")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["patient", "doctor"], name="unique_patient_doctor")]

    def __str__(self):
        return f"{self.patient_id} -> {self.doctor_id}"
