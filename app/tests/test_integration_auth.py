from django.test import TestCase, Client
from django.urls import reverse
from app.models import CustomUser, ProfileType

class AuthIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('app:register')
        self.register_data_url = reverse('app:data_form')
        self.login_url = reverse('app:login')
        self.logout_url = reverse('app:logout')
        self.main_url = reverse('app:main')
        self.session_status_url = reverse('app:session-status')

    def test_1_register_company_user_full_flow(self):
        # Step 1: Submit main registration form
        step1_response = self.client.post(self.register_url, {
            'email': 'company@test.com',
            'contact': '12345678',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
            'profile_type': ProfileType.COMPANY,
        })
        self.assertEqual(step1_response.status_code, 302)
        self.assertRedirects(step1_response, self.register_data_url)

        # Step 2: Submit additional data
        step2_response = self.client.post(self.register_data_url, {
            'first_name': 'Test',
            'last_name': 'Company',
            'country': 'USA',
            'company_name': 'TestCorp'
        })
        self.assertEqual(step2_response.status_code, 302)
        self.assertRedirects(step2_response, self.login_url)

        # User should exist now
        user = CustomUser.objects.get(email='company@test.com')
        self.assertEqual(user.profile_type, ProfileType.COMPANY)

    def test_2_login_after_registration(self):
        user = CustomUser.objects.create_user(
            email='logintest@test.com',
            contact='111111',
            password='MySecret123!',
            profile_type=ProfileType.EMPLOYEE,
            first_name='Test',
            last_name='User',
            country='UA'
        )

        response = self.client.post(self.login_url, {
            'username': 'logintest@test.com',
            'password': 'MySecret123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.main_url)

    def test_3_session_status_authenticated(self):
        user = CustomUser.objects.create_user(
            email='session@test.com',
            contact='999999',
            password='SessionPass123!',
            profile_type=ProfileType.EMPLOYEE,
            first_name='Session',
            last_name='Check',
            country='PL'
        )
        self.client.login(email='session@test.com', password='SessionPass123!')

        res = self.client.get(self.session_status_url)
        self.assertEqual(res.status_code, 200)
        self.assertJSONEqual(res.content, {'status': 'ok'})

    def test_4_logout_user(self):
        user = CustomUser.objects.create_user(
            email='logout@test.com',
            contact='888888',
            password='LogoutPass123!',
            profile_type=ProfileType.EMPLOYEE,
            first_name='Logout',
            last_name='Test',
            country='DE'
        )
        self.client.login(email='logout@test.com', password='LogoutPass123!')

        res = self.client.post(self.logout_url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, self.login_url)

        # After logout, session status should be unauthorized
        res = self.client.get(self.session_status_url)
        self.assertEqual(res.status_code, 401)

    def test_5_invalid_login_rejected(self):
        user = CustomUser.objects.create_user(
            email='wrong@test.com',
            contact='777777',
            password='CorrectPassword123!',
            profile_type=ProfileType.EMPLOYEE,
            first_name='Wrong',
            last_name='Try',
            country='CZ'
        )

        res = self.client.post(self.login_url, {
            'username': 'wrong@test.com',
            'password': 'WrongPassword'
        })
        self.assertEqual(res.status_code, 403)
        self.assertIn(b'failed to login', res.content)
