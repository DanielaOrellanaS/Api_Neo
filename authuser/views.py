from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from authuser.serializers import *
from dj_rest_auth.views import (LoginView,LogoutView,
                                PasswordResetView,PasswordResetConfirmView,PasswordChangeView)
from rest_framework.response import Response
#from dj_rest_auth.registration.views import VerifyEmailView
from rest_framework.decorators import api_view
from django.urls import reverse

# Create your views here.
class UserApiView(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()