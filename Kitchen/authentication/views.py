from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .models import User
from django.contrib.auth import authenticate
# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response(
                {'token' : token, 'email' : user.email, 'msg' : 'Registration Success' },
                status = status.HTTP_201_CREATED
            )
        
        else:
            print("validation error:", serializer.errors)
            return Response(
                {"errors" : serializer.errors},
                status = status.HTTP_400_BAD_REQUEST
            )

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        print("email:", type(email))
        print("password:", type(password))  

        user = authenticate(email=email, password=password)

        if user is not None:
            profile_img_url = user.profile_img.url if user.profile_img else None
            token = get_tokens_for_user(user)

            return Response({
                'token': token,
                'msg': 'Login Success',
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'profile_img': profile_img_url,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'errors': {'non_field_errors': ['Email or Password is not valid']}
            }, status=status.HTTP_401_UNAUTHORIZED)



        



        