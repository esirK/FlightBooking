from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from flight.permissions import IsGetOrIsAdmin, IsAdminOrIsOwner
from .models import Flight, Reservation
from .serializers import FlightSerializer, ReservationSerializer


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
    Admins can see all reservations related to this flight.
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

        flight.reservations_available = flight.reservations_available - 1
        flight.save()
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
        return False,
        # if self.get_object().ticket:
        #     """
        #     Booking has been done therefore we cannot allow user to edit
        #     the reservation info.
        #     """
        #     return True, {"message": "Can not update a flight reservation that has a booking"}
        #
        # return False,

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
