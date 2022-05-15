import email
import enum
import imp
from math import floor
import re
from unicodedata import category, name
from django.contrib.auth.hashers import make_password
from django.http import Http404, HttpResponse, request, response
from django.template import context
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from numpy import array
from .models import *
import io, json
import pandas
import numpy
from collections import defaultdict

# Create your views here.
@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == 'POST':
        # Getting Form Fields
        username = request.POST["username"]
        if not username:
            messages.success(request, "Must Provide a Username!")
            return render(request, "login.html")
        password = request.POST["password"]
        if not password:
            messages.success(request, "Must Provide Password!!")
            return render(request, "login.html")
        user = authenticate(request, username=username, password=password, is_staff=True)
        if not user:
            messages.success(request, "Username and Password did not Match!!!")
            return render(request, "login.html")
        auth_login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, 'login.html')

@require_http_methods(["GET"])
@login_required(login_url="login")
def logout(request):
    auth_logout(request)
    messages.success(
        request, "You have been logged out from the system.")
    return HttpResponseRedirect(reverse("login"))

@require_http_methods(["GET"])
@login_required(login_url="login")
def index(request):
    return render(request, 'index.html')


# User
@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def addUser(request):
    if request.method == 'POST':
        # Getting Form Fields
        username = request.POST["username"]
        if not username:
            messages.success(request, "Must Provide a Username!")
            return render(request, "add_user.html")
        password = request.POST["password"]
        if not password:
            messages.success(request, "Must Provide Password!!")
            return render(request, "add_user.html")

        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        email = request.POST["email"]
        # Checking if the username is already taken
        try:
            User.objects.get(username=username)
            messages.success(request, "Username already exist")
            return HttpResponseRedirect(reverse("add_user"))
        except:
            User.objects.create(
                username=username,
                password=make_password(password),
                first_name=firstname,
                last_name=lastname,
                email=email
            ).save()
            messages.success(request, "User has been created successfully")
            return HttpResponseRedirect(reverse("add_user"))
    else:
        # Getting all the users
        users = User.objects.filter(is_superuser=False)

         # Using Django pagination
        paginator = Paginator(users, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'add_user.html', {'page_obj': page_obj})

@require_http_methods(["POST"])
@login_required(login_url="login")
def deleteUser(request):
    id = request.POST["user_id"]
    if not id:
        messages.success(request, "Invalid user selected")
        return render(request, "add_user.html")
    try:
        user = User.objects.get(id=id)
        user.delete()
        messages.success(request, "User deleted successfully")
        return HttpResponseRedirect(reverse("add_user"))
    except:
        messages.success(request, "Invalid user selected!")
        return HttpResponseRedirect(reverse("add_user"))


# Risk Page
@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def addRisk(request):
    if request.method == 'POST':
        # Getting Form Fields
        name = request.POST["name"]
        if not name:
            messages.success(request, "Must provide a name for Risk!")
            return render(request, "add_risk.html")
        # Checking if the username is already taken
        try:
            risk = Risks.objects.get(name=name)
            messages.success(request, "Risk already exist")
            return HttpResponseRedirect(reverse("add_risk"))
        except:
            Risks.objects.create(
                name=name
            )
            messages.success(request, "User has been created successfully")
            return HttpResponseRedirect(reverse("add_risk"))
    else:
        # Getting all the risks
        risks = Risks.objects.all()

        # Using Django pagination
        paginator = Paginator(risks, 15)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'add_risk.html', {'page_obj': page_obj})

@require_http_methods(["POST"])
@login_required(login_url="login")
def deleteRisk(request):
    id = request.POST["risk_id"]
    if not id:
        messages.success(request, "Invalid risk selected")
        return render(request, "add_risk.html")
    try:
        risk = Risks.objects.get(id=id)
        risk.delete()
        messages.success(request, "Risk deleted successfully")
        return HttpResponseRedirect(reverse("add_risk"))
    except:
        messages.success(request, "Invalid risk selected!")
        return HttpResponseRedirect(reverse("add_risk"))


