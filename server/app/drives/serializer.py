from rest_framework import serializers
from .model import Drive
from ..users.serializer import UserSerializer


class DriveSerializer(serializers.ModelSerializer):

    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Drive
        fields = ('user','start_lat','start_long','start_title',
                    'start_sub_title','start_date_time','end_lat','end_long',
                    'end_title','end_sub_title','end_date_time','repeated_week_days','id')
