from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .model import Drive
from django.contrib.auth.models import User
from .serializer import DriveSerializer
import json
from django.core import serializers
from django.utils.timezone import get_current_timezone
from django.utils.dateparse import parse_datetime
from django.core.files.base import ContentFile
import base64


@api_view(['GET', 'POST'])
def user_drive_list(request):

    # Check if the user is anonymous.
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


    # GET
    if request.method == 'GET':

        drives = Drive.objects.filter(user=request.user).values()
        driveSerializer = DriveSerializer(drives,many=True)

        return Response(driveSerializer.data, status.HTTP_200_OK)


    # POST
    elif request.method == 'POST':

        data = json.loads(request.body)
        start_lat = data['start_lat']
        start_long = data['start_long']
        start_title = data['start_title']
        start_sub_title = data['start_sub_title']
        start_date_time = parse_datetime(data['start_date_time'])
        end_lat = data['end_lat']
        end_long = data['end_long']
        end_title = data['end_title']
        end_sub_title = data['end_sub_title']
        end_date_time = parse_datetime(data['end_date_time'])
        repeated_week_days = data['repeated_week_days']

        try:
            drive = Drive.objects.create(user=request.user, start_lat=start_lat,
                                    start_long=start_long, start_title=start_title,
                                    start_date_time=start_date_time, end_lat=end_lat,
                                    end_long=end_long, end_title=end_title,
                                    end_sub_title=end_sub_title, end_date_time=end_date_time,
                                    repeated_week_days=repeated_week_days)

            polyLineFile = ContentFile(base64.b64decode(data['polyline']))
            drive.polyline.save(str(drive.user_id) + "/" + str(drive.id), polyLineFile)

        except:
            Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_201_CREATED)





@api_view(['GET', 'DELETE'])
def user_drive_detail(request, pk):

    # Get the drive
    try:
        drive = Drive.objects.get(pk=pk)
    except:
        return Response(status.HTTP_400_BAD_REQUEST)


    # Check if the user is authorized to view that drive.
    if request.user.id != drive.user.id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


    # GET
    if request.method == 'GET':
        driveSerializer = DriveSerializer(drive)
        return Response(driveSerializer.data, status=status.HTTP_200_OK)


    # DELETE
    elif request.method == 'DELETE':
        drive.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
