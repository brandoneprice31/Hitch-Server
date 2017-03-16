from rest_framework import serializers
from .model import Hitch
from ..users.serializer import UserSerializer
from ..drives.model import Drive
from ..common.fields import BytesField
from django.db.models import Q


class GetDriveFromHitchSerializer(serializers.ModelSerializer):

    driver = UserSerializer(many=False, required=False)
    polyline = BytesField()

    class Meta:
        model = Drive
        fields = ('driver', 'start_lat', 'start_long', 'start_title',
                    'start_sub_title', 'start_date_time', 'end_lat', 'end_long',
                    'end_title', 'end_sub_title', 'end_date_time','repeated_week_days',
                    'id', 'polyline', 'max_lat', 'max_long', 'min_lat', 'min_long')
        extra_kwargs = {
            'max_lat' : {'write_only' : True},
            'max_long' : {'write_only' : True},
            'min_lat' : {'write_only' : True},
            'min_long' : {'write_only' : True}
        }


class HitchSerializer(serializers.ModelSerializer):

    hitch_hiker = UserSerializer(many=False, read_only=True)
    start_to_pick_up_polyline = BytesField()
    pick_up_to_drop_off_polyline = BytesField()
    drop_off_to_end_polyline = BytesField()
    drive = GetDriveFromHitchSerializer(many=False, read_only=True)

    class Meta:
        model = Hitch
        fields = ('id','hitch_hiker','drive','adjusted_start_date_time','pick_up_lat','pick_up_long','pick_up_title','pick_up_sub_title',
                    'pick_up_date_time','drop_off_lat','drop_off_long','drop_off_title','drop_off_sub_title',
                    'drop_off_date_time','repeated_week_days','accepted','start_to_pick_up_polyline','pick_up_to_drop_off_polyline','drop_off_to_end_polyline')
        depth = 1



    def validate(self, data):

        hitch_hiker_id = self.context['hitch_hiker_id']

        # Check for week day conflicts.
        if len(data['repeated_week_days']) > 0:

            hitches = Hitch.objects.all().filter(hitch_hiker_id = hitch_hiker_id)

            for hitch in hitches:
                for week_day in data['repeated_week_days']:

                    if week_day in hitch.repeated_week_days:
                        raise serializers.ValidationError("Week day conflict.")

        # Check for day conflicts.
        else:
            query = Hitch.objects.all().filter(hitch_hiker_id = hitch_hiker_id, repeated_week_days__len = 0)
            query = query.filter(Q(pick_up_date_time__range=(data['pick_up_date_time'],data['drop_off_date_time'])) | Q(drop_off_date_time__range=(data['pick_up_date_time'],data['drop_off_date_time'])))

            if len(query) > 0:
                raise serializers.ValidationError("Date time conflict.")

        return data


    def create(self, validated_data):

        drive_id = self.context['drive_id']
        hitch_hiker_id = self.context['hitch_hiker_id']
        pick_up_lat = validated_data['pick_up_lat']
        pick_up_long = validated_data['pick_up_long']
        pick_up_title = validated_data['pick_up_title']
        pick_up_sub_title = validated_data['pick_up_sub_title']
        pick_up_date_time = validated_data['pick_up_date_time']
        drop_off_lat = validated_data['drop_off_lat']
        drop_off_long = validated_data['drop_off_long']
        drop_off_title = validated_data['drop_off_title']
        drop_off_sub_title = validated_data['drop_off_sub_title']
        drop_off_date_time = validated_data['drop_off_date_time']
        repeated_week_days = validated_data['repeated_week_days']
        start_to_pick_up_polyline = validated_data['start_to_pick_up_polyline']
        pick_up_to_drop_off_polyline = validated_data['pick_up_to_drop_off_polyline']
        drop_off_to_end_polyline = validated_data['drop_off_to_end_polyline']
        accepted = validated_data['accepted']
        adjusted_start_date_time = validated_data['adjusted_start_date_time']

        drive = Drive.objects.get(id=drive_id)
        hitch = Hitch.objects.create(drive=drive,adjusted_start_date_time=adjusted_start_date_time,accepted=accepted,hitch_hiker_id= hitch_hiker_id, pick_up_lat=pick_up_lat,
                                    pick_up_long=pick_up_long, pick_up_title=pick_up_title, pick_up_sub_title=pick_up_sub_title,
                                    pick_up_date_time=pick_up_date_time, drop_off_lat=drop_off_lat,
                                    drop_off_long=drop_off_long, drop_off_title=drop_off_title,
                                    drop_off_sub_title=drop_off_sub_title, drop_off_date_time=drop_off_date_time,
                                    repeated_week_days=repeated_week_days, start_to_pick_up_polyline=start_to_pick_up_polyline,
                                    pick_up_to_drop_off_polyline=pick_up_to_drop_off_polyline,drop_off_to_end_polyline=drop_off_to_end_polyline)

        return hitch
