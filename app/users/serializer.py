from rest_framework import serializers
from django.contrib.auth.models import User
from ..profiles.serializer import ProfileSerializer

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name','last_name','email','id','username')
