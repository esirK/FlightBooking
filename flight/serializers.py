from rest_framework import serializers
from .models import Flight, Reservation
from authentication.serializers import UserSerializer


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ('id', 'name', 'origin', 'destination', 'date_of_travel', 'capacity',
                  'reservations_available', 'status')


class ReservationSerializer(serializers.ModelSerializer):
    passenger = UserSerializer(read_only=True)
    flight = FlightSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ('id', 'status', 'passenger', 'flight')
