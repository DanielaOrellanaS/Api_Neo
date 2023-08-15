from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, viewsets
from metatrader.models import *
from metatrader.serializers import *

from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.urls import reverse

# Create your views here.
class ParesApiView(viewsets.ModelViewSet):
    serializer_class = ParesSerializer
    queryset = Pares.objects.using('postgres').all()

class MonedaApiView(viewsets.ModelViewSet):
    serializer_class = MonedaSerializer
    queryset = Datatrader1Mtemp.objects.using('postgres').all()
