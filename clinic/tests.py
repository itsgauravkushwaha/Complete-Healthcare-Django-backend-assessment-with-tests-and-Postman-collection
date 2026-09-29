from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Doctor, Patient, PatientDoctorMapping

User = get_user_model()


class ClinicTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            username="alice@example.com", email="alice@example.com", password="Secure!12345"
        )
        self.bob = User.objects.create_user(
            username="bob@example.com", email="bob@example.com", password="Secure!12345"
        )

    def test_protected_endpoints_require_jwt(self):
        for url in ("/api/patients/", "/api/doctors/", "/api/mappings/"):
            self.assertEqual(self.client.get(url).status_code, 401)

    def test_patient_crud_and_owner_isolation(self):
        self.client.force_authenticate(user=self.alice)
        invalid = self.client.post("/api/patients/", {"name": "A", "age": 121}, format="json")
        self.assertEqual(invalid.status_code, 400)
        created = self.client.post("/api/patients/", {
            "name": "Demo Patient", "age": 30, "gender": "female", "phone": "+919876543210"
        }, format="json")
        self.assertEqual(created.status_code, 201)
        patient_id = created.data["id"]
        self.assertEqual(created.data["name"], "Demo Patient")
        self.assertEqual(len(self.client.get("/api/patients/").data), 1)
        updated = self.client.put(f"/api/patients/{patient_id}/", {
            "name": "Demo Patient Updated", "age": 31, "gender": "female", "phone": ""
        }, format="json")
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["age"], 31)
        self.client.force_authenticate(user=self.bob)
        self.assertEqual(len(self.client.get("/api/patients/").data), 0)
        self.assertEqual(self.client.get(f"/api/patients/{patient_id}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/patients/{patient_id}/").status_code, 404)
        self.client.force_authenticate(user=self.alice)
        self.assertEqual(self.client.delete(f"/api/patients/{patient_id}/").status_code, 204)

    def test_doctors_readable_by_all_but_only_owner_can_modify(self):
        self.client.force_authenticate(user=self.alice)
        created = self.client.post("/api/doctors/", {
            "name": "Arun", "specialization": "Cardiology", "email": "arun@example.com"
        }, format="json")
        self.assertEqual(created.status_code, 201)
        doctor_id = created.data["id"]
        self.client.force_authenticate(user=self.bob)
        self.assertEqual(len(self.client.get("/api/doctors/").data), 1)
        self.assertEqual(self.client.get(f"/api/doctors/{doctor_id}/").status_code, 200)
        self.assertEqual(self.client.put(f"/api/doctors/{doctor_id}/", {
            "name": "Changed", "specialization": "Wrong"
        }, format="json").status_code, 403)
        self.assertEqual(self.client.delete(f"/api/doctors/{doctor_id}/").status_code, 403)

    def test_doctor_creator_can_update_and_delete(self):
        self.client.force_authenticate(user=self.alice)
        created = self.client.post("/api/doctors/", {
            "name": "Arun", "specialization": "Cardiology"
        }, format="json")
        self.assertEqual(created.status_code, 201)
        doctor_id = created.data["id"]
        updated = self.client.put(f"/api/doctors/{doctor_id}/", {
            "name": "Arun", "specialization": "Neurology"
        }, format="json")
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data["specialization"], "Neurology")
        self.assertEqual(self.client.delete(f"/api/doctors/{doctor_id}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/doctors/{doctor_id}/").status_code, 404)

    def test_mapping_create_list_patient_doctors_delete_and_duplicate(self):
        patient = Patient.objects.create(name="Demo Patient", age=45, created_by=self.alice)
        doctor = Doctor.objects.create(name="Arun", specialization="Cardiology", created_by=self.bob)
        self.client.force_authenticate(user=self.alice)
        first = self.client.post("/api/mappings/", {
            "patient": patient.id, "doctor": doctor.id
        }, format="json")
        self.assertEqual(first.status_code, 201)
        mapping_id = first.data["id"]
        self.assertEqual(self.client.post("/api/mappings/", {
            "patient": patient.id, "doctor": doctor.id
        }, format="json").status_code, 400)
        self.assertEqual(len(self.client.get("/api/mappings/").data), 1)
        assigned = self.client.get(f"/api/mappings/{patient.id}/")
        self.assertEqual(assigned.status_code, 200)
        self.assertEqual(assigned.data[0]["doctor"]["name"], "Arun")
        self.assertEqual(assigned.data[0]["mapping_id"], mapping_id)
        self.assertEqual(self.client.delete(f"/api/mappings/{mapping_id}/").status_code, 204)
        self.assertEqual(len(self.client.get("/api/mappings/").data), 0)

    def test_other_user_cannot_access_or_map_private_patient(self):
        patient = Patient.objects.create(name="Private", age=33, created_by=self.alice)
        doctor = Doctor.objects.create(name="Arun", specialization="Cardiology", created_by=self.alice)
        mapping = PatientDoctorMapping.objects.create(patient=patient, doctor=doctor)
        self.client.force_authenticate(user=self.bob)
        self.assertEqual(self.client.get("/api/mappings/").data, [])
        self.assertEqual(self.client.get(f"/api/mappings/{patient.id}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/mappings/{mapping.id}/").status_code, 404)
        self.assertEqual(self.client.post("/api/mappings/", {
            "patient": patient.id, "doctor": doctor.id
        }, format="json").status_code, 400)
