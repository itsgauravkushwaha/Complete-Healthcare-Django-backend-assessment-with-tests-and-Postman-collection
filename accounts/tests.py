from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_stores_hashed_password_and_login_returns_jwt(self):
        registration = self.client.post("/api/auth/register/", {
            "name": "Gaurav", "email": "TEST@EXAMPLE.COM", "password": "StrongPass!2026"
        }, format="json")
        self.assertEqual(registration.status_code, 201)
        self.assertNotIn("password", registration.data)
        user = User.objects.get(email="test@example.com")
        self.assertTrue(user.check_password("StrongPass!2026"))

        login = self.client.post("/api/auth/login/", {
            "email": "Test@Example.com", "password": "StrongPass!2026"
        }, format="json")
        self.assertEqual(login.status_code, 200)
        self.assertIn("access", login.data)
        self.assertIn("refresh", login.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        self.assertEqual(self.client.get("/api/patients/").status_code, 200)

    def test_duplicate_email_and_weak_password_rejected(self):
        self.client.post("/api/auth/register/", {
            "name": "First", "email": "first@example.com", "password": "StrongPass!2026"
        }, format="json")
        duplicate = self.client.post("/api/auth/register/", {
            "name": "Second", "email": "FIRST@example.com", "password": "StrongPass!2026"
        }, format="json")
        weak = self.client.post("/api/auth/register/", {
            "name": "Third", "email": "third@example.com", "password": "123"
        }, format="json")
        self.assertEqual(duplicate.status_code, 400)
        self.assertEqual(weak.status_code, 400)

    def test_wrong_password_cannot_log_in(self):
        User.objects.create_user("first@example.com", "first@example.com", "StrongPass!2026")
        response = self.client.post("/api/auth/login/", {
            "email": "first@example.com", "password": "wrong-password"
        }, format="json")
        self.assertEqual(response.status_code, 401)
