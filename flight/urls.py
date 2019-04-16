from django.urls import path
from flight.views import FlightAPIView, FlightDetailsAPIView,\
    ReserveFlightAPIView, FlightReservationAPIView


app_name = "flight"


urlpatterns = [
    path('flights/', FlightAPIView.as_view(), name='flights'),
    path('flights/<int:pk>/', FlightDetailsAPIView.as_view(), name='flight-detail'),
    path('reservations/', ReserveFlightAPIView.as_view(), name='reservation'),
    path('reservations/<int:pk>/', FlightReservationAPIView.as_view(), name='reservation-detail'),
]
