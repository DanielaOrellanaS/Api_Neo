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
    def create(self, request, *args, **kwargs):
        try:
            par = request.data['par']
            date = request.data['date']
            time = request.data['time']
            open = request.data['open']
            high = request.data['high']
            low = request.data['low']
            close = request.data['close']
            volume = request.data['volume']
            tablePar = Pares.objects.using('postgres').get(pares=par)
            dataInfo = Datatrader1Mtemp(par=tablePar, date=date, time=time, open=open, high=high, low=low, close=close, volume=volume)
            dataInfo.save()
            return Response({'Message':'Succesfull!!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'Message':str(e)}, status=status.HTTP_400_BAD_REQUEST)
