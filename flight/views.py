from rest_framework import generics

from flight.permissions import IsGetOrIsAdmin
from .models import Flight
from .serializers import FlightSerializer


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
    permission_classes = (IsGetOrIsAdmin, )
