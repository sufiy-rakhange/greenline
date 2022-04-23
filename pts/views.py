import imp
import re
from unicodedata import category
from django.http import Http404, HttpResponse, request, response
from django.core import paginator
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from numpy import array
from .models import *
import io
import pandas, numpy

# Create your views here.

def index(request):
    return render(request, 'index.html')

def upload(request):
    try:
        file = request.FILES['file']
    except:
        messages.success(request, 'Must Select a FILE')
        return HttpResponseRedirect(reverse("index"))

    category = request.POST['category']

    if category == 'airlines':
        data = (pandas.read_excel(file)).to_numpy()
        for d in data:
            Airlines(
                company_name=d[0],
                two_letter_code=d[1],
                country=d[2],
            ).save()
        messages.success(request, 'Airlines details has been added successfully!')
        return HttpResponseRedirect(reverse("index"))
    elif category == 'airport':
        data = (pandas.read_excel(file)).to_numpy()
        for d in data:
            Airports(
                iata_code=d[1],
                iso_alpha_3_code=d[2],
                long_name=d[3],
                long_location=d[4],
            ).save()
        messages.success(request, 'Airports details has been added successfully!')
        return HttpResponseRedirect(reverse("index"))
    elif category == 'flight':
        data = (pandas.read_excel(file)).to_numpy()
        for d in data:
            Flights(
                flight=d[0],
                departure=d[1],
                arrival=d[2],
                terminal=d[3],
                aircraft=d[4],
                capacity=d[5],
                crew=d[6],
            ).save()
        messages.success(request, 'Flights details has been added successfully!')
        return HttpResponseRedirect(reverse("index"))
    elif category == 'passenger':
        data = (pandas.read_excel(file)).to_numpy()
        for d in data:
            flight = Flights.objects.get(
                flight=d[0]
            )
            f_id = Flights.objects.get(id=flight.id)
            print("f =>", f_id.id)
            p = Passengers(
                forename=d[2],
                family_name=d[3],
                passport_number=d[4],
                country_of_issue=d[5],
            )
            p.save()
            p_id = Passengers.objects.get(id=p.id)
            PassengerFlight(
                p_id = p_id,
                f_id = f_id,
                seat_number=d[1]
            ).save()
        messages.success(request, 'Passengers details has been added successfully!')
        return HttpResponseRedirect(reverse("index"))
    elif category == 'risk':
        data = (pandas.read_excel(file)).to_numpy()
        for d in data:
            Risks(
                name=d[0],
            ).save()
        messages.success(request, 'Risk has been added successfully!')
        return HttpResponseRedirect(reverse("index"))


# Airlines
def airlines(request):
    airlines = Airlines.objects.all()
    return render(request, 'airlines.html', {'airlines': airlines})

def airlineRisk(request, id):
    try:
        airline = Airlines.objects.get(id=id)
    except:
        raise Http404("No Such Student Found")
    return render(request, "risks/airline.html", {'airline' :airline})

# Airports
def airports(request):
    airports = Airports.objects.all()
    return render(request, 'airports.html', {'airports': airports})

def airportRisk(request, id):
    try:
        airport = Airports.objects.get(id=id)
    except:
        raise Http404("No Such Student Found")
    return render(request, "risks/airport.html", {'airport' :airport})

# Flights
def flights(request):
    flights = Flights.objects.all()
    return render(request, 'flights.html', {'flights': flights})

def flightRisk(request, id):
    try:
        flight = Flights.objects.get(id=id)
    except:
        raise Http404("No Such Student Found")
    return render(request, "risks/airport.html", {'flight' :flight})

# Passengers
def passengers(request):
    passenger_flight = PassengerFlight.objects.all()
    return render(request, 'passengers.html', {'passengers': passenger_flight})

def passengerRisk(request, id):
    try:
        passenger = Passengers.objects.get(id=id)
    except:
        raise Http404("No Such Student Found")
    return render(request, "risks/airport.html", {'passenger' :passenger})
