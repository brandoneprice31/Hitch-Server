from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from mapbox import Distance
from ..profiles.model import Profile

from .model import Drive
from django.contrib.auth.models import User
from .serializer import DriveSerializer
import json
from django.core import serializers
import datetime
from django.utils.timezone import get_current_timezone
from django.utils.dateparse import parse_datetime
from django.core.files.base import ContentFile
import base64
from math import sqrt
from django.db.models import Q


@api_view(['GET', 'POST'])
def user_drive_list(request):

    # Check if the user is anonymous.
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


    # GET
    if request.method == 'GET':

        drives = Drive.objects.filter(user=request.user)
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
        max_lat = data['max_lat']
        max_long = data['max_long']
        min_lat = data['min_lat']
        min_long = data['min_long']

        try:
            drive = Drive.objects.create(user=request.user, start_lat=start_lat,
                                    start_long=start_long, start_title=start_title,
                                    start_date_time=start_date_time, end_lat=end_lat,
                                    end_long=end_long, end_title=end_title,
                                    end_sub_title=end_sub_title, end_date_time=end_date_time,
                                    repeated_week_days=repeated_week_days, max_lat=max_lat,
                                    max_long=max_long, min_lat=min_lat, min_long=min_long)

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





@api_view(['POST'])
def drive_search(request):

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
    query = Drive.objects.all().filter(Q(start_date_time__lte=end_date_time) | Q(repeated_week_days__len=0, start_date_time__range=(start_date_time,end_date_time)))

    # Ensure that we're aren't pulling the user's drives.
    if not request.user.is_anonymous:
        query = query.exclude(user_id = request.user.id)

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

        start_to_pick_up = distBetweenPointsSquared(start_point, pick_up_point)
        start_to_drop_off = distBetweenPointsSquared(start_point, drop_off_point)

        # If the hitch is going the same direction as the drive.
        if start_to_pick_up <= start_to_drop_off:
            end_to_pick_up = distBetweenPointsSquared(end_point, pick_up_point)
            end_to_drop_off = distBetweenPointsSquared(end_point, drop_off_point)
            if end_to_drop_off <= end_to_pick_up:
                # Drive passed first round of filtering.

                # Filter by distance api.
                #print(filterByDistance([start_point, pick_up_point, drop_off_point, end_point]))

                # Calculate an estimated time of pick up.
                pick_up_to_drop_off_dist = distBetweenPointsSquared(pick_up_point, drop_off_point)
                start_to_end_min =  (drive.end_date_time - drive.start_date_time).seconds / 60.0
                start_to_end_dist =  start_to_pick_up + pick_up_to_drop_off_dist + end_to_drop_off
                start_to_end_straight = distBetweenPointsSquared(start_point, end_point)
                drive_min_per_deg = start_to_end_min / start_to_end_dist * (start_to_end_dist / start_to_end_straight)
                min_from_pick_up_to_end = drive_min_per_deg * (end_to_drop_off + pick_up_to_drop_off_dist)
                est_pick_up_time = drive.end_date_time - datetime.timedelta(minutes=int(min_from_pick_up_to_end))

                # Convert drive to json and add special fields.
                serializedDrive = DriveSerializer(drive).data
                serializedDrive['estimated_pick_up_date_time'] = est_pick_up_time

                # Get profile image.
                try:
                    profile_image = Profile.objects.get(user_id=drive.user_id).profile_image
                    with open(profile_image.name, "rb") as profile_image_file:
                        encoded_string = base64.b64encode(image_file.read())
                        serializedDrive['profile_image'] = encoded_string
                except:
                    print("no profile")

                filteredDrives.append(serializedDrive)

    return Response(filteredDrives, status=status.HTTP_200_OK)


def distBetweenPointsSquared (pointA, pointB):
    return sqrt((pointA[0] - pointB[0])**2 + (pointA[1] - pointB[1])**2)

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
