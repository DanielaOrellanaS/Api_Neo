from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, viewsets
from metatrader.models import *
from metatrader.serializers import *
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

class ParesApiView(viewsets.ModelViewSet):
    serializer_class = ParesSerializer
    queryset = Pares.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        serializer = ParesSerializer(data=request.data)
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

#@csrf_exempt
class DetailBalanceAccountApiView(viewsets.ModelViewSet):
    serializer_class = DetailBalanceSerializer
    queryset = DetailBalance.objects.using('postgres').all()
    
    def list(self, request, *args, **kwargs):
        account_id = self.request.query_params.get('account_id', None)
        if account_id is not None:
            resultado = list(DetailBalance.objects.using('postgres').filter(account_id=account_id).order_by('id').values())
            if len(resultado) > 0:
                data_ser = resultado[-1]
                print('DetailBalance list success:', data_ser)  # Agregado para imprimir en la consola
                return Response(data_ser, status=status.HTTP_200_OK)
            else:
                print('Error: No existe la cuenta buscada')  # Agregado para imprimir en la consola
                return Response({'Error': 'No existe la cuenta buscada'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print('Error: No se proporcionó el parámetro account_id')  # Agregado para imprimir en la consola
            return Response({'Error': 'No se proporcionó el parámetro account_id'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            #data = request.data
            data=eval(list(request.data)[0].replace('\0', ''))
            account_id = data.get('account_id')
            account_instance = Account.objects.using('postgres').filter(id=account_id).first()

            if account_instance is None:
                return Response({'Exception Message': 'Account does not exist'}, status=status.HTTP_404_NOT_FOUND)
            else:
                date = data.get('date')
                time = data.get('time')
                balance = data.get('balance')
                equity = data.get('equity')
                freemargin = data.get('freemargin')
                freemarginmode = data.get('freemarginmode')
                fracemareq = data.get('fracemareq')
                flotante = data.get('flotante')
                operations = data.get('operations')
                fracflotante = data.get('fracflotante')
    
                detail_balance = DetailBalance.objects.using('postgres').create(
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
                detail_balance.save()
    
                return Response({'Message': 'Successful!!'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'Exception Message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


#@csrf_exempt
class OperationApiView(viewsets.ModelViewSet):
    serializer_class = OperationSerializer
    queryset = Operation.objects.using('postgres').all()
    
    def create(self, request, *args, **kwargs): 
        try: 
            data = eval(list(request.data)[0].replace('\0', ''))
            account_id = data.get('account_id')
            account_instance = Account.objects.using('postgres').filter(id=account_id).first()
            
            if account_instance is None: 
                return Response({'Exception Message': 'Account does not exist'}, status=status.HTTP_404_NOT_FOUND)
            
            date = data.get('date')
            ticket = data.get('ticket')
            symbol = data.get('symbol')
            lotes = data.get('lotes')
            operationType = data.get('type')
            dateOpen = data.get('dateOpen')
            dateClose = data.get('dateClose')
            openPrice = data.get('openPrice')
            closePrice = data.get('closePrice')
            magic = data.get('magic')
            sl = data.get('sl')
            tp = data.get('tp')
            profit = data.get('profit')
            
            # Buscar la operación existente por el ticket
            operation = Operation.objects.using('postgres').filter(ticket=ticket).first()
            
            if operation is None:
                # Crear la operación
                operation = Operation(
                    date=date,
                    ticket=ticket,
                    account=account_instance,
                    symbol=symbol, 
                    lotes=lotes, 
                    operationType=operationType,
                    dateOpen=dateOpen,
                    dateClose=dateClose,
                    openPrice=openPrice,
                    closePrice=closePrice,
                    magic=magic,
                    sl=sl,
                    tp=tp,
                    profit=profit
                )
            else:
                # Actualizar la operacion 
                operation.lotes = lotes
                operation.dateOpen = dateOpen
                operation.dateClose = dateClose
                operation.openPrice = openPrice
                operation.closePrice = closePrice
                operation.magic = magic
                operation.sl = sl
                operation.tp = tp
                operation.profit = profit
            
            operation.save()
            
            return Response({'Message': 'Successful!!'}, status=status.HTTP_201_CREATED)
        
        except Exception as e: 
             return Response({'Exception Message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class robot_neoApiView(viewsets.ModelViewSet):
    serializer_class = IndicadorSerializer
    queryset = ResumeIndicador.objects.using('postgres').all()

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            ind = ResumeIndicador.objects.using('postgres').create(par_id=data['par'],date=data['date'],pc1=data['pc1'], time_frame=data['time_frame'])
            return Response('Success!!',status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request, *args, **kwargs):
        try:
            try:
                data = eval(list(request.data)[0].replace('\0', ''))
            except:
                data = request.data
           
            par_buscado = Pares.objects.using('postgres').get(pares=data['par'])

            resultado = list(ResumeIndicador.objects.using('postgres').filter(par=par_buscado.pk, time_frame=data['time_frame']).order_by('id').values())
            if len(resultado)>0:
                data_ser = resultado[-1]
                return Response({'PC1_{}'.format(data['par']):data_ser['pc1']}, status=status.HTTP_200_OK)
            else:
                return Response({'Error':'No existe el dato buscado'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)