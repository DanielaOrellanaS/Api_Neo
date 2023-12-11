from django.shortcuts import render
from rest_framework.views import APIView
from django.db.models import Count, Max, Min, F, Subquery
from datetime import datetime, timedelta
from rest_framework import status, viewsets
from metatrader.models import *
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
from metatrader.serializers import *
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.urls import reverse
from rest_framework import generics
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

#-----------------------------------------------------------------------------------------

class AllAccountsDetailsApiView(viewsets.ViewSet):
    serializer_class = DetailBalanceSerializer
    queryset = DetailBalance.objects.using('postgres').all()

    def list(self, request, *args, **kwargs):
        try:
            accounts_info = Account.objects.using('postgres').values('id', 'accountType', 'alias')
            
            latest_balances = DetailBalance.objects.using('postgres') \
                .filter(account_id__in=[acc['id'] for acc in accounts_info]) \
                .values('account_id') \
                .annotate(latest_id=Max('id'))
                
            additional_info = DetailBalance.objects.using('postgres') \
                .filter(id__in=Subquery(latest_balances.values('latest_id'))) \
                .values('id', 'account_id', 'balance', 'flotante', 'equity', 'operations')

            account_data_dict = {info['account_id']: info for info in additional_info}

            operations_by_symbol = Operation.objects.using('postgres') \
                .filter(account_id__in=[acc['id'] for acc in accounts_info]) \
                .exclude(dateClose='1970-01-01 00:00') \
                .values('account_id', 'symbol') \
                .annotate(open_operations=Count('id'))

            # Operaciones abiertas
            open_operations = list(
                Operation.objects.using('postgres')
                .filter(account_id__in=[acc['id'] for acc in accounts_info], dateClose='1970-01-01 00:00')
                .values('account_id', 'symbol', 'type', 'lotes', 'dateOpen', 'dateClose', 'openPrice', 'closePrice', 'profit', 'tp', 'sl')
            )

            # Operaciones cerradas
            closed_operations = list(
                Operation.objects.using('postgres')
                .filter(account_id__in=[acc['id'] for acc in accounts_info])
                .exclude(dateClose='1970-01-01 00:00')
                .order_by('-dateClose')[:10]
                .values('account_id', 'symbol', 'type', 'lotes', 'dateOpen', 'dateClose', 'openPrice', 'closePrice', 'profit', 'tp', 'sl')
            )
            
            all_accounts_data = []
            for acc_info in accounts_info:
                account_id = acc_info['id']
                latest_detail_balance = account_data_dict.get(account_id)

                if latest_detail_balance:
                    account_data = {
                        'id': account_id,
                        'alias': acc_info['alias'],
                        'accountType': acc_info['accountType'],
                        'balance': latest_detail_balance['balance'],
                        'flotante': latest_detail_balance['flotante'],
                        'equity': latest_detail_balance['equity'],
                        'percentage': round((latest_detail_balance['flotante'] / latest_detail_balance['balance']) * 100, 2) if latest_detail_balance['balance'] != 0 else 0,
                        'gain': self.get_day_gain(account_id),
                        'num_operations': latest_detail_balance['operations'],
                        'operations_by_symbol': next((ops['open_operations'] for ops in operations_by_symbol if ops['account_id'] == account_id), []),
                        'open_operations': [ops for ops in open_operations if ops['account_id'] == account_id],
                        'closed_operations': [ops for ops in closed_operations if ops['account_id'] == account_id],
                    }
                    all_accounts_data.append(account_data)
                else:
                    all_accounts_data.append({'Error': f'No existen datos para la cuenta {account_id}'})
            
            return Response(all_accounts_data, status=status.HTTP_200_OK)
                
        except Account.DoesNotExist:
            return Response({'Error': 'No existen cuentas'}, status=status.HTTP_400_BAD_REQUEST)
        
    def get_equity(self, account_id):
        try:
            detail_balance_instance = DetailBalance.objects.using('postgres') \
                .filter(account_id=account_id) \
                .latest('id')
            return {
                'equity': detail_balance_instance.equity,
            }
        except DetailBalance.DoesNotExist:
            return None

    def get_day_gain(self, account_id):
        try:
            current_date = datetime.now().date()
            
            current_balance = DetailBalance.objects.using('postgres') \
                .filter(account_id=account_id, date__lte=current_date) \
                .order_by('-date', '-time') \
                .first()

            previous_date = current_date - timedelta(days=1)
            previous_closing_balance = DetailBalance.objects.using('postgres') \
                .filter(account_id=account_id, date=previous_date) \
                .order_by('-date', '-time') \
                .values('balance') \
                .first()

            if current_balance and previous_closing_balance:
                difference = current_balance.balance - previous_closing_balance['balance']
                return difference
                
        except DetailBalance.DoesNotExist:
            pass

        return None
    
    def get_operations_count(self, account_id):
        try:
            operations_count = DetailBalance.objects.using('postgres') \
                .filter(account_id=account_id) \
                .values_list('operations', flat=True) \
                .latest('id')
            return operations_count
                
        except DetailBalance.DoesNotExist:
            return None
        
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


    def get_open_operations(self, account_id):
        try:
            latest_operations = (
                Operation.objects.using('postgres')
                .filter(account_id=account_id, dateClose='1970-01-01 00:00')
                .values('symbol', 'type', 'lotes', 'dateOpen', 'dateClose', 'openPrice', 'closePrice', 'profit', 'tp', 'sl')
            )
            return latest_operations
        except Operation.DoesNotExist:
            return None
    
    def get_closed_operations(self, account_id):
        try:
            closed_operations = (
                Operation.objects.using('postgres')
                .filter(account_id=account_id)
                .exclude(dateClose='1970-01-01 00:00')
                .order_by('-dateClose')[:10]
                .values('symbol', 'type', 'lotes', 'dateOpen', 'dateClose', 'openPrice', 'closePrice', 'profit', 'tp', 'sl')
            )
            return closed_operations
        except Operation.DoesNotExist:
            return None
        

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
            operationType = data.get('type')
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
        

class LastIndicatorApiView(viewsets.ModelViewSet):
    serializer_class = IndicadorSerializer
    def get_queryset(self):
        last_indicators = (
            ResumeIndicador.objects.using('postgres')
            .values('par_id')
            .annotate(last_id=Max('id'))
            .values('last_id')
        )

        indicators_data = (
            ResumeIndicador.objects.using('postgres')
            .filter(id__in=last_indicators)
        )

        return indicators_data

class UserFavAccountsApiView(viewsets.ModelViewSet):
    serializer_class = UserFavAccountsSerializer
    queryset = UserFavAccount.objects.using('postgres').all()

    def create(self, request, *args, **kwargs):
        serializer = UserFavAccountsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            UserFavAccount.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'Error':'Dato no valido'}, status=status.HTTP_400_BAD_REQUEST)

class EventsApiView(viewsets.ModelViewSet):
    serializer_class = EventsSerializer
    queryset = Events.objects.using('postgres').all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        fechas = self.request.query_params.getlist('fecha', None)
        if fechas:
            parsed_dates = [parse_date(fecha) for fecha in fechas if parse_date(fecha)]
            if parsed_dates:
                queryset = queryset.filter(fecha__in=parsed_dates)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = EventsSerializer(data=request.data)
        if(serializer.is_valid()):
            Events.objects.using('postgres').create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else: 
            return Response({'Error':'Dato no valido'}, status=status.HTTP_400_BAD_REQUEST)

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