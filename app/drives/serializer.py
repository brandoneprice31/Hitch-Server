from rest_framework import serializers
from .model import Drive
from ..users.serializer import UserSerializer
from ..hitches.serializer import HitchSerializer
from ..common.fields import BytesField
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from ..hitches.model import Hitch


class GetHitchFromDriveSerializer(serializers.ModelSerializer):

    hitch_hiker = UserSerializer(many=False, read_only=True)
    start_to_pick_up_polyline = BytesField()
    pick_up_to_drop_off_polyline = BytesField()
    drop_off_to_end_polyline = BytesField()

    class Meta:
        model = Hitch
        fields = ('id','hitch_hiker','adjusted_start_date_time','pick_up_lat','pick_up_long','pick_up_title','pick_up_sub_title',
                    'pick_up_date_time','drop_off_lat','drop_off_long','drop_off_title','drop_off_sub_title',
                    'drop_off_date_time','repeated_week_days','accepted','start_to_pick_up_polyline','pick_up_to_drop_off_polyline','drop_off_to_end_polyline')
        depth = 1



class DriveSerializer(serializers.ModelSerializer):

    driver = UserSerializer(many=False, required=False)
    hitches = GetHitchFromDriveSerializer(many=True, read_only=True)
    polyline = BytesField()

    class Meta:
        model = Drive
        fields = ('driver', 'start_lat', 'start_long', 'start_title',
                    'start_sub_title', 'start_date_time', 'end_lat', 'end_long',
                    'end_title', 'end_sub_title', 'end_date_time','repeated_week_days',
                    'id', 'hitches', 'polyline', 'max_lat', 'max_long', 'min_lat', 'min_long')
        extra_kwargs = {
            'max_lat' : {'write_only' : True},
            'max_long' : {'write_only' : True},
            'min_lat' : {'write_only' : True},
            'min_long' : {'write_only' : True}
        }


    def validate(self, data):

        driver_id = self.context['driver_id']


        # Check for week day conflicts.
        if len(data['repeated_week_days']) > 0:

            drives = Drive.objects.all().filter(driver_id = driver_id)

            for drive in drives:
                for week_day in data['repeated_week_days']:

                    if week_day in drive.repeated_week_days:
                        raise serializers.ValidationError("Week day conflict.")

        # Check for day conflicts.
        else:
            query = Drive.objects.all().filter(driver_id = driver_id, repeated_week_days__len = 0)
            query = query.filter(Q(start_date_time__range=(data['start_date_time'],data['end_date_time'])) | Q(end_date_time__range=(data['start_date_time'],data['end_date_time'])))

            if len(query) > 0:
                raise serializers.ValidationError("Date time conflict.")

        return data


    def create(self, validated_data):

        driver_id = self.context['driver_id']
        start_lat = validated_data['start_lat']
        start_long = validated_data['start_long']
        start_title = validated_data['start_title']
        start_sub_title = validated_data['start_sub_title']
        start_date_time = validated_data['start_date_time']
        end_lat = validated_data['end_lat']
        end_long = validated_data['end_long']
        end_title = validated_data['end_title']
        end_sub_title = validated_data['end_sub_title']
        end_date_time = validated_data['end_date_time']
        repeated_week_days = validated_data['repeated_week_days']
        max_lat = validated_data['max_lat']
        max_long = validated_data['max_long']
        min_lat = validated_data['min_lat']
        min_long = validated_data['min_long']
        polyline = validated_data['polyline']


        drive = Drive.objects.create(driver_id= driver_id, start_lat=start_lat,
                                    start_long=start_long, start_title=start_title,
                                    start_date_time=start_date_time, end_lat=end_lat,
                                    end_long=end_long, end_title=end_title,
                                    end_sub_title=end_sub_title, end_date_time=end_date_time,
                                    repeated_week_days=repeated_week_days, max_lat=max_lat,
                                    max_long=max_long, min_lat=min_lat, min_long=min_long, polyline=polyline)

        return drive
