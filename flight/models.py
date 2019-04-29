from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Flight(models.Model):
    FLIGHT_STATUS = (
        ("scheduled", "Scheduled"),
        ("active", "Active"),
        ("landed", "Landed")
    )

    name = models.CharField(verbose_name='flight name', max_length=50, unique=True, null=False)
    origin = models.CharField(verbose_name='flight origin', max_length=50, null=False)
    destination = models.CharField(verbose_name='flight destination', max_length=50, null=False)
    date_of_travel = models.DateTimeField(verbose_name="Date And Time of Travel")
    capacity = models.IntegerField(verbose_name='Number of passengers the flight can accommodate.', null=False)
    reservations_available = models.IntegerField(verbose_name='Number of reservations left for the flight', null=False)
    status = models.CharField(choices=FLIGHT_STATUS, max_length=150, default="scheduled")
    cost = models.IntegerField(verbose_name="Cost in dollars for the Flight.", null=False, default=0)

    def __str__(self):
        return f"Flight {self.name}"


class Reservation(models.Model):
    RESERVATION_STATUS = (
        ("active", "Active"),
        ("canceled", "Canceled"),
        ("late", "Late"),
        ("done", "Done")
    )
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passenger_reservations')
    flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, blank=True, null=True, related_name='flight_reservations')
    status = models.CharField(choices=RESERVATION_STATUS, max_length=150, default="active")

    def __str__(self):
        return f"Reservation for {self.passenger.email}"


class Ticket(models.Model):
    TICKET_STATUS = (
        ("paid", "Paid"),
        ("not_paid", "Not Paid"),
    )
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='tickets')
    status = models.CharField(choices=TICKET_STATUS, max_length=10, default='not_paid')

    def __str__(self):
        return f"Ticket for {self.reservation.passenger.email}"
