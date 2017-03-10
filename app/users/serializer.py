from rest_framework import serializers
from django.contrib.auth.models import User
from ..profiles.serializer import ProfileSerializer
from ..profiles.model import Profile
from ..common.fields import BytesField

class UserSerializer(serializers.ModelSerializer):

    profile_image = BytesField(source = 'profile.profile_image', required = False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_image', 'password','id')
        extra_kwargs = {
            'password' : {  'write_only' : True,
                            'required' : False },
            'email' :    {  'write_only' : True,
                            'required' : False }
        }

    def validate(self,data):

        if 'email' in data and User.objects.filter(email = data['email']):
            raise serializers.ValidationError("Email not unique.")

        return data

    def create(self, validated_data):

        user =  User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )

        if 'profile' in validated_data:
            user.profile.profile_image = validated_data['profile']['profile_image']
            user.profile.save()

        return user

    def update(self, instance, validated_data):

        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']
        if 'profile' in validated_data:
            instance.profile.profile_image = validated_data['profile']['profile_image']

        instance.save()
        instance.profile.save()
        return instance
