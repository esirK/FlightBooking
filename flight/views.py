import os

from django.http import JsonResponse
from django.urls import reverse
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import F

from flight.permissions import IsGetOrIsAdmin, IsAdminOrIsOwner
from .models import Flight, Reservation, Ticket
from .serializers import FlightSerializer, ReservationSerializer, TicketSerializer
from django.core.mail import send_mail
from rest_framework.decorators import api_view

import threading
import paypalrestsdk


def custom404(request, *args, **kwargs):
    return JsonResponse({
        'status_code': 404,
        'error': 'Not found'
    }, status=status.HTTP_404_NOT_FOUND)


class FlightAPIView(generics.ListCreateAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsGetOrIsAdmin,)


class FlightDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows users to
        -> view single flight,
        -> update it(Admins only)
        -> Delete a flight(Admins Only)
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsGetOrIsAdmin,)


class ReserveFlightAPIView(generics.ListCreateAPIView):
    """
    Allows a user to create and view flight reservation.
    Admins can see all reservations related for this flight.
    """
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        flight_id = self.kwargs.get('pk')
        user = self.request.user
        reservations = Reservation.objects.all()

        return [reservation for reservation in reservations
                if (reservation.passenger == user or user.is_staff) and reservation.flight.id == flight_id]

    def perform_create(self, serializer):
        user = self.request.user
        flight = get_object_or_404(Flight, pk=self.kwargs.get('pk'))

        # Ensure the user doesn't make more than one reservation on one flight.
        reservations = flight.flight_reservations.all()
        passengers = [passenger for passenger in reservations.filter(passenger_id=user.id)]

        if passengers:
            raise Exception({"message": "Passengers are allowed to only make one reservation per flight."})

        if flight.reservations_available < 1:
            raise Exception({"message": "No flight reservations slot available at the moment."
                                        " Please try again latter."})

        # Using F will prevent race condition.
        flight.reservations_available = F('reservations_available') - 1
        flight.save()
        flight.refresh_from_db()
        return serializer.save(passenger_id=user.id, flight=flight)


class AllReservationsAPIView(generics.ListAPIView):
    """
    Allows a user to view all their flights reservations.
    """
    serializer_class = ReservationSerializer
    permission_classes = (IsAdminOrIsOwner,)

    def get_queryset(self):
        user = self.request.user
        reservations = Reservation.objects.all()

        return [reservation for reservation in reservations
                if (reservation.passenger == user or user.is_staff)]


class SingleReservationAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows users to cancel their flight reservations.
    Once a ticket has been bought, this actions can not be performed.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAdminOrIsOwner,)

    def has_ticket(self):
        tickets = self.get_object().tickets.all()
        ticket = [t for t in tickets if t.status == 'paid']
        if ticket:
            """
            Booking has been done and paid therefore we cannot allow user to edit
            the reservation info.
            """
            return True, {"message": "Can not update a flight reservation that has a paid booking"}

        return False,

    def patch(self, request, *args, **kwargs):
        has_ticket = self.has_ticket()

        if has_ticket[0]:
            return Response(
                has_ticket[1],
                status=status.HTTP_200_OK)
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        has_ticket = self.has_ticket()

        if has_ticket[0]:
            return Response(
                has_ticket[1],
                status=status.HTTP_200_OK)
        return self.update(request, *args, **kwargs)