@require_http_methods(["POST"])
@login_required(login_url="login")
def upload(request):
    try:
        file = request.FILES['file']
    except:
        messages.success(request, 'Must select a file')
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
        messages.success(
            request, 'Airlines details has been added successfully!')
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
        messages.success(
            request, 'Airports details has been added successfully!')
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
        messages.success(
            request, 'Flights details has been added successfully!')
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
                p_id=p_id,
                f_id=f_id,
                seat_number=d[1]
            ).save()
        messages.success(
            request, 'Passengers details has been added successfully!')
        return HttpResponseRedirect(reverse("index"))
    elif category == 'risk':
        columns = list(pandas.read_excel(file))
        data = (pandas.read_excel(file)).to_numpy()
        for row in data:
            count = 0
            passenger = Passengers.objects.filter(passport_number=row[5]).first()
            for column in row:
                if (count >= 6):
                    try:
                        risk = Risks.objects.get(name=columns[count])

                    except:
                        risk = Risks.objects.create(
                            name=columns[count]
                        )

                    PassengerRisk.objects.create(
                        p_id=passenger,
                        r_id=risk,
                        value=(column * 100)
                    ).save()
                count += 1

        messages.success(request, 'Risk has been added successfully!')
        return HttpResponseRedirect(reverse("index"))


