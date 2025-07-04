from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ExpanseIncome


class AuthencationTets(APITestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password": "test123",
        }

        self.user = User.objects.create_user(**self.user_data)

    def test_user_registration(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "newtest@test.com",
                "password": "newtest123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        response = self.client.post(
            "/api/auth/login/", {"username": "testuser", "password": "test123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        
    def test_user_registration_with_existing_username(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "email": "newtest@test.com",
                "password": "newtest123",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_user_login_with_invalid_credentials(self):
        response = self.client.post(
            "/api/auth/login/", {"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_token_refresh(self):
        response = self.client.post(
            "/api/auth/login/", {"username": "testuser", "password": "test123"}
        )
        refresh_token = response.data["refresh"]
        response = self.client.post(
            "/api/auth/refresh/", {"refresh": refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        
    def test_access_protected_endpoint_with_valid_token(self):
        response = self.client.post(
            "/api/auth/login/", {"username": "testuser", "password": "test123"}
        )
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get("/api/expense/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_access_protected_endpoint_with_invalid_token(self):
        response = self.client.get("/api/expense/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CRUDTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        self.superuser = User.objects.create_superuser(
            username="admin", password="pass123"
        )

        self.expense1 = ExpanseIncome.objects.create(
            title="Expense 1",
            amount=100,
            user=self.user1,
            transaction_type="debit",
            tax_type="flat",
            tax=10,
        )
        
    def test_regular_user_can_only_access_own_records(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get("/api/expense/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        
    def test_superuser_can_access_all_records(self):
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get("/api/expense/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_create_expense(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/expense/",
            {
                "title": "Expense 2",
                "amount": 100,
                "user": self.user1.id,
                "transaction_type": "debit",
                "tax_type": "flat",
                "tax": 10,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
        
    def test_retrvie_specific_expense(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/expense/{self.expense1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_expense(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.put(
            f"/api/expense/{self.expense1.id}/",
            {
                "title": "Expense 2",
                "amount": 200,
                "user": self.user1.id,
                "transaction_type": "debit",
                "tax_type": "flat",
                "tax": 10,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_delete_expense(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f"/api/expense/{self.expense1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    
    
class BusinessLogicTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")


        self.expense1 = ExpanseIncome.objects.create(
            title="Expense 1",
            amount=100,
            user=self.user1,
            transaction_type="debit",
            tax_type="flat",
            tax=10,
        )
        
        
    def test_flat_tax(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/expense/",
            {
                "title": "Expense 2",
                "amount": 100,
                "user": self.user1.id,
                "transaction_type": "debit",
                "tax_type": "flat",
                "tax": 10,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertAlmostEqual(float(response.data['total']), 110, places=2)
        
    def test_percentage_test(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/expense/",
            {
                "title": "Expense 2",
                "amount": 100,
                "user": self.user1.id,
                "transaction_type": "debit",
                "tax_type": "percentage",
                "tax": 10,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertAlmostEqual(float(response.data['total']), 110, places=2)
        
    def test_zero_tax(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            "/api/expense/",
            {
                "title": "Expense 2",
                "amount": 100,
                "user": self.user1.id,
                "transaction_type": "debit",
                "tax_type": "zero",
                "tax": 10,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertAlmostEqual(float(response.data['total']), 100, places=2)
        
class PermissionTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass123")
        self.user2 = User.objects.create_user(username="user2", password="pass123")
        self.superuser = User.objects.create_superuser(
            username="admin", password="pass123"
        )

        self.expense1 = ExpanseIncome.objects.create(
            title="Expense 1",
            amount=100,
            user=self.user1,
            transaction_type="debit",
            tax_type="flat",
            tax=10,
        )
    def regular_user_cannot_access_other_user_records(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/expense/{self.expense1.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        
        
        
        
        
        
        
        
    
        
        
        
      
