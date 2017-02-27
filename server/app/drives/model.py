from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.postgres import fields

# Create your models here.
class Drive(models.Model):

    # Driver Info
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Routing Info.
    start_lat = models.FloatField()
    start_long = models.FloatField()
    start_title = models.CharField(max_length = 100)
    start_sub_title = models.CharField(max_length = 100)
    start_date_time = models.DateTimeField()
    end_lat = models.FloatField()
    end_long = models.FloatField()
    end_title = models.CharField(max_length = 100)
    end_sub_title = models.CharField(max_length = 100)
    end_date_time = models.DateTimeField()

    # Occurrence Info
    repeated_week_days = fields.ArrayField(models.IntegerField())

    # Polyline
    polyline = models.BinaryField(blank=True)


    def __str__ (self):
        return str(self.id)

    def loadFromJSON (json):

        if 'user' in json:
            self.user = json['user']
        self.start_lat = json['start_lat']
        self.start_long = json['start_long']
        self.start_title = json['start_title']
        self.start_sub_title = json['start_sub_title']
        self.start_time = json['start_time']
        self.end_lat = json['end_lat']
        self.end_long = json['end_long']
        self.end_title = json['end_title']
        self.end_sub_title = json['end_sub_title']
        self.end_time = json['end_time']
        self.repeated_week_days = json['repeated_week_days']
        self.start_date = json['start_date']
        self.polyline = json['polyline']
