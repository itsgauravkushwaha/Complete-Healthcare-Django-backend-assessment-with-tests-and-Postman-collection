from rest_framework import serializers
from .models import Doctor, Patient, PatientDoctorMapping


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "age", "gender", "phone", "created_at"]
        read_only_fields = ["id", "created_at"]


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id", "name", "specialization", "email", "phone", "created_at"]
        read_only_fields = ["id", "created_at"]


class MappingSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "patient", "doctor", "doctor_name", "assigned_at"]
        read_only_fields = ["id", "doctor_name", "assigned_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # An unknown ID and another user's patient both produce the same 400.
        # That avoids revealing whether somebody else's patient exists.
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            self.fields["patient"].queryset = Patient.objects.filter(created_by=request.user)

    def validate_patient(self, patient):
        # Defense in depth: never map somebody else's patient.
        if patient.created_by_id != self.context["request"].user.id:
            raise serializers.ValidationError("Patient not found or not owned by you.")
        return patient

    def validate(self, attrs):
        if PatientDoctorMapping.objects.filter(patient=attrs["patient"], doctor=attrs["doctor"]).exists():
            raise serializers.ValidationError("This doctor is already assigned to the patient.")
        return attrs
