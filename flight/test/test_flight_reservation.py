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
            capacity=150,
            reservations_available=150
        )
        self.reservation_url = reverse('flight:reservations', kwargs={'pk':self.flight.id})

    def test_non_logged_in_user_cant_create_a_reservation(self):
        """
        Tests to Ensure that only logged in users can create a flight reservation
        """
        response = self.perform_request('post', url=self.reservation_url)
        self.assertEqual(403, response.status_code)
        self.assertIn('detail', response.json())

    def test_logged_in_users_can_create_reservations(self):
        token = self.login_normal_user()
        # Ensure that we don't have any reservation currently
        self.assertEqual(0, Reservation.objects.count())

        response = self.perform_request('post', url=self.reservation_url, token=token)
        self.assertEqual(201, response.status_code)

        # Check to see that a reservation has been created.
        self.assertEqual(1, Reservation.objects.count())

    def test_available_reservations_are_update_every_time_reservation_is_made(self):
        """
        Ensures that every time a reservation is made, the number of available reservations is reduced
        to ensure users don't reserve flights that are full already.
        """
        token = self.login_normal_user()

        old_count = self.flight.reservations_available

        self.perform_request('post', url=self.reservation_url, token=token)
        res = self.perform_request('get', url=self.reservation_url, token=token)
        new_count = res.json()[0].get('flight').get('reservations_available')
        self.assertEqual(new_count, old_count-1)

    def test_a_user_can_only_make_one_flight_reservation(self):
        token = self.login_normal_user()
        response = self.perform_request('post', url=self.reservation_url, token=token)
        self.assertEqual(201, response.status_code)

        # Use same reservation url thus same flight
        response = self.perform_request('post', url=self.reservation_url, token=token)
        self.assertEqual(400, response.status_code)


    def test_users_can_only_view_their_reservations(self):
        """
        Tests that only admins and the owners of a reservation can
        see it.
        """
        token = self.login_normal_user()
        self.perform_request('post', url=self.reservation_url, token=token)

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
        self.perform_request('post', self.reservation_url, token=token)

        res = self.perform_request('get', self.reservation_url, token=token)

        data = {'status': 'canceled'}

        url = reverse('flight:reservation-detail', kwargs={'pk': res.json()[0].get('id')})
        response = self.perform_request('patch', url=url, token=token, data=data)

        self.assertEqual(200, response.status_code)
        self.assertEqual('canceled', response.json().get('status'))

        # Ensure admins can edit a reservation
        admin_token = self.login_admin()

        response = self.perform_request('patch', url=url, token=admin_token, data={'status': 'late'})
        self.assertEqual(200, response.status_code)
        self.assertEqual('late', response.json().get('status'))

        # Ensure non admins/non owners can't edit a reservation
        token2 = self.login_user2()

        response = self.perform_request('patch', url=url, token=token2, data=data)
        self.assertEqual(403, response.status_code)
