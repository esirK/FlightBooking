from rest_framework import serializers
from .models import Flight, Reservation
from authentication.serializers import UserSerializer


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ('name', 'origin', 'destination', 'date_of_travel', 'capacity', 'status')


class ReservationSerializer(serializers.ModelSerializer):
    passenger = UserSerializer(read_only=True)
    flight = FlightSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ('id', 'origin', 'destination', 'date_of_travel', 'status', 'passenger', 'flight')
