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
        fields = ['id', 'accountType', 'alias']

class DetailBalanceSerializer(serializers.ModelSerializer):
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.using('postgres').all())
    class Meta:
        model = DetailBalance
        fields = '__all__'