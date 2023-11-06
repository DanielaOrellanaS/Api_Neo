from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, viewsets
from django.contrib.auth.models import User
from authuser.serializers import *
from django.views.decorators.csrf import get_token
from django.http import JsonResponse
from dj_rest_auth.views import (LoginView,LogoutView,
                                PasswordResetView,PasswordResetConfirmView,PasswordChangeView)
from rest_framework.response import Response
#from dj_rest_auth.registration.views import VerifyEmailView
from rest_framework.decorators import api_view
from django.urls import reverse

class UserApiView(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    def create(self, request, *args, **kwargs):
        data=request.data
        user=User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        user.save()
        return Response('User create', status=status.HTTP_201_CREATED)
    
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})