# Airlines
@require_http_methods(["GET"])
@login_required(login_url="login")
def airlines(request):
    # Getting all the airlines
    airlines = Airlines.objects.all()

    # Using Django pagination
    paginator = Paginator(airlines, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Rendering airlines page with required values
    return render(request, 'airlines.html', {'page_obj': page_obj})

@require_http_methods(["GET"])
@login_required(login_url="login")
def airlineRisk(request, id):
    try:
        airline = Airlines.objects.get(id=id)
        risks = Risks.objects.all()
    except:
        raise Http404("No Such Airline Found")
    passenger_risk = PassengerRisk.objects.all()
    passenger_flight = PassengerFlight.objects.filter(
        f_id__flight__contains=airline.two_letter_code
    )
    risks = Risks.objects.all()
    risk_list = defaultdict(dict)
    risk_list_overall = defaultdict(dict)
    for i in passenger_flight:
        passengers = PassengerRisk.objects.filter(p_id=i.p_id)
        for p in passengers.values():
            risk = Risks.objects.get(id=p['r_id_id'])
            flight = Flights.objects.get(id=i.f_id_id)
            try:
                risk_list[flight.flight][risk.name] += p["value"]
            except:
                risk_list[flight.flight][risk.name] = p["value"]

            try:
                risk_list_overall['Overall'][risk.name] += p["value"]
            except:
                risk_list_overall['Overall'][risk.name] = p["value"]
    arr = {
        'r': []
    }
    for risk in risks.values():
        arr['r'].append(risk)
    print(risk_list)
    context = {
        'airline': airline,
        'passenger_risk': passenger_risk,
        'risks': risks,
        'js_risk': json.dumps(arr['r']),
        'js_passenger': json.dumps(risk_list),
        'js_passenger_overall': json.dumps(risk_list_overall)
    }
    return render(request, "risks/airline.html", context)


# Airports
@require_http_methods(["GET"])
@login_required(login_url="login")
def airports(request):
    # Getting all the airports
    airports = Airports.objects.all()

    # Using Django pagination
    paginator = Paginator(airports, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Rendering airlines page with required values
    return render(request, 'airports.html', {'page_obj': page_obj})

@require_http_methods(["GET"])
@login_required(login_url="login")
def airportRisk(request, id):
    airport = Airports.objects.get(id=id)
    passenger_risk = PassengerRisk.objects.all()
    passenger_flight = PassengerFlight.objects.filter(
        f_id__arrival=airport.iata_code
    )
    risks = Risks.objects.all()
    risk_list = defaultdict(dict)
    risk_list_overall = defaultdict(dict)
    for i in passenger_flight:
        passengers = PassengerRisk.objects.filter(p_id=i.p_id)
        for p in passengers.values():
            risk = Risks.objects.get(id=p['r_id_id'])
            flight = Flights.objects.get(id=i.f_id_id)
            try:
                risk_list[flight.flight][risk.name] += p["value"]
            except:
                risk_list[flight.flight][risk.name] = p["value"]

            try:
                risk_list_overall['Overall'][risk.name] += p["value"]
            except:
                risk_list_overall['Overall'][risk.name] = p["value"]
    arr = {
        'r': []
    }
    for risk in risks.values():
        arr['r'].append(risk)
    context = {
        'airport': airport,
        'passenger_risk': passenger_risk,
        'risks': risks,
        'js_risk': json.dumps(arr['r']),
        'js_passenger': json.dumps(risk_list),
        'js_passenger_overall': json.dumps(risk_list_overall)
    }
    return render(request, "risks/airport.html", context)


# Flights
@require_http_methods(["GET"])
@login_required(login_url="login")
def flights(request):
    # Getting all the flights
    flights = Flights.objects.all()

    # Using Django pagination
    paginator = Paginator(flights, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Rendering airlines page with required values
    return render(request, 'flights.html', {'page_obj': page_obj})

@require_http_methods(["GET"])
@login_required(login_url="login")
def flightRisk(request, id):
    try:
        flight = Flights.objects.get(id=id)
        risks = Risks.objects.all()
    except:
        raise Http404("No Such Flight Found")
    arr = {
        'r': []
    }

    risk_list = defaultdict(dict)
    risk_list_overall = defaultdict(dict)
    passenger_flight = PassengerFlight.objects.filter(f_id=flight.id).values()

    for i in passenger_flight:
        passengers = PassengerRisk.objects.filter(p_id=i['p_id_id'])
        for p in passengers.values():
            passenger = Passengers.objects.get(id=p['p_id_id'])
            risk = Risks.objects.get(id=p['r_id_id'])
            risk_list[passenger.forename][risk.name] = p["value"]
            try:
                risk_list_overall['Overall'][risk.name] += p["value"]
            except:
                risk_list_overall['Overall'][risk.name] = p["value"]

    # When there is no risk for flight
    if len(passenger_flight) == 0 or len(passengers) == 0:
        messages.success(request, "No risk found for this flight")
        return HttpResponseRedirect(reverse("flights"))
    for risk in risks.values():
        arr['r'].append(risk)
    context = {
        'flight': flight,
        'risks': risks,
        'js_risk': json.dumps(arr['r']),
        'js_passenger': json.dumps(risk_list),
        'js_passenger_overall': json.dumps(risk_list_overall)
    }
    return render(request, "risks/flight.html", context)


# Passengers
@require_http_methods(["GET"])
@login_required(login_url="login")
def passengers(request):
    # Getting all the passengers
    passenger_flight = PassengerFlight.objects.all()

     # Using Django pagination
    paginator = Paginator(passenger_flight, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Rendering airlines page with required values
    return render(request, 'passengers.html', {'page_obj': page_obj})

@require_http_methods(["GET"])
@login_required(login_url="login")
def passengerRisk(request, id, p_id):
    try:
        passenger = PassengerFlight.objects.filter(id=id)
        p_risk = PassengerRisk.objects.filter(p_id=p_id)
        risks = Risks.objects.all()
    except:
        raise Http404("No Such Flight Found")

    # When there is no risk for the passenger
    if len(p_risk) == 0:
        messages.success(request, "No risk found for this passenger")
        return HttpResponseRedirect(reverse("passengers"))

    arr = {
        'a' : [],
        'r': []
    }
    for p in p_risk.values():
        arr['a'].append(p)
    for risk in risks.values():
        arr['r'].append(risk)

    context = {
        'risks': risks,
        'passenger': passenger.values(),
        'p': passenger,
        'p_risk': p_risk,
        'js_passenger': json.dumps(arr['a']),
        'js_risk': json.dumps(arr['r']),
    }
    return render(request, "risks/passenger.html", context)
