from django.db import models

# Create your models here.


class Airlines(models.Model):
    company_name = models.CharField(max_length=50)
    two_letter_code = models.CharField(max_length=5)
    country = models.CharField(max_length=50)


class Airports(models.Model):
    iata_code = models.CharField(max_length=3)
    iso_alpha_3_code = models.CharField(max_length=3)
    long_name = models.CharField(max_length=50)
    long_location = models.CharField(max_length=50)


class Flights(models.Model):
    flight = models.CharField(max_length=10)
    departure = models.CharField(max_length=3)
    arrival = models.CharField(max_length=3)
    terminal = models.CharField(max_length=2)
    aircraft = models.CharField(max_length=10)
    capacity = models.IntegerField()
    crew = models.IntegerField()


class Passengers(models.Model):
    forename = models.CharField(max_length=20)
    family_name = models.CharField(max_length=20)
    gender = models.CharField(max_length=2, null=True)
    dob = models.CharField(max_length=10, null=True)
    nationality = models.CharField(max_length=20, null=True)
    passport_number = models.CharField(max_length=50)
    country_of_issue = models.CharField(max_length=50)


class Risks(models.Model):
    name = models.CharField(max_length=50)


class PassengerFlight(models.Model):
    p_id = models.ForeignKey(Passengers, on_delete=models.DO_NOTHING)
    f_id = models.ForeignKey(Flights, on_delete=models.DO_NOTHING)
    seat_number = models.CharField(max_length=20)


class PassengerRisk(models.Model):
    p_id = models.ForeignKey(Passengers, on_delete=models.DO_NOTHING)
    r_id = models.ForeignKey(Risks, on_delete=models.DO_NOTHING)
    value = models.DecimalField(max_digits=3, decimal_places=2)
