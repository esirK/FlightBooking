from datetime import datetime

from authentication.test import BaseTestCase
from flight.models import Flight, Reservation
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

User = get_user_model()


class TestFlightReservation(BaseTestCase):
    def setUp(self):
        # Create some flights for testing
        self.flight = Flight.objects.create(
            name="QA3142",
            origin="DOHA",
            destination="NAIROBI",
            date_of_travel=datetime(2019, 4, 20, 17, 10, 9),
            capacity=150
        )
        self.reservation = {
            "origin": "DOHA",
            "destination": "BOSTON",
            "date_of_travel": "2019-4-20",
        }

    def test_non_logged_in_user_cant_create_a_reservation(self):
        """
        Tests to Ensure that only logged in users can create a flight reservation
        """
        response = self.perform_request('post', url=self.reservation_url, data=self.reservation)
        self.assertEqual(403, response.status_code)
        self.assertIn('detail', response.json())

    def test_logged_in_users_can_create_reservations(self):
        token = self.login_normal_user()
        # Ensure that we don't have any reservation currently
        self.assertEqual(0, Reservation.objects.count())

        response = self.perform_request('post', url=self.reservation_url, token=token, data=self.reservation)
        self.assertEqual(201, response.status_code)

        # Check to see that a reservation has been created.
        self.assertEqual(1, Reservation.objects.count())

    def test_users_can_only_view_their_reservations(self):
        """
        Tests that only admins and the owners of a reservation can
        see it.
        """
        token = self.login_normal_user()
        self.perform_request('post', url=self.reservation_url, token=token, data=self.reservation)

        # Ensure the owner can access their reservations
        res = self.perform_request('get', url=self.reservation_url, token=token)

        self.assertEqual(1, len(res.json()))

        token2 = self.login_user2()
        response = self.perform_request('get', url=self.reservation_url, token=token2)

        # Ensure non owners can't access the reservations
        self.assertEqual(0, len(response.json()))

        # Ensure admins can access the reservations
        admin_token = self.login_admin()
        response = self.perform_request('get', url=self.reservation_url, token=admin_token)

        self.assertEqual(1, len(response.json()))

    def test_only_admins_and_reservation_owners_can_edit_a_reservation(self):
        token = self.login_normal_user()
        self.perform_request('post', self.reservation_url, token=token, data=self.reservation)

        res = self.perform_request('get', self.reservation_url, token=token)

        data = {'origin': 'Nairobi'}

        url = reverse('flight:reservation-detail', kwargs={'pk': res.json()[0].get('id')})
        response = self.perform_request('patch', url=url, token=token, data=data)

        self.assertEqual(200, response.status_code)
        self.assertEqual('Nairobi', response.json().get('origin'))

        data['destination'] = 'DOHA'

        # Ensure admins can edit a reservation
        admin_token = self.login_admin()

        response = self.perform_request('patch', url=url, token=admin_token, data=data)
        self.assertEqual(200, response.status_code)
        self.assertEqual('DOHA', response.json().get('destination'))

        # Ensure non admins/non owners can't edit a reservation
        token2 = self.login_user2()

        response = self.perform_request('patch', url=url, token=token2, data=data)
        self.assertEqual(403, response.status_code)
