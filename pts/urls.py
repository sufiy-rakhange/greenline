from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('upload', views.upload, name="upload"),
    path('airlines', views.airlines, name="airlines"),
    path('airports', views.airports, name="airports"),
    path('flights', views.flights, name="flights"),
    path('passengers', views.passengers, name="passengers"),
]