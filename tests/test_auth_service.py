import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuthService(unittest.TestCase):

    def test_register_user(self):
        # Test successful registration
        response = client.post("/auth/register", json={
            "username": "test_user",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("User registered successfully", response.json()["message"])

        # Test duplicate registration
        response = client.post("/auth/register", json={
            "username": "test_user",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("User already exists", response.json()["detail"])

    def test_login_user(self):
        # Register a user first
        client.post("/auth/register", json={
            "username": "login_user",
            "password": "securepassword"
        })

        # Test successful login
        response = client.post("/auth/login", json={
            "username": "login_user",
            "password": "securepassword"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Login successful", response.json()["message"])

        # Test invalid login
        response = client.post("/auth/login", json={
            "username": "login_user",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid credentials", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()