from django.shortcuts import render
from django.db.models import Count, Max, Subquery
from datetime import datetime, timedelta, timezone
from rest_framework import status, viewsets
from metatrader.models import *
from django.utils import timezone
from django.utils.dateparse import parse_date
from metatrader.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import requests
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.exceptions import NotFound
from django.db import connections
from django.http import JsonResponse
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.http import HttpResponse
from django.utils.encoding import smart_str
from datetime import datetime
import os
from django.conf import settings

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
                print('DetailBalance list success:', data_ser)  
                return Response(data_ser, status=status.HTTP_200_OK)
            else:
                print('Error: No existe la cuenta buscada') 
                return Response({'Error': 'No existe la cuenta buscada'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print('Error: No se proporcionó el parámetro account_id') 
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



### DETAILS ACCOUNTS ###

#-----------------------------------------------------------------------------------------

class ResumeDetailBalanceApiView(viewsets.ModelViewSet):
    serializer_class = DetailBalanceSerializer
    queryset = DetailBalance.objects.using('postgres').all()

    def list(self, request):
        account_ids_param = request.query_params.get('account_id')
        if account_ids_param:
            account_ids = [int(id) for id in account_ids_param.split(',')]
            #DESC
            detail_balances = DetailBalance.objects.using('postgres').filter(account_id__in=account_ids).order_by('account_id', '-date', '-time')
            accounts_info = (
                Account.objects.using('postgres')
                .filter(id__in=account_ids)
                .order_by('group')
                .values('id', 'alias', 'accountType', 'group')
            )
            
            response_data = []
            for account_id in account_ids:
                #Fecha metatrader 
                current_date = datetime.now()+timedelta(hours=2)
                #Balance actual (Ultimo balance)
                latest_balance = detail_balances.filter(account_id=account_id).first()
                alias = next((acc['alias'] for acc in accounts_info if acc['id'] == account_id), None)
                balance_formatted = format(latest_balance.balance, ',.4f') if latest_balance.balance is not None else None
                flotante_formatted = format(latest_balance.flotante, ',.4f') if latest_balance.flotante is not None else None
                float_percent = round((latest_balance.flotante / latest_balance.balance) * 100, 4) if latest_balance.balance != 0 else 0
                        
                if latest_balance.date == current_date.date():
                    if latest_balance:
                        #Balance inicial 
                        first_balance = DetailBalance.objects.using('postgres').filter(
                            account_id=account_id, date=latest_balance.date).order_by('time')

                        if first_balance.exists():
                            balance_percent = round(((latest_balance.balance - first_balance[0].balance) / first_balance[0].balance) * 100, 4)
                        else: 
                            balance_percent = 0 
                        
                        # Calcular el balance inicial del mes
                        first_day_of_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                        first_balance_month = DetailBalance.objects.using('postgres').filter(
                            account_id=account_id, 
                            date__range=[first_day_of_month.date(), current_date.date()]
                        ).order_by('date', 'time').first()

                        if first_balance_month:
                            # Calcular el porcentaje mensual del balance
                            month_balance_percent = round(((latest_balance.balance - first_balance_month.balance) / first_balance_month.balance) * 100, 4)
                        else:
                            month_balance_percent = 0

                        data = {
                            'balance': balance_formatted,
                            'flotante': flotante_formatted,
                            'percentage': float_percent,
                            'balance_percent': balance_percent,
                            'month_balance_percent': month_balance_percent,  
                            'account_id': account_id,
                            'alias': alias,
                        }

                else: 
                    data = {
                            'balance': balance_formatted,
                            'flotante': flotante_formatted,
                            'percentage': float_percent,
                            'balance_percent': 0,
                            'month_balance_percent': 0,  # Nuevo campo agregado
                            'account_id': account_id,
                            'alias': alias,
                        }
                response_data.append(data)
                
            sorted_response_data = sorted(response_data, key=lambda x: x.get('alias', '').lower())
            return Response(sorted_response_data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'No se proporcionaron parámetros account_id'}, status=status.HTTP_400_BAD_REQUEST)

class AllDetailBalanceApiView(viewsets.ModelViewSet):
    serializer_class = OperationSerializer

    def list(self, request, *args, **kwargs):
        account_id = request.query_params.get('account_id')
        if account_id is not None:
            now = timezone.now()
            start_date = (now - timedelta(hours=8)).date()
            end_date = (now + timedelta(hours=8)).date()

            # Operaciones abiertas
            open_operations = Operation.objects.using('postgres').filter(
                account_id=account_id,
                dateClose='1970-01-01T00:00:00Z',
                dateOpen__date__range=[start_date, end_date]
            ).order_by('-dateOpen')

            # Operaciones cerradas
            closed_operations = Operation.objects.using('postgres').filter(
                account_id=account_id
            ).exclude(dateClose='1970-01-01T00:00:00Z').filter(
                dateClose__date__range=[start_date, end_date]
            ).order_by('-dateClose')

            open_serializer = OperationSerializer(open_operations, many=True)
            closed_serializer = OperationSerializer(closed_operations, many=True)

            latest_detail_balance = DetailBalance.objects.using('postgres').filter(account_id=account_id).order_by('-date', '-time').first()
            day_gain = self.get_day_gain(account_id)

            response_data = {
                'balance': format(latest_detail_balance.balance if latest_detail_balance else None, ',.4f'),
                'flotante': format(latest_detail_balance.flotante if latest_detail_balance else None, ',.4f'),
                'equity': format(latest_detail_balance.equity if latest_detail_balance else None, ',.4f'),
                'gain': format(day_gain, ',.2f'),
                'num_operations': open_operations.count() + closed_operations.count(),
                'colas': self.get_operations_by_symbol(account_id),
                'open_operations': open_serializer.data,
                'closed_operations': closed_serializer.data,
            }

            balance_value = latest_detail_balance.balance if latest_detail_balance else 0
            flotante_value = latest_detail_balance.flotante if latest_detail_balance else 0
            if flotante_value != 0:
                percentage = (balance_value / flotante_value) * 100
                response_data['percentage'] = round(percentage, 2)
            else:
                response_data['percentage'] = None

            self.format_operations(response_data['open_operations'])
            self.format_operations(response_data['closed_operations'])

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'No se proporcionó el parámetro account_id'}, status=status.HTTP_400_BAD_REQUEST)

    def format_operations(self, operations):
        for operation in operations:
            operation['dateOpen'] = timezone.datetime.strptime(operation['dateOpen'], "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d %H:%M:%S')
            operation['dateClose'] = timezone.datetime.strptime(operation['dateClose'], "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d %H:%M:%S')
            operation['date'] = timezone.datetime.strptime(operation['date'], "%Y-%m-%dT%H:%M:%SZ").strftime('%Y-%m-%d %H:%M:%S')
            for key in ['lotes', 'openPrice', 'closePrice', 'sl', 'tp', 'profit']:
                operation[key] = format(operation[key], ',.4f') if isinstance(operation[key], float) else operation[key]

    def get_day_gain(self, account_id):
        detail_balances = DetailBalance.objects.using('postgres').filter(account_id=account_id).order_by('-date', '-time')
        latest_balance = detail_balances.first()
        current_date = timezone.now().date()

        if latest_balance:
            first_balance = DetailBalance.objects.using('postgres').filter(
                account_id=account_id, date=latest_balance.date
            ).order_by('time').first()
            if first_balance:
                gain = latest_balance.balance - first_balance.balance
                return gain
        return 0

    def get_operations_by_symbol(self, account_id=None):
        if account_id is None:
            account_ids = Account.objects.using('postgres').values_list('id', flat=True)
            operations_count_by_account = {}
            for acc_id in account_ids:
                operations_for_account = (
                    Operation.objects.using('postgres')
                    .filter(account_id=acc_id, dateClose='1970-01-01 00:00:00')
                    .values('symbol')
                    .annotate(open_operations=Count('id'))
                )
                operations_count_by_account[acc_id] = list(operations_for_account)
            return operations_count_by_account
        else:
            operations_for_account = (
                Operation.objects.using('postgres')
                .filter(account_id=account_id, dateClose='1970-01-01 00:00:00')
                .values('symbol')
                .annotate(open_operations=Count('id'))
            )
            return list(operations_for_account)
        
#-----------------------------------------------------------------------------------------

### OPERATIONS ###

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
            type = data.get('type')
            dateOpen = data.get('dateOpen')
            dateClose = data.get('dateClose')
            openPrice = data.get('openPrice')
            closePrice = data.get('closePrice')
            magic = data.get('magic')
            sl = data.get('sl')
            tp = data.get('tp')
            profit = data.get('profit')
            operation = Operation.objects.using('postgres').filter(ticket=ticket).first()
            
            if operation is None:
                # Crear la operación
                operation = Operation(
                    date=date,
                    ticket=ticket,
                    account=account_instance,
                    symbol=symbol, 
                    lotes=lotes, 
                    type=type,
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
                fecha = data_ser['date']
                fecha_server = datetime.now()+timedelta(hours=2)
                fecha2_server = datetime.fromisoformat(str(fecha_server)).replace(tzinfo=timezone.utc)
                
                if fecha>=fecha2_server-timedelta(hours=3):
                    return Response({'PC1_{}'.format(data['par']):data_ser['pc1']}, status=status.HTTP_200_OK)
                else:
                    return Response({'Datos no actualizados de par {}, se devuelve indicador neutro: '.format(data['par']):0,
                                     'Hora api':str(datetime.now())}, status=status.HTTP_200_OK)
            else:
                return Response({'Error':'No existe el dato buscado'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        

class LastIndicatorApiView(viewsets.ModelViewSet):
    serializer_class = IndicadorSerializer

    def get_queryset(self):
        # Timeframe 5
        last_indicators_5 = (
            ResumeIndicador.objects.using('postgres')
            .filter(time_frame=5)
            .values('par')
            .annotate(last_id=Max('id'))
            .values('last_id')
        )

        indicators_data_5 = (
            ResumeIndicador.objects.using('postgres')
            .filter(id__in=last_indicators_5)
        )

        # Timeframe 15
        last_indicators_15 = (
            ResumeIndicador.objects.using('postgres')
            .filter(time_frame=15)
            .values('par')
            .annotate(last_id=Max('id'))
            .values('last_id')
        )

        indicators_data_15 = (
            ResumeIndicador.objects.using('postgres')
            .filter(id__in=last_indicators_15)
        )

        return indicators_data_5.union(indicators_data_15)

class UserFavAccountsApiView(viewsets.ModelViewSet): 
    serializer_class = UserFavAccountsSerializer
    queryset = UserFavAccounts.objects.using('postgres').all()

    def list(self, request, *args, **kwargs):
        user = request.query_params.get('user', None)
        if user:
            user_accounts = UserFavAccounts.objects.using('postgres').filter(user=user)
            serializer = self.get_serializer(user_accounts, many=True)
            return Response(serializer.data)
        else:
            return Response({'Error':'Usuario no proporcionado'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = UserFavAccountsSerializer(data=request.data)
        if serializer.is_valid():
            UserFavAccounts.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else: 
            return Response({'Error':'Dato no válido'}, status=status.HTTP_400_BAD_REQUEST)

class EventsApiView(viewsets.ModelViewSet):
    serializer_class = EventsSerializer
    queryset = Events.objects.using('postgres').all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        date_param = self.request.query_params.get('fecha', None)
        
        if date_param:
            parsed_date = parse_date(date_param)
            if parsed_date:
                queryset = queryset.filter(fecha=parsed_date)
        
        if not date_param:
            return queryset.order_by('fecha', 'hora')

        return queryset.order_by('-fecha', '-hora')
    
    
class ParMonedaApiView(viewsets.ModelViewSet): 
    serializer_class = ParMonedaSerializer
    queryset = ParMoneda.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        serializer = ParMonedaSerializer(data=request.data)
        if(serializer.is_valid()):
            ParMoneda.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else: 
            return Response({'Error':'Dato no valido'}, status=status.HTTP_400_BAD_REQUEST)

class PipsApiView(viewsets.ModelViewSet): 
    serializer_class = PipsSerializer
    queryset = Pips.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        serializer = PipsSerializer(data=request.data)
        if(serializer.is_valid()):
            Pips.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else: 
            return Response({'Error':'Dato no valido'}, status=status.HTTP_400_BAD_REQUEST)

class rangos_neoApiView(viewsets.ModelViewSet):
    serializer_class = RangosSerializer
    queryset = CortesIndicador.objects.using('postgres').all()

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            ind = CortesIndicador.objects.using('postgres').create(par_id=data['par'],date=data['date'],
                                                                   corte_buy=data['corte_buy'],corte_sell=data['corte_sell'],
                                                                   time_frame=data['time_frame'])
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

            resultado = list(CortesIndicador.objects.using('postgres').filter(par=par_buscado.pk, time_frame=data['time_frame']).order_by('id').values())
            if len(resultado)>0:
                data_ser = resultado[-1]
                return Response({'Corte_buy_{}'.format(data['par']):data_ser['corte_buy'],
                                 'Corte_sell_{}'.format(data['par']):data_ser['corte_sell']}, status=status.HTTP_200_OK)
            else:
                return Response({'Error':'No existe los rangos buscados'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        
class AlertEventsApiView(viewsets.ModelViewSet):
    serializer_class = AlertEventsSerializer
    queryset = AlertEvents.objects.using('postgres').all()

    def list(self, request, *args, **kwargs):
        try:
            par_name = request.GET.get('par', None)
            fecha_inicio_str = request.GET.get('fecha_inicio', None)
            fecha_fin_str = request.GET.get('fecha_fin', None)
            print("Datos: ", par_name, fecha_inicio_str, fecha_fin_str)
            if not all([par_name, fecha_inicio_str, fecha_fin_str]):
                data = request.data
                par_name = data.get('par', None) or par_name
                fecha_inicio_str = data.get('fecha_inicio', None) or fecha_inicio_str
                fecha_fin_str = data.get('fecha_fin', None) or fecha_fin_str

            if not all([par_name, fecha_inicio_str, fecha_fin_str]):
                return Response({'error': 'Parámetros incompletos'}, status=status.HTTP_400_BAD_REQUEST)

            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            queryset = AlertEvents.objects.using('postgres').filter(
                par_name=par_name, 
                fecha__range=(fecha_inicio, fecha_fin)
            ).order_by('-fecha')
            
            if not queryset.exists():
                return Response({'error': 'No hay datos para la consulta'}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(queryset, many=True)

            response_data = {
                'alerts': serializer.data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class DeviceTokenApiView(viewsets.ModelViewSet):
    serializer_class = DeviceTokenSerializer
    queryset = DeviceToken.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        serializer = DeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            token = serializer.validated_data.get('token')
            existing_token = DeviceToken.objects.using('postgres').filter(user=user).first()
            if existing_token:
                existing_token.token = token
                existing_token.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Variacion Pips
class robot_neopipsApiView(viewsets.ModelViewSet):
    serializer_class = VariacionPipsSerializer
    queryset = variacion_pips_estimacion.objects.using('postgres').all()

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            ind = variacion_pips_estimacion.objects.using('postgres').create(par_id=data['par'],
                                                                             date=data['date'],
                                                                             variacion=data['variacion'],
                                                                             inferior=data['limite_inferior'],
                                                                             superior=data['limite_superior'],
                                                                             time_frame=data['time_frame'])
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

            resultado = list(variacion_pips_estimacion.objects.using('postgres').filter(par=par_buscado.pk).order_by('id').values())
            if len(resultado)>0:
                data_ser = resultado[-1]
                fecha = data_ser['date']
                fecha_server = datetime.now()+timedelta(hours=2)
                fecha2_server = datetime.fromisoformat(str(fecha_server)).replace(tzinfo=timezone.utc)
                
                if fecha>=fecha2_server-timedelta(hours=1):
                    return Response({'variacion_{}'.format(data['par']):data_ser['variacion'],
                                     'Limite_inferior_{}'.format(data['par']):data_ser['inferior'],
                                     'Limite_superior_{}'.format(data['par']):data_ser['superior']}, status=status.HTTP_200_OK)
                else:
                    return Response({'Datos no actualizados de par {}, se devuelve variacion neutra: '.format(data['par']):0,
                                     'Hora api':str(datetime.now())}, status=status.HTTP_200_OK)
            else:
                return Response({'Error':'No existe el dato buscado'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
       
#FUNCIONAL
class SentNotificationAllDevices(viewsets.ModelViewSet):
    serializer_class = ParesSerializer
    queryset = Pares.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        access_token = self._get_access_token()
        authorization_header = f"Bearer {access_token}"
        url = "https://fcm.googleapis.com/v1/projects/app-trading-notifications/messages:send"
        tokens_data_device = requests.get("https://tradinapi.azurewebsites.net/token/").json()
        
        serializer = ParesSerializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data.get('id')
            body = serializer.validated_data.get('pares')
            success_count = 0
            error_count = 0
            for token_info in tokens_data_device:
                token_device = token_info.get("token")
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": authorization_header
                }
                data = {
                    "message": {
                        "notification": {
                            "title": "ALERTA!",
                            "body": body
                        },
                        "token": token_device
                    }
                }
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1
                    print(f"Error al enviar la notificación a FCM para el token {token_device}. Detalles: {response.text}")

            if error_count == 0:
                return Response({"message": f"La notificacion ({id}, {body}) se envio exitosamente."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": f"Se enviaron {success_count} notificaciones exitosamente, pero ocurrieron errores al enviar {error_count} notificaciones. Por favor, revisa los registros del servidor para más detalles."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"message": "Error en los datos del JSON recibido."}, status=status.HTTP_400_BAD_REQUEST)
    def _get_access_token(self):  
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-file.json', scopes=['https://www.googleapis.com/auth/cloud-platform'])
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token
    
class NotificationApiView(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.using('postgres').all()

    def create(self, request, *args, **kwargs):
        #serializer = NotificationSerializer(data=request.data)
        if b'\0' in request.body:
            data = eval(list(request.data)[0].replace('\0', ''))
            serializer = NotificationSerializer(data=data)
        else:
            serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            access_token = self._get_access_token()
            authorization_header = f"Bearer {access_token}"
            url = "https://fcm.googleapis.com/v1/projects/app-trading-notifications/messages:send"
            tokens_data_device = self._get_device_token(user=request.data.get("user"))
            if not tokens_data_device: 
                raise NotFound(detail="Usuario no encontrado", code=404)
            for token_info in tokens_data_device:
                token_device = token_info.get("token")
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": authorization_header
                }
                data = {
                    "message": {
                        "notification": {
                            "title": request.data.get("title"),
                            "body": request.data.get("body")
                        },
                        "token": token_device
                    }
                }
                print('ENVIO SOLICITUD: ', request.data)
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 200:
                    Notification.objects.using('postgres').create(**serializer.validated_data)
                else:
                    error_message = {'Error al enviar la notificacion': response.text}
                    return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
            return Response({'Notificacion enviada correctamente!': serializer.data}, status=status.HTTP_201_CREATED)
        else: 
            return Response({'Error': 'Datos no válidos', 'Detalles': serializer.errors, 'Envio' : request.data}, status=status.HTTP_400_BAD_REQUEST)
    def _get_access_token(self):  
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-file.json', scopes=['https://www.googleapis.com/auth/cloud-platform'])
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token
    def _get_device_token(self, user=None):
        tokens_endpoint = "https://tradinapi.azurewebsites.net/token/"
        # TODOS
        if user is None or user.lower() == "all":
            return requests.get(tokens_endpoint).json()
        # Personalizado
        else:
            tokens_url = f"{tokens_endpoint}?user={user}"
            return requests.get(tokens_url).json()

#CALL FUNCTION DISPATCHER 
@api_view(['GET'])
def dispatcher_view(request):
    if request.method == 'GET':
        entrada = request.query_params.get('entrada', '')

        if not entrada:
            return Response({'Error':'Entrada no proporcionada'}, status=status.HTTP_400_BAD_REQUEST)
        resultado = _call_dispatcher(entrada)
        return JsonResponse({'resultado': resultado})

    else:
        return Response({'Error':'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

logger = logging.getLogger(__name__)
def _call_dispatcher(entrada):
    with connections['postgres'].cursor() as cursor: 
        sql = "SELECT dispatcher(%s)"
        logger.info(f"Ejecutando SQL: {sql} con entrada: {entrada}")

        cursor.execute(sql, [entrada])
        resultado = cursor.fetchone()[0]
        logger.info(f"Resultado obtenido: {resultado}")

    return resultado

class TendenciaApiView(viewsets.ModelViewSet):
    serializer_class = TendenciaSerializer
    queryset = Tendencia.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        serializer = TendenciaSerializer(data=request.data)
        if(serializer.is_valid()):
            Tendencia.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'Error':'Dato no valido'}, status=status.HTTP_400_BAD_REQUEST)

class ResultFilesApiView(viewsets.ModelViewSet):
    serializer_class = ResultFilesSerializer
    queryset = ResultFiles.objects.using('postgres').all()
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        file = request.data.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        name_file = file.name
        date_upload = datetime.now()

        serializer = ResultFilesSerializer(data={'nameFile': name_file, 'dateUpload': date_upload, 'fileUpload': file})
        if serializer.is_valid():
            ResultFiles.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def list_files(self, request):
        try:
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            if not os.path.exists(upload_dir):
                return Response({"error": "Upload directory not found"}, status=status.HTTP_404_NOT_FOUND)

            files = os.listdir(upload_dir)
            file_list = [{"nameFile": file, "path": os.path.join(settings.MEDIA_URL, 'uploads', file)} for file in files]
            return JsonResponse(file_list, safe=False)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['get'], url_path='download/(?P<filename>[^/]+)')
    def download_file(self, request, filename):
        print('MEDIA ROOT: ', settings.MEDIA_ROOT)
        print('FILE NAME: ', filename)
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
            if not os.path.exists(file_path):
                return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="{smart_str(filename)}"'
                return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)