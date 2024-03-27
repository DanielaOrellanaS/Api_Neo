from rest_framework import serializers
from rest_framework.fields import empty
from metatrader.models import *

class ParesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Pares
        fields = ['id', 'pares']

class MonedaSerializer(serializers.ModelSerializer):
    par = serializers.PrimaryKeyRelatedField(queryset=Pares.objects.using('postgres').all())
    class Meta:
        model = Datatrader1M
        fields = '__all__'

class AccountTypeSerializer(serializers.ModelSerializer):
    #description = serializers.CharField(queryset=AccountType.objects.using('postgres').all())
    class Meta:
        model = AccountType
        fields = ['description'] 

class AccountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    accountType = serializers.PrimaryKeyRelatedField(queryset=AccountType.objects.using('postgres').all())
    class Meta:
        model = Account
        fields = ['id', 'accountType', 'alias', 'group']

class DetailBalanceSerializer(serializers.ModelSerializer):
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.using('postgres').all())
    class Meta:
        model = DetailBalance
        fields = '__all__'

class OperationSerializer(serializers.ModelSerializer):
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.using('postgres').all())
    class Meta: 
        model = Operation
        fields = '__all__'

class IndicadorSerializer(serializers.ModelSerializer):
    par = serializers.PrimaryKeyRelatedField(queryset=Pares.objects.using('postgres').all())
    class Meta:
        model = ResumeIndicador
        fields = '__all__'
        
class UserFavAccountsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    
    class Meta:
        model = UserFavAccounts
        fields = '__all__'
        
class EventsSerializer(serializers.ModelSerializer):
    orden = serializers.IntegerField()
    class Meta: 
        model = Events
        fields = '__all__'

class ParMonedaSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField()
    class Meta: 
        model = ParMoneda
        fields = '__all__'

class PipsSerializer(serializers.ModelSerializer): 
    orden = serializers.IntegerField()
    class Meta: 
        model = Pips
        fields = '__all__'

class RangosSerializer(serializers.ModelSerializer):
    par = serializers.PrimaryKeyRelatedField(queryset=Pares.objects.using('postgres').all())
    class Meta:
        model = CortesIndicador
        fields = '__all__'

class AlertEventsSerializer(serializers.ModelSerializer):
    par = serializers.PrimaryKeyRelatedField(queryset=Pares.objects.using('postgres').all())
    class Meta:
        model = AlertEvents
        fields = '__all__' 

class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = '__all__'


class VariacionPipsSerializer(serializers.ModelSerializer):
    par = serializers.PrimaryKeyRelatedField(queryset=Pares.objects.using('postgres').all())
    class Meta:
        model = variacion_pips_estimacion
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Notification
        fields = '__all__'