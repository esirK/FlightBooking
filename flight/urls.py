from django.urls import path
from flight.views import FlightAPIView, FlightDetailsAPIView,\
    ReserveFlightAPIView, SingleReservationAPIView, AllReservationsAPIView, \
    TicketsAPIView, BookTicketsAPIView


app_name = "flight"


urlpatterns = [
    path('flights/', FlightAPIView.as_view(), name='flights'),
    path('flights/<int:pk>/', FlightDetailsAPIView.as_view(), name='flight-detail'),
    path('flights/<int:pk>/book', BookTicketsAPIView.as_view(), name='book-ticket'),
    path('flights/<int:pk>/tickets', TicketsAPIView.as_view(), name='tickets'),
    path('flights/<int:pk>/reservations/', ReserveFlightAPIView.as_view(), name='reservations'),
    path('reservations/', AllReservationsAPIView.as_view(), name='all-reservations'),
    path('reservations/<int:pk>/', SingleReservationAPIView.as_view(), name='reservation-detail'),
]
