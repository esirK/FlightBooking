from django.test import TestCase

from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

User = get_user_model()
client = APIClient()


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.data = {
            "first_name": "Isaiah",
            "last_name": "Ngaruiya",
            "username": "esir",
            "email": "esir@gmail.com",
            "password": "Nice19407#",
        }

        cls.user = {
            "first_name": "Miriam",
            "last_name": "Wanjiku",
            "username": "Shiko",
            "email": "shiko@gmail.com",
            "password": "Nice19407#",
        }

        # URLS
        cls.registration_url = reverse('authentication:register')
        cls.login_url = reverse('authentication:login')
        cls.user_passport_url = reverse('authentication:passport')
