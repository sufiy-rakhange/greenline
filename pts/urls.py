from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),

    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),

    # User URLs
    path('add-user', views.addUser, name="add_user"),
    path('delete-user', views.deleteUser, name="delete_user"),

    # Risk URLs
    path('add-risk', views.addRisk, name="add_risk"),
    path('delete-risk', views.deleteRisk, name="delete_risk"),


    # To upload the files
    path('upload', views.upload, name="upload"),

    # Airlines
    path('airlines', views.airlines, name="airlines"),
    path('airline/<id>', views.airlineRisk, name="airline_risk"),


    path('airports', views.airports, name="airports"),
    path('airport/<id>', views.airportRisk, name="airport_risk"),


    path('flights', views.flights, name="flights"),
    path('flight/<id>', views.flightRisk, name="flight_risk"),

    path('passengers', views.passengers, name="passengers"),
    path('passenger/<id>/<p_id>', views.passengerRisk, name="passenger_risk"),
]