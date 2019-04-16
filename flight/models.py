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
    status = models.CharField(choices=FLIGHT_STATUS, max_length=150, default="scheduled")

    def __str__(self):
        return f"Flight {self.name}"


class Reservation(models.Model):
    RESERVATION_STATUS = (
        ("active", "Active"),
        ("canceled", "Canceled"),
        ("late", "Late"),
        ("done", "Done")
    )

    origin = models.CharField(verbose_name='passenger origin', max_length=50, null=False)
    destination = models.CharField(verbose_name='passenger destination', max_length=50, null=False)
    date_of_travel = models.DateField(verbose_name="Date of Travel")
    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, blank=True, null=True, related_name='reservations')
    status = models.CharField(choices=RESERVATION_STATUS, max_length=150, default="active")

    def __str__(self):
        return f"Reservation for {self.passenger.email}"
