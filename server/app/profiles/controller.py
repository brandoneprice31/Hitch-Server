from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .model import Profile
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializer import ProfileSerializer
from .serializer import UserSerializer
import json


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def user_list(request):
    """
    List all snippets, or create a new snippet.
    """
    if request.method == 'GET':
        profiles = Profile.objects.all().order_by('user')
        serializer = ProfileSerializer(profiles, many=True)
        users = User.objects.all().order_by('id')
        userSerializer = UserSerializer(users,many=True)
        return Response({'profiles': serializer.data,'users': userSerializer.data},status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = json.loads(request.body)

        if 'email' in data and 'password' in data:

            try:
                user = User.objects.create_user(data['email'], data['email'], data['password'])
            except:
                return Response(status=status.HTTP_409_CONFLICT)

            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']

            user.save()

            response = {
                'id' : user.id,
                'first_name' : user.first_name,
                'last_name' : user.last_name,
                'email' : user.email,
                'token' : Token.objects.get(user=user).key
            }

            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'DELETE'])
def user_detail(request, pk):
    """
    Retrieve, update or delete a user instance.
    """
    try:
        user = User.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'DELETE':

        # Only the authorized user can delete themselves.
        if request.user.id == user.id:
            request.user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
