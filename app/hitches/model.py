from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from ..drives.model import Drive
from django.contrib.postgres import fields


# Create your models here.
class Hitch(models.Model):

    # Associate drive.
    drive = models.ForeignKey(Drive, on_delete=models.CASCADE)

    # Driver Info
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Routing Info.
    pick_up_lat = models.FloatField()
    pick_up_long = models.FloatField()
    pick_up_title = models.CharField(max_length = 100)
    pick_up_sub_title = models.CharField(max_length = 100)
    pick_up_date_time = models.DateTimeField()
    drop_off_lat = models.FloatField()
    drop_off_long = models.FloatField()
    drop_off_title = models.CharField(max_length = 100)
    drop_off_sub_title = models.CharField(max_length = 100)
    drop_off_date_time = models.DateTimeField()

    # Occurrence Info
    repeateded_week_days = fields.ArrayField(models.IntegerField())
    accepted = models.BooleanField()

    # Polyline
    start_to_pick_up_polyline = models.FileField(upload_to='./app/hitches/files/', blank=True)
    pick_up_to_drop_off_polyline = models.FileField(upload_to='./app/hitches/files/', blank=True)
    drop_off_to_end_polyline = models.FileField(upload_to='./app/hitches/files/', blank=True)


    def __str__ (self):
        return str(self.user.first_name + " " + self.user.last_name + "'s hitch from " + self.pick_up_title + " to " + self.drop_off_title)
