from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from mapbox import Distance

from ..profiles.model import Profile
from ..drives.model import Drive
from .model import Hitch
from django.contrib.auth.models import User

from .serializer import HitchSerializer

import json
from django.core import serializers
import datetime
from django.utils.timezone import get_current_timezone
from django.utils.dateparse import parse_datetime
from django.core.files.base import ContentFile
import base64
from math import sqrt


@api_view(['GET', 'POST'])
def hitch_list(request):

    if request.user.is_anonymous:
        # User is un-authorized.
        return Response(status=status.HTTP_401_UNAUTHORIZED)



    if request.method == 'GET':
        hitches = Hitch.objects.all().filter(user_id=request.user.id)
        serializedHitches = HitchSerializer(hitches, many=True)
        return Response(serializedHitches.data, status=status.HTTP_200_OK)



    elif request.method == 'POST':
        # Load json.
        hitchJSON = json.loads(request.body)

        if hitchJSON["user"] != request.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # Associate drive.
        drive = hitchJSON["drive"]

        # Driver Info
        user = hitchJSON["user"]

        # Routing Info.
        pick_up_lat = hitchJSON["pick_up_lat"]
        pick_up_long = hitchJSON["pick_up_long"]
        pick_up_title = hitchJSON["pick_up_title"]
        pick_up_sub_title = hitchJSON["pick_up_sub_title"]
        pick_up_date_time = hitchJSON["pick_up_date_time"]
        drop_off_lat = hitchJSON["drop_off_lat"]
        drop_off_long = hitchJSON["drop_off_long"]
        drop_off_title = hitchJSON["drop_off_title"]
        drop_off_sub_title = hitchJSON["drop_off_sub_title"]
        drop_off_date_time = hitchJSON["drop_off_date_time"]

        # Occurrence Info
        repeated_week_days = hitchJSON["repeated_week_days"]
        accepted = hitchJSON["accepted"]

        # Polyline
        start_to_pick_up_polyline = hitchJSON["start_to_pick_up_polyline"]
        pick_up_to_drop_off_polyline = hitchJSON["pick_up_to_drop_off_polyline"]
        drop_off_to_end_polyline = hitchJSON["drop_off_to_end_polyline"]

        #try:
        if True:
            hitch = Hitch.objects.create(drive_id=drive,user_id=user,pick_up_lat=pick_up_lat,pick_up_long=pick_up_long,
                                pick_up_title=pick_up_title, pick_up_sub_title=pick_up_sub_title, drop_off_lat=drop_off_lat,
                                drop_off_long=drop_off_long, drop_off_title=drop_off_title,drop_off_sub_title=drop_off_sub_title,
                                pick_up_date_time=pick_up_date_time,drop_off_date_time=drop_off_date_time,
                                repeated_week_days=repeated_week_days,accepted=accepted)

            start_to_pick_up_polylineFile = ContentFile(base64.b64decode(start_to_pick_up_polyline))
            hitch.start_to_pick_up_polyline.save(str(hitch.user_id) + "/" + str(hitch.id) + "/StartToPickUp", start_to_pick_up_polylineFile)

            pick_up_to_drop_off_polylineFile = ContentFile(base64.b64decode(pick_up_to_drop_off_polyline))
            hitch.pick_up_to_drop_off_polyline.save(str(hitch.user_id) + "/" + str(hitch.id) + "/PickupToDropOff", pick_up_to_drop_off_polylineFile)

            drop_off_to_end_polylineFile = ContentFile(base64.b64decode(drop_off_to_end_polyline))
            hitch.drop_off_to_end_polyline.save(str(hitch.user_id) + "/" + str(hitch.id) + "/DropOffToEnd", drop_off_to_end_polylineFile)
        #except:
        #    return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)
