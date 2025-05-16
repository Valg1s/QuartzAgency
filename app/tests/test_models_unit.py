from django.test import TestCase
from app.models import CustomUser, Order, ProfileType, TypeOfEmployment
from django.conf import settings

settings.DATABASES['default']['HOST'] = 'localhost'

class CustomUserModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="John",
            last_name="Doe",
            contact="1234567890",
            country="USA",
            profile_type=ProfileType.EMPLOYEE
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("password123"))
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.profile_type, ProfileType.EMPLOYEE)

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), "John Doe")


class OrderModelTest(TestCase):

    def setUp(self):
        self.company_user = CustomUser.objects.create_user(
            email="company@example.com",
            password="password123",
            first_name="Company",
            last_name="Owner",
            contact="0987654321",
            country="Germany",
            profile_type=ProfileType.COMPANY,
            company_name="TechCorp"
        )

    def test_create_order_valid(self):
        order = Order.create(
            owner=self.company_user,
            title="Django Developer Needed",
            description="We are looking for a Django dev",
            category="Software",
            type_of_employment=TypeOfEmployment.REMOTE,
            payload=1000.0
        )
        self.assertIsInstance(order, Order)
        self.assertEqual(order.owner, self.company_user)
        self.assertEqual(order.payload, 1000.0)

    def test_create_order_invalid_owner(self):
        employee_user = CustomUser.objects.create_user(
            email="employee@example.com",
            password="password123",
            first_name="Jane",
            last_name="Smith",
            contact="1112223333",
            country="USA",
            profile_type=ProfileType.EMPLOYEE
        )
        result = Order.create(
            owner=employee_user,
            title="Bad Order",
            description="This should fail",
            category="Marketing",
            type_of_employment=TypeOfEmployment.REMOTE,
            payload=500.0
        )
        self.assertIsInstance(result, Exception)
        self.assertEqual(str(result), "Order owner must be Company Profile")

    def test_create_order_invalid_employment_type(self):
        result = Order.create(
            owner=self.company_user,
            title="Invalid Employment Type",
            description="Invalid employment",
            category="Finance",
            type_of_employment="hybrid",
            payload=1500.0
        )
        self.assertIsInstance(result, Exception)
        self.assertIn("Type of Employment", str(result))

    def test_order_str(self):
        order = Order.create(
            owner=self.company_user,
            title="Fullstack Developer",
            description="Looking for a fullstack dev",
            category="Web",
            type_of_employment=TypeOfEmployment.OFFICE,
            payload=1200.0
        )
        self.assertEqual(str(order), f"{self.company_user} Fullstack Developer")

