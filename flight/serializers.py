from rest_framework import serializers
from .models import Flight


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ['name', 'origin', 'destination', 'date_of_travel', 'capacity', 'status']
