from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..profiles.model import Profile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializer import UserSerializer
import json

from django.core.files.base import ContentFile
import base64

@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def user_list(request):


    # GET
    if request.method == 'GET':

        # Get all users, order them by id, and return their json.
        users = User.objects.all().order_by('id')
        userSerializer = UserSerializer(users,many=True)
        return Response(userSerializer.data,status=status.HTTP_200_OK)


    # POST
    elif request.method == 'POST':
        data = json.loads(request.body)

        if 'email' in data and 'password' not in data:
            # Check if the email exists and return either conflict or not found.
            if User.objects.filter(username=data['email']).exists():
                return Response(status=status.HTTP_409_CONFLICT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        elif 'email' in data and 'password' in data and len(data.keys()) > 2:
            # Try creating the user and storing his information.
            try:
                user = User.objects.create_user(data['email'], data['email'], data['password'])
            except:
                return Response(status=status.HTTP_409_CONFLICT)

            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']

            # Save the user and return his info plus token.
            user.save()

            # Get the user's profile and save new information.
            profile = Profile.objects.get(user=user)

            if 'profile_image' in data:
                imageFile = ContentFile(base64.b64decode(data['profile_image']))
                profile.profile_image.save(str(profile.id) + "/profile_image.png", imageFile)

            profile.save()

            jsonResponse = {
                'id' : user.id,
                'first_name' : user.first_name,
                'last_name' : user.last_name,
                'email' : user.email,
                'token' : Token.objects.get(user=user).key
            }

            return Response(jsonResponse, status=status.HTTP_201_CREATED)

        elif 'email' in data and 'password' in data:

            # Login the user if the provided information is valid.
            try:
                user = User.objects.get(email=data['email'])
            except:
                return Response(status=status.HTTP_404_NOT_FOUND)

            if user.check_password(data['password']):

                # Get the user's profile and save new information.
                profile = Profile.objects.get(user=user)

                with open(profile.profile_image.name, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read())

                response = {
                    'id' : user.id,
                    'first_name' : user.first_name,
                    'last_name' : user.last_name,
                    'email' : user.email,
                    'token' : Token.objects.get_or_create(user=user)[0].key,
                    'profile_image' : encoded_string
                }

                return Response(response, status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

        else:
            # this is a bad request.
            return Response(status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'DELETE'])
def user_detail(request, pk):

    try:
        user = User.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


    # GET
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)



    # DELETE
    elif request.method == 'DELETE':

        # Only the authorized user can delete themselves.
        if request.user.id == user.id:
            request.user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
def log_out(request):

    # Only users with tokens can log out.
    if request.user.is_anonymous():
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        request.user.auth_token.delete()
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_200_OK)
