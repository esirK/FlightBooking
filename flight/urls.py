from django.urls import path
from flight.views import FlightAPIView, FlightDetailsAPIView,\
    ReserveFlightAPIView, SingleReservationAPIView, AllReservationsAPIView, \
    TicketsAPIView, BookTicketsAPIView, TicketDetailAPIView, PayTicketAPIView, \
    execute, cancel


app_name = "flight"


urlpatterns = [
    path('flights/', FlightAPIView.as_view(), name='flights'),
    path('flights/<int:pk>/', FlightDetailsAPIView.as_view(), name='flight-detail'),
    path('flights/<int:pk>/book', BookTicketsAPIView.as_view(), name='book-ticket'),
    path('flights/<int:pk>/reservations/', ReserveFlightAPIView.as_view(), name='reservations'),
    path('reservations/', AllReservationsAPIView.as_view(), name='all-reservations'),
    path('reservations/<int:pk>/', SingleReservationAPIView.as_view(), name='reservation-detail'),
    path('tickets/', TicketsAPIView.as_view(), name='tickets'),
    path('tickets/<int:pk>', TicketDetailAPIView.as_view(), name='ticket-detail'),
    path('tickets/<int:pk>/pay/', PayTicketAPIView.as_view(), name='pay-ticket'),
    path('execute/<int:ticket_pk>/', execute, name='execute'),
    path('cancel/', cancel, name='cancel'),
]
