from rest_framework import serializers
from .model import Drive


class DriveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Drive
        fields = ('user_id','start_lat','start_long','start_title',
                    'start_sub_title','start_date_time','end_lat','end_long',
                    'end_title','end_sub_title','end_date_time','repeated_week_days')