class BookTicketsAPIView(generics.CreateAPIView):
    """
    Allows users to book tickets for their reservations.
    """
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """
        Ensure that the user who want to book this flight has a reservation.
        If not, automatically create a reservation for Him/Her.
        """
        user = self.request.user
        all_reservations = Reservation.objects.filter(passenger_id=user.id)
        flight = get_object_or_404(Flight, pk=self.kwargs.get('pk'))

        user_reservations = [reservation for reservation in all_reservations if reservation.flight.id == flight.id]

        if not user_reservations:
            # Create a reservation for this user.
            if flight.reservations_available < 1:
                raise Exception({"message": "No flight reservations slot available at the moment."
                                            " You cannot be able to book a ticket without a reservation."})

            # Using F will prevent race condition.
            flight.reservations_available = F('reservations_available') - 1
            flight.save()
            flight.refresh_from_db()

            reservation = Reservation.objects.create(passenger=user, flight=flight)
        else:
            reservation = user_reservations[0]
            # Explicitly set the reservation status to active just incase the user had
            # Canceled it earlier
            reservation.status = 'active'
            reservation.save()
        # Email the user their ticket information.
        self.email_user(flight)

        return serializer.save(reservation=reservation)

    def email_user(self, flight):
        subject = f'Ticket for flight {flight.name}.'
        message = f"""
                          Thank you for choosing to fly with us.
                          Here are the details for your ticket.
                          ORIGIN: {flight.origin}
                          DESTINATION: {flight.destination}
                          DATE_OF_FLIGHT: {flight.date_of_travel}
                          TICKET_PRICE: {flight.cost}
                          TICKET_STATUS: "Not Paid"
                          """
        recipient_list = [self.request.user.email]

        # Start a new thread to Send an Email to the User in the background.
        sender = settings.EMAIL_HOST_USER
        thread = threading.Thread(target=send_mail, args=(subject, message, sender, recipient_list))
        thread.start()


class TicketsAPIView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        tickets = Ticket.objects.all()

        return [ticket for ticket in tickets
                if ticket.reservation.passenger == user
                or user.is_staff]


class TicketDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        ticket = get_object_or_404(Ticket, {'pk': self.kwargs.get('pk')})
        if ticket.reservation.passenger == self.request.user:
            return ticket
        else:
            return None


class PayTicketAPIView(views.APIView):
    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=self.kwargs.get('pk'))
        if ticket.status == 'paid':
            return Response(data={
                'message': 'payment for this ticket has already been made.',
            })

        paypalrestsdk.configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": os.getenv('PAY_PAL_CLIENT_ID'),
            "client_secret": os.getenv('PAY_PAL_CLIENT_SECRET')})
        payment = paypalrestsdk.Payment(
            {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal",
                    "payer_info": {
                        "email": f"{self.request.user.email}"
                    }
                },
                "redirect_urls": {
                    "return_url": request.build_absolute_uri(reverse('flight:execute', kwargs={"ticket_pk": pk})),
                    "cancel_url": request.build_absolute_uri(reverse('flight:cancel'))},
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"Flight {ticket.reservation.flight.name} Ticket",
                            "sku": "service",
                            "price": f"{ticket.reservation.flight.cost}",
                            "currency": "USD",
                            "quantity": 1}]},
                    "amount": {
                        "total": f"{ticket.reservation.flight.cost}",
                        "currency": "USD"},
                    "description": "Payment for your ticket."}]
            }
        )
        if payment.create():
            print("Payment created successfully")
        else:
            print(payment.error)
            return Response(data={
                'error': f'{payment.error}',
            })

        for link in payment.links:
            if link.rel == "approval_url":
                # Convert to str to avoid Google App Engine Unicode issue
                # https://github.com/paypal/rest-api-sdk-python/pull/58
                approval_url = str(link.href)
                print("Redirect for approval: %s" % (approval_url))

                return Response(data={
                    'message': 'follow this link to approve the payment.',
                    'approval_url': approval_url
                })


@api_view(['GET'])
def execute(request, ticket_pk):
    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox or live
        "client_id": os.getenv('PAY_PAL_CLIENT_ID'),
        "client_secret": os.getenv('PAY_PAL_CLIENT_SECRET')})

    paymentId = request.GET['paymentId']
    payment = paypalrestsdk.Payment.find(paymentId)

    PayerID = request.GET['PayerID']

    if payment.execute({"payer_id": PayerID}):
        # Update the ticket status to paid.
        print("Payment execute successfully")
        ticket = Ticket.objects.get(id=ticket_pk)
        ticket.status = 'paid'
        ticket.save()

        ticket_data = TicketSerializer(ticket)

        return Response(data={
            'message': 'Payment successful',
            'ticket': ticket_data.data
        })

    else:
        print(payment.error)  # Error Hash
        return Response(data={
            'error': f'{payment.error}',
        })


@api_view(['GET'])
def cancel(request):
    return JsonResponse(data={
        'error': "Transaction was canceled by the user.",
    })
