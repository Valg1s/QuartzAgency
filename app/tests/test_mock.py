import time
from unittest import mock
from django.test import TestCase, Client
from django.urls import reverse
from app.models import ProfileType, CustomUser


class MockPerformanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('app:register')
        self.register_data_url = reverse('app:data_form')
        self.login_url = reverse('app:login')

        self.initial_data = {
            'email': 'mock@test.com',
            'contact': '12345678',
            'password': 'MockPass123!',
            'confirm_password': 'MockPass123!',
            'profile_type': ProfileType.EMPLOYEE,
        }

        self.additional_data = {
            'first_name': 'Mocky',
            'last_name': 'McTest',
            'country': 'Testland',
        }

    def _test_1_register_real_db(self):
        """Regular registration test using the real database."""
        start = time.time()

        self.client.post(self.register_url, self.initial_data)
        response = self.client.post(self.register_data_url, self.additional_data)

        duration = time.time() - start
        self.assertEqual(response.status_code, 302)

        print(f"\n🔵 [REAL DB] Duration: {duration:.4f} seconds")
        return duration

    def _test_2_register_mocked_db(self):
        mock_user = mock.Mock(spec=CustomUser)

        with mock.patch('app.views.CustomUser.objects.create_user', return_value=mock_user) as mocked_create:
            start = time.time()

            session = self.client.session
            session['register_data'] = {
                'email': 'mock@example.com',
                'contact': '1234567890',
                'password': 'securepassword',
                'profile_type': ProfileType.EMPLOYEE,
            }
            session.save()

            response = self.client.post(self.register_data_url, self.additional_data)
            self.assertEqual(response.status_code, 302)

            duration = time.time() - start
            mocked_create.assert_called_once()

        print(f"\n🟢 [MOCKED DB] Duration: {duration:.4f} seconds")
        return duration

    def test_3_comparison(self):
        """Performance comparison between real and mocked registration."""
        real_duration = self._test_1_register_real_db()
        mocked_duration = self._test_2_register_mocked_db()

        diff = real_duration - mocked_duration
        print(f"\n📊 Comparison: Real DB is slower by {diff:.4f} seconds")
