from rest_framework import serializers
from .model import Hitch
from ..drives.serializer import DriveSerializer
from ..users.serializer import UserSerializer


class HitchSerializer(serializers.ModelSerializer):

    user = UserSerializer(many=False, read_only=True)
    drive = DriveSerializer(many=False, read_only=True, required=False)

    class Meta:
        model = Hitch
        fields = ('drive','user','pick_up_lat','pick_up_long','pick_up_title','pick_up_sub_title',
                    'pick_up_date_time','drop_off_lat','drop_off_long','drop_off_title','drop_off_sub_title',
                    'drop_off_date_time','repeateded_week_days','accepted','start_to_pick_up_polyline',
                    'pick_up_to_drop_off_polyline','drop_off_to_end_polyline')
