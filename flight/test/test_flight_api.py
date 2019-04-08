from authentication.test import BaseTestCase
from flight.models import Flight
from datetime import datetime
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class TestFlightAPI(BaseTestCase):
    def setUp(self):
        # Create some flights for testing
        self.flight = Flight.objects.create(
            name="QA3142",
            origin="DOHA",
            destination="NAIROBI",
            date_of_travel=datetime(2019, 4, 20, 17, 10, 9),
            capacity=150
        )
        self.flight_data = {
            "name": "ZR1341",
            "origin": "DOHA",
            "destination": "NAIROBI",
            "date_of_travel": "2019-03-31T02:00:30Z",
            "capacity": 170
        }

        # Create an admin User
        self.admin = User.objects.create_superuser(
            username="Admin",
            email="admin@admin.com",
            password="Nice19407#"
        )

    def login_admin(self):
        "Logs in admin and returns a token"
        admin_login = self.client.post(self.login_url,
                                       data={
                                           "email": "admin@admin.com",
                                           "password": "Nice19407#"
                                       })

        token = admin_login.json().get('token')
        return token

    def login_normal_user(self):
        "Registers and Logs in a normal user and returns a token"
        self.client.post(self.registration_url,
                         data=self.user)
        user_login = self.client.post(self.login_url,
                                      data={
                                          "email": "shiko@gmail.com",
                                          "password": "Nice19407#"}
                                      )
        token = user_login.json().get('token')
        return token

    def test_any_user_can_view_all_flight(self):
        """
        Test that any user
        (Including un authenticated users can view flights)
        """

        response = self.client.get(self.flights_url)
        self.assertEqual(1, len(response.json()))
        self.assertEqual(200, response.status_code)

    def test_any_user_can_view_a_single_flight(self):
        """
        Test that any user
        (Including un authenticated users can view a flight)
        """
        url = reverse('flight:flight-detail', kwargs={'pk': self.flight.id})

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_non_admin_can_not_create_new_flights(self):
        token = self.login_normal_user()
        response = self.client.post(self.flights_url, data=self.flight_data,
                                    format='json',
                                    HTTP_AUTHORIZATION=f"Token {token}")

        self.assertEqual(403, response.status_code)
        self.assertEqual('You do not have permission to perform this action.',
                         response.json().get('detail'))

    def test_admin_can_create_new_flights(self):
        token = self.login_admin()
        response = self.client.post(self.flights_url, data=self.flight_data,
                                    format='json',
                                    HTTP_AUTHORIZATION=f"Token {token}")
        flights = self.client.get(self.flights_url)

        self.assertEqual(201, response.status_code)
        self.assertEqual(2, len(flights.json()))

    def test_admin_can_update_flights(self):
        token = self.login_admin()

        # Update the flight capacity
        data = {"capacity": 200}

        url = reverse('flight:flight-detail', kwargs={'pk': self.flight.id})
        response = self.client.patch(url, data=data,
                                     content_type='application/json',
                                     HTTP_AUTHORIZATION=f"Token {token}")

        flight = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(200, flight.json().get('capacity'))

    def test_non_admin_cannot_update_flights(self):
        token = self.login_normal_user()
        # Update the flight capacity
        data = {"capacity": 200}
        url = reverse('flight:flight-detail', kwargs={'pk': self.flight.id})
        response = self.client.patch(url, data=data,
                                     content_type='application/json',
                                     HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(403, response.status_code)
        self.assertEqual("You do not have permission to perform this action.",
                         response.json().get('detail'))

    def test_admin_can_delete_a_flight(self):
        flights_count = Flight.objects.count()

        token = self.login_admin()
        url = reverse('flight:flight-detail', kwargs={'pk': self.flight.id})
        response = self.client.delete(url, HTTP_AUTHORIZATION=f"Token {token}")
        new_flights_count = Flight.objects.count()

        self.assertEqual(204, response.status_code)
        self.assertEqual(new_flights_count, flights_count-1)

    def test_non_admin_cannot_delete_a_flight(self):
        flights_count = Flight.objects.count()

        token = self.login_normal_user()
        url = reverse('flight:flight-detail', kwargs={'pk': self.flight.id})
        response = self.client.delete(url, HTTP_AUTHORIZATION=f"Token {token}")
        new_flights_count = Flight.objects.count()

        self.assertEqual(403, response.status_code)
        self.assertEqual(new_flights_count, flights_count)
