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



# Gets all of the user's hitches.
# 401 - un-authorized
# 200 - got all of the user's hitches.
@api_view(['GET'])
def list_all(request):

    if request.user.is_anonymous:
        # User is un-authorized.
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    hitches = Hitch.objects.all().filter(hitch_hiker_id=request.user.id)
    serializedHitches = HitchSerializer(hitches, many=True)
    return Response(serializedHitches.data, status=status.HTTP_200_OK)




# Creates a new hitch.
# 401 - un-authorized
# 400 - bad request.
# 201 - new hitch created.
@api_view(['POST'])
def create(request):

    # Check if the user is anonymous.
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    data = json.loads(request.body)
    hitchSerializer = HitchSerializer(data=data, context={'hitch_hiker_id': request.user.id, 'drive_id' : data['drive_id']})

    if hitchSerializer.is_valid():
        hitchSerializer.save()
        return Response(hitchSerializer.data, status=status.HTTP_201_CREATED)
    else:
        print(hitchSerializer.errors)
        return Response(hitchSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
