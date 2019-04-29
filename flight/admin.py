from django.contrib import admin
from .models import Flight, Reservation, Ticket

admin.site.register(Flight)
admin.site.register(Reservation)
admin.site.register(Ticket)
