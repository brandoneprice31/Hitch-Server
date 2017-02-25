from rest_framework import serializers
from django.contrib.auth.models import User
from .model import Profile


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('user','profileImage')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name','email','id','username')
