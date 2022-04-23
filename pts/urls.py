from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('upload', views.upload, name="upload"),

    # Airlines
    path('airlines', views.airlines, name="airlines"),
    path('airline/<id>', views.airlineRisk, name="airline_risk"),


    path('airports', views.airports, name="airports"),
    path('airport/<id>', views.airportRisk, name="airport_risk"),


    path('flights', views.flights, name="flights"),
    path('flight/<id>', views.flightRisk, name="flight_risk"),

    path('passengers', views.passengers, name="passengers"),
    path('passenger/<id>', views.passengerRisk, name="passenger_risk"),
]