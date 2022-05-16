# Including all the required libraries
from django.contrib.auth.hashers import make_password
from django.http import Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
import json
import pandas
from collections import defaultdict

# Login
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
        user = authenticate(request, username=username, password=password)
        # Checking if the user exist
        if not user:
            messages.success(request, "Username and Password did not Match!!!")
            return render(request, "login.html")
        # Signing in genuine user by using django in-built function
        auth_login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        # Displaying login page
        return render(request, 'login.html')

# Logout
@require_http_methods(["GET"])
@login_required(login_url="login")
def logout(request):
    # Signing out by using in-built django function
    auth_logout(request)
    messages.success(
        request, "You have been logged out from the system.")
    return HttpResponseRedirect(reverse("login"))

@require_http_methods(["GET"])
@login_required(login_url="login")
def index(request):
    # Displaying index page
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
            # Creating a user if it is a new username
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
    # Checking if user exist
    try:
        id = request.POST["user_id"]
    except:
        # Displaying error message for invalid users
        messages.error(request, "Invalid user selected")
        return render(request, "add_user.html")
    try:
        # Getting the desired user
        user = User.objects.get(id=id)
        # Deleting a user from model
        user.delete()
        messages.success(request, "User deleted successfully")
        return HttpResponseRedirect(reverse("add_user"))
    except:
        # If the desired user does not exist in the model
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
        try:
        # Checking if the risk name is already taken
            risk = Risks.objects.get(name=name)
            messages.success(request, "Risk already exist")
            return HttpResponseRedirect(reverse("add_risk"))
        except:
            # Creating a new risk
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
    # If the desired id has been passed from web page
    if not id:
        messages.success(request, "Invalid risk selected")
        return render(request, "add_risk.html")
    try:
        # checking if the risk exist
        risk = Risks.objects.get(id=id)
        # Deleting the risk if exist
        risk.delete()
        messages.success(request, "Risk deleted successfully")
        return HttpResponseRedirect(reverse("add_risk"))
    except:
        # Displaying the error message
        messages.error(request, "Invalid risk selected!")
        return HttpResponseRedirect(reverse("add_risk"))

@require_http_methods(["POST"])
@login_required(login_url="login")
def deleteData(request):
    # Getting all the required models
    flights = Flights.objects.all()
    passengers = Passengers.objects.all()
    passengers_flights = PassengerFlight.objects.all()
    passengers_risks = PassengerRisk.objects.all()
    risks = Risks.objects.all()
    # When no data is available to delete
    if len(flights) == 0 or len(passengers) == 0:
        messages.error(request, "No data found for deletion")
        return HttpResponseRedirect(reverse("index"))
    # Deleting all the desired models
    passengers_flights.delete()
    passengers_risks.delete()
    flights.delete()
    passengers.delete()
    risks.delete()
    messages.success(request, "Passenger and Flight data deleted successfully")
    return HttpResponseRedirect(reverse("index"))

