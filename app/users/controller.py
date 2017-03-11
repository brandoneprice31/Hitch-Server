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





# Returns all of the users.:
# 200 - all users returned.
@api_view(['GET'])
@permission_classes((AllowAny,))
def list_all(request):

    # Get all users.
    users = User.objects.all().order_by('id')
    userSerializer = UserSerializer(users,many=True)
    return Response(userSerializer.data,status=status.HTTP_200_OK)




# Creates user:
# 201 - user created
# 400 - incorrect credentials provided.
@api_view(['POST'])
@permission_classes((AllowAny,))
def create(request):

    # User is trying to be created.
    data = json.loads(request.body)
    userSerializer = UserSerializer(data=data)

    if userSerializer.is_valid():
        # Save the user and get that damn token.
        userSerializer.save()
        response = userSerializer.data
        response['token'] = Token.objects.get_or_create(user_id=response['id'])[0].key
        return Response(response, status=status.HTTP_201_CREATED)
    else:
        return Response(userSerializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Updates user:
# 200 - user updated
# 401 - un-authorized.
# 400 - bad request.
@api_view(['POST'])
def update(request):

    if request.user.is_anonymous():
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    # User is trying to be updated.
    data = json.loads(request.body)

    userSerializer = UserSerializer(request.user, data=data, partial=True)

    if userSerializer.is_valid():
        userSerializer.save()
        return Response(userSerializer.data, status=status.HTTP_200_OK)
    else:
        Response(status=status.HTTP_400_BAD_REQUEST)


# Checks if the user exists:
# 409 - user does exist.
# 404 - user doesn't exist.
# 400 - no email provided.
@api_view(['POST'])
@permission_classes((AllowAny,))
def check_user(request):

    data = json.loads(request.body)

    if 'email' in data:
        # Check if the email exists and return either conflict or not found.
        if User.objects.filter(email=data['email']).exists():
            return Response(status=status.HTTP_409_CONFLICT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)





# Logs in the user:
# 404 - user doesn't exist
# 202 - user logged in successfully
# 406 - wrong password
# 400 - no email provided
@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):

    data = json.loads(request.body)

    if 'email' in data and 'password' in data:
        # Login the user if the provided information is valid.
        try:
            user = User.objects.get(email=data['email'])
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Check the password provided.
        if user.check_password(data['password']):

            # Return object information and password.
            userSerializer = UserSerializer(user)
            response = userSerializer.data
            response['token'] = Token.objects.get_or_create(user=user)[0].key
            response['email'] = data['email']
            return Response(response, status=status.HTTP_202_ACCEPTED)

        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        # this is a bad request.
        return Response(status=status.HTTP_400_BAD_REQUEST)




# Gets single user information.
# 404 - user doesn't exist.
# 200 - got user's information.
# 400 - didn't provide user's id.
@permission_classes((AllowAny,))
@api_view(['POST'])
def detail(request):

    data = json.loads(request.body)

    if 'id' in data:
        try:
            user = User.objects.get(pk=data['id'])

            # Get user.
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)






# Deletes a single user.
# 401 - user isn't authorized.
# 204 - user has been deleted.
@api_view(['DELETE'])
def delete(request):
        # Only the authorized user can delete themselves.
        if request.user.is_anonymous():
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






# Gets single user information.
# 401 - didn't provide a token.
# 200 - successfully logged out the user.
# 400 - user isn't logged in.
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
