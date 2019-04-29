from datetime import datetime

from authentication.test import BaseTestCase
from flight.models import Flight, Reservation, Ticket
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from django.core import mail

User = get_user_model()


class TestBookFlightTicket(BaseTestCase):
    def setUp(self):
        # Create some flights for testing
        self.flight = Flight.objects.create(
            name="QA3142",
            origin="DOHA",
            destination="NAIROBI",
            date_of_travel=datetime(2019, 4, 20, 17, 10, 9),
            capacity=150,
            reservations_available=150,
            cost=500
        )
        self.book_flight_url = reverse('flight:book-ticket', kwargs={'pk': self.flight.id})

    def test_non_logged_in_users_cannot_book_flight_tickets(self):
        response = self.perform_request('post', self.book_flight_url)
        self.assertEqual(403, response.status_code)

    def test_logged_in_users_can_book_flight_tickets(self):
        token = self.login_normal_user()
        self.assertEqual(0, Ticket.objects.count())
        response = self.perform_request('post', self.book_flight_url, token=token)

        self.assertEqual(201, response.status_code)
        self.assertEqual(1, Ticket.objects.count())

    def test_email_is_sent_on_ticket_booking(self):
        token = self.login_normal_user()
        self.perform_request('post', self.book_flight_url, token=token)
        import time
        time.sleep(0.5)
        # Test that one message has been sent.
        self.assertEqual(1, len(mail.outbox))
        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, f'Ticket for flight {self.flight.name}.')

    def test_logged_in_users_can_see_their_tickets(self):
        url = reverse('flight:tickets', kwargs={'pk': self.flight.id})
        token = self.login_normal_user()
        response = self.perform_request('get', url, token=token)
        self.assertEqual(0, len(response.json()))

        self.perform_request('post', self.book_flight_url, token=token)
        response = self.perform_request('get', url, token=token)
        self.assertEqual(1, len(response.json()))
