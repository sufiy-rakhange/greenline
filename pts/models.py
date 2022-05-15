from django.db import models

# Create your models here.


class Airlines(models.Model):
    company_name = models.CharField(max_length=50)
    two_letter_code = models.CharField(max_length=5)
    country = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.company_name}, {self.two_letter_code}, {self.country}"

class Airports(models.Model):
    iata_code = models.CharField(max_length=3)
    iso_alpha_3_code = models.CharField(max_length=3)
    long_name = models.CharField(max_length=50)
    long_location = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.iata_code}, {self.iso_alpha_3_code}, {self.long_name}, {self.long_location}"

class Flights(models.Model):
    flight = models.CharField(max_length=10)
    departure = models.CharField(max_length=3)
    arrival = models.CharField(max_length=3)
    terminal = models.CharField(max_length=2)
    aircraft = models.CharField(max_length=10)
    capacity = models.IntegerField()
    crew = models.IntegerField()
    def __str__(self):
        return f"{self.flight}, {self.departure}, {self.arrival}, {self.terminal}, {self.aircraft}, {self.capacity}, {self.crew}"

class Passengers(models.Model):
    forename = models.CharField(max_length=20)
    family_name = models.CharField(max_length=20)
    gender = models.CharField(max_length=2, null=True)
    dob = models.CharField(max_length=10, null=True)
    nationality = models.CharField(max_length=20, null=True)
    passport_number = models.CharField(max_length=50)
    country_of_issue = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.forename}, {self.family_name}, {self.gender}, {self.dob}, {self.nationality}, {self.passport_number}, {self.country_of_issue}"

class Risks(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}"

class PassengerFlight(models.Model):
    p_id = models.ForeignKey(Passengers, on_delete=models.DO_NOTHING)
    f_id = models.ForeignKey(Flights, on_delete=models.DO_NOTHING)
    seat_number = models.CharField(max_length=20)
    def __str__(self):
        return f"{self.p_id}, {self.f_id}, {self.seat_number}"

class PassengerRisk(models.Model):
    p_id = models.ForeignKey(Passengers, on_delete=models.DO_NOTHING)
    r_id = models.ForeignKey(Risks, on_delete=models.DO_NOTHING)
    value = models.IntegerField()
    def __str__(self):
        return f"{self.p_id}, {self.r_id}, {self.value}"