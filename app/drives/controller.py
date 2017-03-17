from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from mapbox import Distance
from ..profiles.model import Profile
from ..hitches.model import Hitch

from .model import Drive
from django.contrib.auth.models import User
from .serializer import DriveSerializer
import json
from django.core import serializers
from ..users.serializer import UserSerializer
import datetime
from django.utils.timezone import get_current_timezone
from django.utils.dateparse import parse_datetime
from django.core.files.base import ContentFile
import base64
from math import sqrt
from django.db.models import Q




# Gets all user's drives.
# 401 - un-authorized.
# 200 - got all of the user's drives.
@api_view(['GET'])
def list_all(request):

    # Check if the user is anonymous.
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    drives = Drive.objects.filter(driver=request.user)
    driveSerializer = DriveSerializer(drives,many=True)

    return Response(driveSerializer.data, status.HTTP_200_OK)





# Creates a drive for the user.
# 400 - Bad request.
# 201 - created a drive for that user.
# 401 - User is un-authorized
@api_view(['POST'])
def create(request):

    # Check if the user is anonymous.
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    data = json.loads(request.body)
    driveSerializer = DriveSerializer(data=data, context={'driver_id': request.user.id})

    if driveSerializer.is_valid():
        driveSerializer.save()
        return Response(driveSerializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(driveSerializer.errors, status=status.HTTP_400_BAD_REQUEST)







# Gets the details of the given drive.
# 400 - Bad request.
# 200 - returned the user's drives..
# 401 - User is un-authorized
@api_view(['POST'])
def detail(request):

    # Get the drive
    try:
        data = json.loads(request.body)
        drive = Drive.objects.get(pk=data['id'])
    except:
        return Response(status.HTTP_400_BAD_REQUEST)


    # Check if the user is authorized to view that drive.
    if request.user.id != drive.user.id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    driveSerializer = DriveSerializer(drive)
    return Response(driveSerializer.data, status=status.HTTP_200_OK)





# Deletes a drive.
# 400 - Bad request.
# 204 - Deleted the user's drive.
# 401 - User is un-authorized
@api_view(['DELETE'])
def delete(request):

    # Get the drive
    try:
        data = json.loads(request.body)
        drive = Drive.objects.get(pk=data['id'])
    except:
        return Response(status.HTTP_400_BAD_REQUEST)


    # Check if the user is authorized to view that drive.
    if request.user.id != drive.user.id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    drive.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)






# Search for drives given coordinates and time frame.
# 400 - Bad request.
# 200 - Returned available drives (it could be empty).
@api_view(['POST'])
def search(request):

    # Parse json object.
    try:
        data = json.loads(request.body)
        pick_up_lat = data["pick_up_lat"]
        pick_up_long = data["pick_up_long"]
        drop_off_lat = data["drop_off_lat"]
        drop_off_long = data["drop_off_long"]
        start_date_time = parse_datetime(data["start_date_time"])
        end_date_time = parse_datetime(data["end_date_time"])
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    # Build search query.
    # First filter off of date range.
    query = Drive.objects.all().filter(start_date_time__range=(start_date_time,end_date_time))
    query = query.filter(Q(start_date_time__lte=end_date_time) | Q(repeated_week_days__len=0))

    # Ensure that we're aren't pulling the user's drives.
    if not request.user.is_anonymous:
        query = query.exclude(driver_id = request.user.id)

    # Padding defines how far outside bounds you're able to go.
    padding = 1.0

    # Filter based off of pick_up.
    query = query.filter(max_lat__gte = pick_up_lat - padding, min_lat__lte = pick_up_lat + padding)
    query = query.filter(max_long__gte = pick_up_long - padding, min_long__lte = pick_up_long + padding)

    # Filter based off of drop_off.
    query = query.filter(max_lat__gte = drop_off_lat - padding, min_lat__lte = drop_off_lat + padding)
    query = query.filter(max_long__gte = drop_off_long - padding, min_long__lte = drop_off_long + padding)

    # Perform further programmatic filtering.
    pick_up_point = (pick_up_lat,pick_up_long)
    drop_off_point = (drop_off_lat, drop_off_long)

    filteredDrives = []
    for drive in query:

        # Filter each drive based off of distances from pick up / drop off  to start / end
        start_point = (drive.start_lat, drive.start_long)
        end_point = (drive.end_lat, drive.end_long)

        start_to_pick_up = distBetweenPoints(start_point, pick_up_point)
        start_to_drop_off = distBetweenPoints(start_point, drop_off_point)

        # If the hitch is going the same direction as the drive.
        if start_to_pick_up <= start_to_drop_off:
            end_to_pick_up = distBetweenPoints(end_point, pick_up_point)
            end_to_drop_off = distBetweenPoints(end_point, drop_off_point)
            if end_to_drop_off <= end_to_pick_up:
                # Drive passed first round of filtering.

                # Filter by distance api.
                #print(filterByDistance([start_point, pick_up_point, drop_off_point, end_point]))

                # Calculate an estimated time of pick up.
                pick_up_to_drop_off_dist = distBetweenPoints(pick_up_point, drop_off_point)
                start_to_end_min =  (drive.end_date_time - drive.start_date_time).seconds / 60.0
                start_to_end_dist =  start_to_pick_up + pick_up_to_drop_off_dist + end_to_drop_off
                start_to_end_straight = distBetweenPoints(start_point, end_point)
                drive_min_per_deg = start_to_end_min / start_to_end_dist * (start_to_end_dist / start_to_end_straight)
                min_from_pick_up_to_end = drive_min_per_deg * (end_to_drop_off + pick_up_to_drop_off_dist)
                est_pick_up_time = drive.end_date_time - datetime.timedelta(minutes=int(min_from_pick_up_to_end))

                # Convert drive to json and add special fields.
                serializedDrive = DriveSerializer(drive).data
                serializedDrive['estimated_pick_up_date_time'] = est_pick_up_time

                filteredDrives.append(serializedDrive)

    return Response(filteredDrives, status=status.HTTP_200_OK)



# Accepts a hitch request.
# 400 - Bad request.
# 200 - Accepted.
# 401 - User is un-authorized
@api_view(['POST'])
def accept_hitch (request):

    if request.user.is_anonymous():
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    # Get JSON.
    data = json.loads(request.body)

    try:

        drive = Drive.objects.get(id=data["drive_id"])

        if drive.driver_id != request.user.id:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        hitch = Hitch.objects.get(id=data["hitch_id"])
        hitch.accepted = True
        hitch.save()
        # Notify the hitchhiker.

    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)




# Function that finds the distance between two points.
def distBetweenPoints (pointA, pointB):
    return sqrt((pointA[0] - pointB[0])**2 + (pointA[1] - pointB[1])**2)


# Function that filters a list of points using mapbox distance api.
def filterByDistance(points):

    service = Distance()

    geoJsonList = []

    for point_iter in range(len(points)):
        geoJsonList.append({
        'type': 'Feature',
        'properties': {'name': ['start','pick_up','drop_off','end'][point_iter]},
        'geometry': {
            'type': 'Point',
            'coordinates': [points[point_iter][0], points[point_iter][1]]
            }
        })

    response = service.distances(geoJsonList, 'driving')
    print(geoJsonList)
    return(response.json()['durations'])
