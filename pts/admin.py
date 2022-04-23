from django.contrib import admin
from pts.models import *
# Register your models here.

admin.site.register(Airlines)
admin.site.register(Airports)
admin.site.register(Flights)
admin.site.register(Passengers)
admin.site.register(PassengerFlight)
admin.site.register(Risks)
admin.site.register(PassengerRisk)