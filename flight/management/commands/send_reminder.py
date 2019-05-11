"""
This management command will check passengers with paid flights and send them email reminders about
 their flight 24hours before the flight.
"""
from datetime import datetime, timezone
from django.conf import settings
import threading
from django.core.mail import send_mail

from django.core.management import BaseCommand

from flight.models import Ticket


class Command(BaseCommand):

    def handle(self, *args, **options):

        emails_and_flights = self.get_passengers_with_tickets()
        print(emails_and_flights)

        for email_and_flight in emails_and_flights:
            email = email_and_flight[0]
            flight = email_and_flight[1]

            subject = f'Reminder of your flight {flight.name}'
            message = f"""
                        This is a reminder about your flight from\n
                        {flight.origin}\n To {flight.destination}
                        which is scheduled on {flight.date_of_travel}.
                        Thank you for choosing to fly with us.
                        """

            # Start a new thread to Send an Email to the User in the background.
            sender = settings.EMAIL_HOST_USER
            thread = threading.Thread(target=send_mail, args=(subject, message, sender, [email]))
            thread.start()

    def get_passengers_with_tickets(self):
        """
        :return: list of email addresses of the passengers with paid tickets and flight is in the next 24 hours.
        """
        tickets = Ticket.objects.filter(status='paid')
        current_time = datetime.now(timezone.utc)
        emails_and_flights = []
        for ticket in tickets:
            time_difference = (ticket.reservation.flight.date_of_travel - current_time)
            if time_difference.days == 0 and time_difference.seconds // 3600 == 23:
                emails_and_flights.append((ticket.reservation.passenger.email, ticket.reservation.flight))
        return emails_and_flights
