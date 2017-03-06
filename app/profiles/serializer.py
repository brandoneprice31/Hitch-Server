from rest_framework import serializers
from .model import Profile


class ProfileSerializer(serializers.Serializer):

    class Meta:
        model = Profile
        fields = ('profile_image')
