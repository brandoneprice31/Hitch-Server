from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.postgres import fields
import base64


# Create your models here.
class Drive(models.Model):

    # Driver Info
    driver = models.ForeignKey(User, on_delete=models.CASCADE)

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

    # Rectangular region info.
    max_lat = models.FloatField()
    max_long = models.FloatField()
    min_lat = models.FloatField()
    min_long = models.FloatField()

    # Occurrence Info
    repeated_week_days = fields.ArrayField(models.IntegerField())

    # Polyline
    polyline = models.BinaryField()


    def __str__ (self):
        return str(self.driver.first_name + " " + self.driver.last_name + "'s drive from " + self.start_title + " to " + self.end_title)
