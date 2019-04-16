from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from flight.permissions import IsGetOrIsAdmin, IsAdminOrIsOwner
from .models import Flight, Reservation
from .serializers import FlightSerializer, ReservationSerializer


class FlightAPIView(generics.ListCreateAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsGetOrIsAdmin,)


class FlightDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows users to
        -> view single flight,
        -> update it(for admins only)
        -> Delete a flight(Admins Only)
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsGetOrIsAdmin,)


class ReserveFlightAPIView(generics.ListCreateAPIView):
    """
    Allows a user to create a flight reservation.
    """
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        reservations = Reservation.objects.all()

        return [flight for flight in reservations if flight.passenger == user or user.is_staff]

    def perform_create(self, serializer):
        user = self.request.user
        return serializer.save(passenger_id=user.id)


class FlightReservationAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows users to edit their flight reservations. e.g cancel, change origin or destination,
    Once a booking has been done, this actions can not be performed.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsAdminOrIsOwner,)

    def has_booking(self):
        if self.get_object().flight:
            """
            Booking has been done therefore we cannot allow user to edit 
            the reservation info.
            """
            return True, {"message": "Can not update a flight reservation with a booking"}

        return False,

    def patch(self, request, *args, **kwargs):
        has_booking = self.has_booking()

        if has_booking[0]:
            return Response(
                has_booking[1],
                status=status.HTTP_200_OK)
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        has_booking = self.has_booking()

        if has_booking[0]:
            return Response(
                has_booking[1],
                status=status.HTTP_200_OK)
        return self.update(request, *args, **kwargs)
