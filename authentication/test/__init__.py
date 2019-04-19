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
        # Create an admin User
        cls.admin = User.objects.create_superuser(
            username="Admin",
            email="admin@admin.com",
            password="Nice19407#"
        )
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
        cls.user2 = {
            "first_name": "Isaiah",
            "last_name": "Kingori",
            "username": "Esir",
            "email": "esir@gmail.com",
            "password": "Nice19407#",
        }

        # URLS
        cls.registration_url = reverse('authentication:register')
        cls.login_url = reverse('authentication:login')
        cls.user_passport_url = reverse('authentication:passport')
        cls.flights_url = reverse('flight:flights')

    def login_admin(cls):
        """Logs in admin and returns a token"""
        admin_login = cls.client.post(cls.login_url,
                                      data={
                                          "email": "admin@admin.com",
                                          "password": "Nice19407#"
                                      })

        token = admin_login.json().get('token')
        return token

    def login_normal_user(cls):
        """Registers and Logs in a normal user and returns a token"""
        cls.client.post(cls.registration_url,
                        data=cls.user)
        user_login = cls.client.post(cls.login_url,
                                     data={
                                         "email": "shiko@gmail.com",
                                         "password": "Nice19407#"}
                                     )
        token = user_login.json().get('token')
        return token

    def login_user2(cls):
        """Registers and Logs in a normal user and returns a token"""
        cls.client.post(cls.registration_url,
                        data=cls.user2)
        user_login = cls.client.post(cls.login_url,
                                     data={
                                         "email": "esir@gmail.com",
                                         "password": "Nice19407#"}
                                     )
        token = user_login.json().get('token')
        return token

    def perform_request(cls, method, url, token=None, data=None):
        """
        :param method: Method to execute ['GET', 'POST', 'PUT', etc]
        :param url: URL to send the request
        :param token: token to be used for authentication if required.
        :param data: data to send to the server
        :return: response form the server
        """
        if token:
            HTTP_AUTHORIZATION = f"Token {token}"
            result = getattr(cls.client, method)(url,
                                                 data=data,
                                                 content_type='application/json',
                                                 HTTP_AUTHORIZATION=HTTP_AUTHORIZATION
                                                 )
        else:
            result = getattr(cls.client, method)(url,
                                                 data=data,
                                                 content_type='application/json',
                                                 )
        return result