@require_http_methods(["POST"])
@login_required(login_url="login")
def upload(request):
    try:
        category = request.POST['category']
    except:
        messages.success(request, 'Must select a category')
        return HttpResponseRedirect(reverse("index"))
    try:
        file = request.FILES['file']
    except:
        messages.success(request, 'Must select a file')
        return HttpResponseRedirect(reverse("index"))

    if category == 'airlines':
        # Reading the file
        data = (pandas.read_excel(file)).to_numpy()
        # Reading the columns
        columns = list(pandas.read_excel(file))
        # Validating with unique column name
        if not '2 Letter Code' in columns:
            messages.error(request, 'Invalid file selected')
            return HttpResponseRedirect(reverse("index"))
        for d in data:
            try:
                Airlines.objects.get(two_letter_code=d[1])
                messages.success(request, 'Airlines already exist')
                return HttpResponseRedirect(reverse("index"))
            except:
                Airlines(
                    company_name=d[0],
                    two_letter_code=d[1],
                    country=d[2],
                ).save()
        messages.success(
            request, 'Airlines details has been added successfully!')
        return HttpResponseRedirect(reverse("index"))

    elif category == 'airport':
        # Reading the file
        data = (pandas.read_excel(file)).to_numpy()
        # Reading the columns
        columns = list(pandas.read_excel(file))
        # Validating with unique column name
        if not 'IATA Code' in columns:
            messages.error(request, 'Invalid file selected')
            return HttpResponseRedirect(reverse("index"))
        for d in data:
            try:
                Airports.objects.get(iata_code=d[0])
                messages.success(request, 'Airport already exist')
                return HttpResponseRedirect(reverse("index"))
            except:
                Airports(
                    iata_code=d[0],
                    iso_alpha_3_code=d[1],
                    long_name=d[2],
                    long_location=d[3],
                ).save()
        messages.success(
            request, 'Airports details has been added successfully!')
        return HttpResponseRedirect(reverse("index"))
    elif category == 'flight':
        if len(Airlines.objects.all()) == 0 or len(Airports.objects.all()) == 0:
            messages.error(request, 'Cannot add flights before airlines and airports')
            return HttpResponseRedirect(reverse("index"))
        # Reading the file
        data = (pandas.read_excel(file)).to_numpy()
        # Reading the columns
        columns = list(pandas.read_excel(file))
        # Validating with unique column name
        if not 'Flight' in columns:
            messages.error(request, 'Invalid file selected')
            return HttpResponseRedirect(reverse("index"))
        for d in data:
            try:
                Flights.objects.get(flight=d[0])
                messages.success(request, 'Flight already exist')
                return HttpResponseRedirect(reverse("index"))
            except:
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
        if len(Flights.objects.all()) == 0:
            messages.error(request, 'Cannot add risk before adding flights')
            return HttpResponseRedirect(reverse("index"))
        # Reading the file
        data = (pandas.read_excel(file)).to_numpy()
        # Reading the columns
        columns = list(pandas.read_excel(file))
        # Validating with unique column name
        if not 'Seat Number' in columns:
            messages.error(request, 'Invalid file selected')
            return HttpResponseRedirect(reverse("index"))
        for d in data:
            try:
                Passengers.objects.get(passport_number=d[4])
                messages.success(request, 'Passenger already exist')
                return HttpResponseRedirect(reverse("index"))
            except:
                flight = Flights.objects.get(
                    flight=d[0]
                )
                f_id = Flights.objects.get(id=flight.id)
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
        if len(Passengers.objects.all()) == 0:
            messages.error(request, 'Cannot add risk before Passenger and Flights')
            return HttpResponseRedirect(reverse("index"))
        # Reading the file
        data = (pandas.read_excel(file)).to_numpy()
        # Reading the columns
        columns = list(pandas.read_excel(file))
        # Validating with unique column name
        if not 'Nationality' in columns:
            messages.error(request, 'Invalid file selected')
            return HttpResponseRedirect(reverse("index"))
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
        # checking for desired airline
        airline = Airlines.objects.get(id=id)
        risks = Risks.objects.all()
    except:
        # when the airline does not exist
        raise Http404("No Such Airline Found")
    passenger_risk = PassengerRisk.objects.all()
    # Filtering fligts with Two Letter Code
    passenger_flight = PassengerFlight.objects.filter(
            f_id__flight__contains=airline.two_letter_code
        )
    # When here is no risk for the airline
    if len(passenger_flight) == 0:
        messages.success(request, "No risk found for this flight")
        return HttpResponseRedirect(reverse("airlines"))

    # Getting all risk object
    risks = Risks.objects.all()
    # Initialising 2D dictionaries
    risk_list = defaultdict(dict)
    risk_list_overall = defaultdict(dict)
    # Looping over to get overall as well as individual risk of Airlines
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
    # When here is no risk for the airport
    if len(passenger_flight) == 0:
        messages.success(request, "No risk found for this flight")
        return HttpResponseRedirect(reverse("airports"))
    risks = Risks.objects.all()
    risk_list = defaultdict(dict)
    risk_list_overall = defaultdict(dict)
    # Looping over to get overall as well as individual risk of Airports
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
    # Checking whether or not the flight is valid
    try:
        flight = Flights.objects.get(id=id)
        risks = Risks.objects.all()
    except:
        raise Http404("No Such Flight Found")
    # Initializing empty array
    arr = {
        'r': []
    }
    # Initializing empty dictionaries
    risk_list = defaultdict(dict)
    risk_list_overall = defaultdict(dict)

    passenger_flight = PassengerFlight.objects.filter(f_id=flight.id).values()
    # Looping over to get overall as well as individual risk of Flights
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
    # Passing all the values in dictionary to html page
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
    # Looping over to get overall as well as individual risk of Passengers
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
