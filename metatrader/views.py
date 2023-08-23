from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, viewsets
from metatrader.models import *
from metatrader.serializers import *
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.urls import reverse

# Create your views here.
class ParesApiView(viewsets.ModelViewSet):
    serializer_class = ParesSerializer
    queryset = Pares.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = ParesSerializer(data=request.data)
        print('SERIALIZER: ',serializer)
        if(serializer.is_valid()):
            Pares.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'Error':'Dato no valido'}, status=status.HTTP_400_BAD_REQUEST)

class MonedaApiView(viewsets.ModelViewSet):
    serializer_class = MonedaSerializer
    queryset = Datatrader1M.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        try:
            data=eval(list(request.data)[0].replace('\0', ''))
            par = data['par']
            date = data['date']
            time = data['time']
            open = data['open']
            high = data['high']
            low = data['low']
            close = data['close']
            volume = data['volume']
            tablePar = Pares.objects.using('postgres').get(pares=par)
            dataInfo = Datatrader1M(par=tablePar, date=date, time=time, open=open, high=high, low=low, close=close, volume=volume)
            dataInfo.save()
            return Response({'Message':'Succesfull!!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'Message':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AccountTypeApiView(viewsets.ModelViewSet):
    serializer_class = AccountTypeSerializer
    queryset = AccountType.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        serializer = AccountTypeSerializer(data=request.data)
        if(serializer.is_valid()):
            AccountType.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else: 
            return Response({'Error':'Dato no valido'}, status=status.HTTP_400_BAD_REQUEST)
        
class AccountApiView(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        serializer = AccountSerializer(data=request.data)
        if(serializer.is_valid()):
            Account.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else: 
            return Response({'Error':'Dato no valido'}, status=status.HTTP_400_BAD_REQUEST)

class DetailBalanceApiView(viewsets.ModelViewSet):
    serializer_class = DetailBalanceSerializer
    queryset = DetailBalance.objects.using('postgres').all()
    
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            account_id = data['account']
            account_instance = Account.objects.using('postgres').get(id=account_id)
            date = data['date']
            time = data['time']
            balance = data['balance']
            equity = data['equity']
            freemargin = data['freemargin']
            freemarginmode = data['freemarginmode']
            fracemareq = data['fracemareq']
            flotante = data['flotante']
            operations = data['operations']
            fracflotante = data['fracflotante']

            DetailBalance.objects.using('postgres').create(
                account=account_instance,
                date=date,
                time=time,
                balance=balance,
                equity=equity,
                freemargin=freemargin,
                freemarginmode=freemarginmode,
                fracemareq=fracemareq,
                flotante=flotante,
                operations=operations,
                fracflotante=fracflotante
            )
            return Response({'Message': 'Successful!!'}, status=status.HTTP_201_CREATED)
        except Account.DoesNotExist:
            return Response({'Exception Message': 'Account does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Exception Message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
