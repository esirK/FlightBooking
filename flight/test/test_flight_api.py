from authentication.test import BaseTestCase
from flight.models import Flight
from datetime import datetime
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestFlightAPI(BaseTestCase):
    def setUp(self):
        # Create some flights for testing
        self.flight = Flight.objects.create(
            name="QA3142",
            origin="DOHA",
            destination="NAIROBI",
            date_of_travel=datetime(2019, 4, 20, 17, 10, 9),
            capacity=150,
            reservations_available=150
        )
        self.flight_data = {
            "name": "ZR1341",
            "origin": "DOHA",
            "destination": "NAIROBI",
            "date_of_travel": "2019-03-31T02:00:30Z",
            "capacity": 170,
            "reservations_available": 170
        }

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
        response = self.perform_request('post', self.flights_url, token=token, data=self.flight_data)

        self.assertEqual(403, response.status_code)
        self.assertEqual('You do not have permission to perform this action.',
                         response.json().get('detail'))

    def test_admin_can_create_new_flights(self):
        token = self.login_admin()
        response = self.perform_request('post', self.flights_url, token=token, data=self.flight_data)

        flights = self.client.get(self.flights_url)

        self.assertEqual(201, response.status_code)
        self.assertEqual(2, len(flights.json()))

    def test_admin_can_update_flights(self):
        token = self.login_admin()

        # Update the flight capacity
        data = {"capacity": 200}

        url = reverse('flight:flight-detail', kwargs={'pk': self.flight.id})
        response = self.perform_request('patch', url, token=token, data=data)

        flight = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(200, flight.json().get('capacity'))

    def test_non_admin_cannot_update_flights(self):
        token = self.login_normal_user()
        # Update the flight capacity
        data = {"capacity": 200}
        url = reverse('flight:flight-detail', kwargs={'pk': self.flight.id})
        response = self.perform_request('patch', url, token=token, data=data)

        self.assertEqual(403, response.status_code)
        self.assertEqual("You do not have permission to perform this action.",
                         response.json().get('detail'))

    def test_admin_can_delete_a_flight(self):
        flights_count = Flight.objects.count()

        token = self.login_admin()
        url = reverse('flight:flight-detail', kwargs={'pk': self.flight.id})
        response = self.perform_request('delete', url, token=token)

        new_flights_count = Flight.objects.count()

        self.assertEqual(204, response.status_code)
        self.assertEqual(new_flights_count, flights_count-1)

    def test_non_admin_cannot_delete_a_flight(self):
        flights_count = Flight.objects.count()

        token = self.login_normal_user()
        url = reverse('flight:flight-detail', kwargs={'pk': self.flight.id})
        response = self.perform_request('delete', url, token=token)

        new_flights_count = Flight.objects.count()

        self.assertEqual(403, response.status_code)
        self.assertEqual(new_flights_count, flights_count)
