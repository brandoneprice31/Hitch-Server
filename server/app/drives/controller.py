from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .model import Drive
from django.contrib.auth.models import User
from .serializer import DriveSerializer
import json
from django.core import serializers


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
        try:
            drive = Drive.object.create()
            json = json.loads(request.body)
            print(json.__dict__)
            drive.loadFromJSON(json)
            drive.save()
        except:
            return Response(status.HTTP_400_BAD_REQUEST)
        return Response(json, status.HTTP_201_CREATED)





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
