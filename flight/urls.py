from django.urls import path
from flight.views import FlightAPIView, FlightDetailsAPIView


app_name = "flight"


urlpatterns = [
    path('flights/', FlightAPIView.as_view(), name='flights'),
    path('flights/<int:pk>/', FlightDetailsAPIView.as_view(), name='flight-detail'),
]
