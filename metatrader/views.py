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
from rest_framework.views import APIView
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account

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

                        data = {
                            'balance': balance_formatted,
                            'flotante': flotante_formatted,
                            'percentage': float_percent,
                            'balance_percent': balance_percent,
                            'account_id': account_id,
                            'alias': alias,
                        }

                else: 
                    data = {
                            'balance': balance_formatted,
                            'flotante': flotante_formatted,
                            'percentage': float_percent,
                            'balance_percent': 0,
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
            open_operations = Operation.objects.using('postgres').filter(account_id=account_id, dateClose='1970-01-01T00:00:00Z').order_by('-dateOpen')[:10]
            closed_operations = Operation.objects.using('postgres').filter(account_id=account_id).exclude(dateClose='1970-01-01T00:00:00Z').order_by('-dateClose')[:10]

            open_serializer = OperationSerializer(open_operations, many=True)
            closed_serializer = OperationSerializer(closed_operations, many=True)

            latest_detail_balance = DetailBalance.objects.using('postgres').filter(account_id=account_id).order_by('-date', '-time').first()
            day_gain = self.get_day_gain(account_id)

            response_data = {
                'balance': format(latest_detail_balance.balance if latest_detail_balance else None, ',.4f'),
                'flotante': format(latest_detail_balance.flotante if latest_detail_balance else None, ',.4f'),
                'equity': format(latest_detail_balance.equity if latest_detail_balance else None, ',.4f'),
                'gain': format(day_gain, ',.2f'),
                'num_operations': latest_detail_balance.operations if latest_detail_balance else None,
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
        #DESC
        detail_balances = DetailBalance.objects.using('postgres').filter(account_id=account_id).order_by('-date', '-time')
        #Balance actual
        latest_balance = detail_balances
        #Balance inicial 
        first_balance = DetailBalance.objects.using('postgres').filter(
            account_id=account_id, date=latest_balance[0].date).order_by('time')
        
        current_date = datetime.now()+timedelta(hours=2)  
        if latest_balance.exists() and first_balance.exists():
            if latest_balance[0].date == current_date.date(): 
                gain = latest_balance[0].balance - first_balance[0].balance
            else: 
                gain = 0
        return gain 
        
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
            return queryset.order_by('-fecha', '-hora')

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

    def list(self, request, *args, **kwargs):
        user = request.query_params.get('user', None)
        if user:
            user_token = DeviceToken.objects.using('postgres').filter(user=user)
            serializer = self.get_serializer(user_token, many=True)
            return Response(serializer.data)
        else:
            all_tokens = self.queryset
            serializer = self.get_serializer(all_tokens, many=True)
            return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = DeviceTokenSerializer(data=request.data)
        if serializer.is_valid():
            DeviceToken.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'Error': 'Dato no válido'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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

class SentCustomNotifications(APIView):
    def post(self, request, *args, **kwargs):
        notification_data = request.data.get("message").get("notification")
        user = request.data.get("message").get("user")
        user_token = self._get_user_token(user)
        if not user_token:
            print("No se encontró el token de usuario")
            return Response({"error": "Token de usuario no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "message": {
                "notification": {
                    "title": notification_data.get("title"),
                    "body": notification_data.get("body")
                },
                "token": user_token
            }
        }

        url = "https://fcm.googleapis.com/v1/projects/app-trading-notifications/messages:send"
        access_token = self._get_access_token()
        authorization_header = f"Bearer {access_token}"
        print("TOKEN DE AUTORIZACION: ", authorization_header)
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization_header
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            return Response({"message": "Notificacion enviada exitosamente"}, status=status.HTTP_200_OK)
        else:
            print("Error al enviar la notificación a FCM:", response.status_code)
            return Response({"error": "Error al enviar la notificación a FCM"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_access_token(self):  
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-file.json', scopes=['https://www.googleapis.com/auth/cloud-platform'])
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    def _get_user_token(self, user):
        response = self.request_device_token(user)
        if response.status_code == 200:
            data = response.json()  
            return data[0].get("token")
        else:
            print("Error al obtener el token de usuario:", response.status_code)
            return None
    
    def request_device_token(self, user):
        url = f"https://tradinapi.azurewebsites.net/token/?user={user}"
        response = requests.get(url)
        print("Respuesta de solicitud de token de dispositivo:", response.text)
        return response


class SentNotifications(APIView):
    def post(self, request, *args, **kwargs):
        print("Recibida solicitud POST a SentNotifications")
        #Api google FCM
        url = "https://fcm.googleapis.com/v1/projects/app-trading-notifications/messages:send"
        #Obtener tokens almacenados
        tokens_data = requests.get("https://tradinapi.azurewebsites.net/token/").json()
        #Obtener el cuerpo de la notificacion
        notification_data = request.data.get("message").get("notification")

        for token_info in tokens_data:
            token = token_info.get("token")
            data = {
                "message": {
                    "notification": {
                        "title": notification_data.get("title"),
                        "body": notification_data.get("body")
                    },
                    "token": token
                }
            }
            access_token = self._get_access_token()
            authorization_header = f"Bearer {access_token}"
            headers = {
                "Content-Type": "application/json",
                "Authorization": authorization_header
            }
            response = requests.post(url, json=data, headers=headers)
            print("RESPUESTA: ", response.text)
        if response.status_code == 200:
            return Response({"message": "Notificación enviada exitosamente"}, status=status.HTTP_200_OK)
        else:
            print("Error al enviar la notificación a FCM")
            return Response({"error": "Error al enviar la notificación a FCM"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def _get_access_token(self):  
        credentials = service_account.Credentials.from_service_account_file(
            'service-account-file.json', scopes=['https://www.googleapis.com/auth/cloud-platform'])
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token
    

class MonedaApiViewCopy(viewsets.ModelViewSet):
    serializer_class = MonedaSerializer
    queryset = Datatrader1M.objects.using('postgres').all()
    def create(self, request, *args, **kwargs):
        url = "https://fcm.googleapis.com/v1/projects/app-trading-notifications/messages:send"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "ya29.a0Ad52N38ZrT1DLxgmxDmG1qPmsK14IT8qA8VW0g8T1s3SPlk0ldevsTji3IRkFmaFDTaz6naCs3WSr-Gn3BH1i8QwTgZi1sHZoxpaLpUtgtGNvIwrtbsvSFIr3LRLEsxr8ic9Pgpo5hAPZWDinyfXiVu6-ovatxgwTmrwaCgYKAbUSARESFQHGX2MiN3DksjrL4g3SLgEGGIpOHg0171"
        }
        data = {
            "message": {
                "notification": {
                    "title": "Probando desde visual",
                    "body": "Personalizando notificaciones por usuarios"
                },
                "token": "eLFVJsgFTO2EtjlS-nYNPM:APA91bFbtCpqBvrFRaUNSKQjDYf_JNWhncXoT35hznsXH8bRPRQqeUentE4kRLOgZrgsse_ua2FE2A22TUxMuYs2nqlAfUgNFzOlYbb8WBgKpE2TYoGie4HLvCY8oBYjHLC9fawZGm7G"
            }
        }
        data2 = {
            "message": {
                "notification": {
                    "title": "Probando desde visual",
                    "body": "Personalizando notificaciones por usuarios"
                },
                "token": "eU2I7IOeaC9jzZEJcTIgJq:APA91bEbukRQrocatYfS6Thoj6ZewgCSinKKFje_JULFsv8OEIz22Fr0S5F3d8HW8TzibqABsH2rEXG1Tc_mUhsRZTYysJLC1626g8QhDB3OWrwuhBBPh7RBrUtG9wO9RrDmjbtUHXgS"
            }
        }
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
            Datatrader1M(par=tablePar, date=date, time=time, open=open, high=high, low=low, close=close, volume=volume)
            requests.post(url, json=data, headers=headers)
            requests.post(url, json=data2, headers=headers)
            return Response({'Message':'Succesfull!!'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'Message':str(e)}, status=status.HTTP_400_BAD_REQUEST)
    