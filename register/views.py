from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from rest_framework import  permissions


class CustomObtainAuthToken(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        
        """Iniciar sesion
        
        Se necesita el email, pero por alguna razon que no voy a ver ahorita, tienes que pasar el campo del email 
        con el nombre del username, es decir:
        
        username: ejemplode@email.com

        Returns:
            _type_: _description_
        """

        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token:Token = Token.objects.get(key=response.data['token'])


        return Response(
            {
                'token': token.key, 
                'name': token.user.get_full_name(),
                'role': token.user.role,
                'id': token.user.id,
            })

from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model # If used custom user model

from .serializers import CreateUserSerializer


class CreateUserView(CreateAPIView):

    model = get_user_model()
    permission_classes = [
        permissions.AllowAny # Or anon users can't register
    ]
   
    serializer_class = CreateUserSerializer
