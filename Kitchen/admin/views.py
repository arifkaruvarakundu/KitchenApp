from django.shortcuts import render
from rest_framework import generics
from authentication.models import User
from authentication.serializers import UserSerializer
from rest_framework.permissions import IsAdminUser
# Create your views here.


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # Only allow admin users to access this view